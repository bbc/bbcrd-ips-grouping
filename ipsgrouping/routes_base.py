# Copyright 2017 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import make_response, Response
from jsonschema import validate, ValidationError
from collections import defaultdict
from nmoscommon.webapi import request, jsonify, abort
from ipsgrouping.database import db_mongo, ChildNotFound
from ipsgrouping.constants import INTERNAL_USE_KEY_PREFIX, API_VERSION_KEY, DEFAULT_API_VERSION, V2_0
from functools import wraps

import re


class Marshal(object):
    def __init__(self, excluder=lambda keys: []):
        # excluder :: iter -> iter (returns the keys to remove)
        self.excluder = excluder

    def __call__(self, func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            rv = func(*args, **kwargs)
            if isinstance(rv, tuple):
                resp = self.marshal_ipstudio_resp_args(rv)
            else:
                if isinstance(rv, Response):
                    args[0].logger.writeInfo("Marshal ignoring Response object")
                resp = rv
            return resp
        return decorated_func

    def marshal_ipstudio_resp_args(self, rv):
        data = rv[1]
        return rv[:1] + (self.marshal(data), ) + rv[2:]

    def marshal(self, data):
        if isinstance(data, list):
            modified = [self.marshal(resource) for resource in data]

        elif isinstance(data, dict):
            modified = data.copy()
            for key in self.excluder(modified.keys()):
                modified.pop(key, None)
        else:
            return data
        return modified

marshal = Marshal(
    excluder=lambda keys: (key for key in keys if INTERNAL_USE_KEY_PREFIX in key)
)
group_collection = db_mongo.group_collection
package_collection = db_mongo.package_collection


def validate_uuid(text):
    uuid_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "string",
        "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    }
    validate(text, uuid_schema)


def validator(validation_func, obj):
    try:
        validation_func(obj)
    except ValidationError as e:
        abort(400, e.message)
    return obj


def translate_version(mapping, item):
    copy = item.copy()
    for old_key, new_key in mapping.items():
        old_value = copy.pop(old_key, None)
        if old_value is not None and new_key is not None:
            copy[new_key] = old_value
    return copy


class TranslationException(Exception):
    pass


def _translate_to(logger, version, item):
    item_version = item.get(API_VERSION_KEY, DEFAULT_API_VERSION)
    logger.writeInfo('translating {} from {} to {}'.format(API_VERSION_KEY, item_version, version))

    if item_version == version:
        return item
    else:
        raise TranslationException('Translation not regonised for {} to {}'.format(item_version, version))


def parse_tags_query(args):
    tags_query = {}
    for key in args.keys():
        tag_name = re.match(r'^tags\.(.+)', key)
        if tag_name:
            if tag_name.group(0) not in tags_query:
                tags_query[tag_name.group(0)] = []
            tags_query[tag_name.group(0)].append(args.pop(key, None))
    return tags_query


class RouteBase(object):

    def insert_package(self, *args):
        return self._insert_package(self.api_version, *args)

    def insert_group(self, *args):
        return self._insert_group(self.api_version, *args)

    def translate_to(self, version, item):
        return _translate_to(self.logger, version, item)

    @staticmethod
    def _insert_package(version, req_json):
        resp = req_json.copy()
        req_json[API_VERSION_KEY] = version

        try:
            resource_id = db_mongo.insert_package(req_json)
        except ChildNotFound as e:
            abort(400, e.message)

        resp["id"] = resource_id
        resp = marshal.marshal(resp)  # TODO: could be safer to wrap make_response to marshal
        response = make_response(jsonify(resp), 201)
        response.autocorrect_location_header = False
        response.headers['Location'] = '{}/{}/'.format(request.path, resource_id)
        return response

    @staticmethod
    def _insert_group(version, req_json):
        resp = req_json.copy()
        req_json[API_VERSION_KEY] = version

        resource_id = group_collection.insert(req_json)
        resp["id"] = resource_id

        resp = marshal.marshal(resp)  # TODO: could be safer to wrap make_response to marshal
        response = make_response(jsonify(resp), 201)
        response.autocorrect_location_header = False
        response.headers['Location'] = '{}/{}/'.format(request.path, resource_id)
        return response

    @staticmethod
    def get_request_json_or_abort():
        ret = request.get_json()
        if ret is None:
            abort(400, "Only accepts context-type: application/json")
        return ret
