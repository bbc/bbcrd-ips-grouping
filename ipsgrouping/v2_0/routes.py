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

from nmoscommon.timestamp import Timestamp
from werkzeug.exceptions import HTTPException
from nmoscommon.webapi import secure_route, request, abort
from nmoscommon.utils import getLocalIP
from ipsgrouping.database import db_mongo, Query, TagQuery, ApiVersionQuery, RQLQuery
from ipsgrouping.config import v2_0 as CONFIG
from .validation import validate_group, validate_package
from ipsgrouping.routes_base import RouteBase, validate_uuid, validator, parse_tags_query, marshal
from ipsgrouping.constants import API_VERSION_KEY, V2_0, V2_0_TS_KEYS


group_collection = db_mongo.group_collection
package_collection = db_mongo.package_collection

HOST = getLocalIP()

ACCEPTED_QUERY_PARAMS_GROUPS = CONFIG["ACCEPTED_QUERY_PARAMS_GROUPS"]
ACCEPTED_QUERY_PARAMS_PACKAGES = CONFIG["ACCEPTED_QUERY_PARAMS_PACKAGES"]


def parse_resp_timestamps(resp):
    return {
        k:
        Timestamp.from_str(v).to_sec_nsec() if k in V2_0_TS_KEYS
        else v
        for k, v in resp.iteritems()
    }


class Routes(RouteBase):

    api_version = V2_0

    def __init__(self, logger, oauth_config, app):
        self.logger = logger
        self._oauth_config = oauth_config
        self.app = app

    @secure_route('/')
    def versionroot(self):
        return ["groups/", "packages/"]

    @secure_route('/doc/')
    def docs(self):
        return self.app.send_static_file("GroupingAPI-v2.0.html")

    @secure_route('/groups/', methods=["GET"], auto_json=False)
    @marshal
    def groups_get(self):
        if request.method == 'GET':
            args = request.args.to_dict()
            q = ApiVersionQuery([V2_0, None])  # ignore items predating v2.0

            tags_query = parse_tags_query(args)
            if len(tags_query) > 0:
                q += TagQuery(tags_query)

            rql = args.pop('query.rql', None)
            if rql:
                q += RQLQuery(rql)

            args = {k: v for k, v in args.items() if k in ACCEPTED_QUERY_PARAMS_GROUPS}
            response = (200, group_collection.find_all(q + Query(args)))

        return response

    @secure_route('/groups', methods=["POST"], auto_json=False)
    @marshal
    def groups_write(self):
        if request.method == 'POST':
            req_json = self.get_request_json_or_abort()
            validator(validate_group, req_json)
            response = self.insert_group(req_json)

        return response

    @secure_route('/groups/<group_id>/', methods=["HEAD", "GET"])
    @marshal
    def group_get(self, group_id):

        validator(validate_uuid, group_id)

        if request.method == "GET":
            group = group_collection.get_or_404(group_id)
            if group.get(API_VERSION_KEY, 0) < self.api_version:
                abort(404)
            resp = (200, group)

        return resp

    @secure_route('/groups/<group_id>', methods=["PUT", "PATCH", "DELETE"])
    @marshal
    def group_writer(self, group_id):

        validator(validate_uuid, group_id)

        if request.method == "PUT":
            req_json = self.get_request_json_or_abort()
            if 'id' in req_json:
                if req_json['id'] != group_id:
                    abort(400, "Payload 'id' must match that in the URL: got {}, expected {}".format(req_json['id'], group_id))
                req_json.pop('id')

            validator(validate_group, req_json)

            updated_group = group_collection.update_or_404(group_id, req_json)
            resp = (200, updated_group)

        if request.method == "DELETE":
            db_mongo.remove_group_or_404(group_id)
            resp = (204, '')

        return resp

    @secure_route('/packages/', methods=["GET"], auto_json=False)
    @marshal
    def packages_get(self):

        if request.method == 'GET':
            args = request.args.to_dict()
            q = ApiVersionQuery([V2_0, None])  # ignore items predating v2.0

            tags_query = parse_tags_query(args)
            if len(tags_query) > 0:
                q += TagQuery(tags_query)

            rql = args.pop('query.rql', None)
            if rql:
                q += RQLQuery(rql)

            args = {k: v for k, v in args.items() if k in ACCEPTED_QUERY_PARAMS_PACKAGES}

            resp = package_collection.find_all(q + Query(args))
            response = (200, resp)

        return response

    @secure_route('/packages', methods=["POST"], auto_json=False)
    @marshal
    def packages_write(self):

        if request.method == 'POST':
            req_json = self.get_request_json_or_abort()
            package = parse_resp_timestamps(req_json)
            validator(validate_package, package)
            response = self.insert_package(package)

        return response

    @secure_route('/packages/<package_id>/', methods=["HEAD", "GET"])
    @marshal
    def package_get(self, package_id):

        validator(validate_uuid, package_id)

        if request.method == "GET":
            resp = (200, package_collection.get_or_404(package_id))

        return resp

    @secure_route('/packages/<package_id>', methods=["PUT", "PATCH", "DELETE"])
    @marshal
    def package_writer(self, package_id):

        validator(validate_uuid, package_id)

        if request.method == "PUT":
            req_json = self.get_request_json_or_abort()
            if 'id' in req_json:
                if req_json['id'] != package_id:
                    abort(400, "Payload 'id' must match that in the URL: got {}, expected {}".format(req_json['id'], package_id))
                req_json.pop('id')

            package = parse_resp_timestamps(req_json)
            validator(validate_package, package)

            updated_package = package_collection.update_or_404(package_id, package)
            resp = (200, updated_package)

        if request.method == "DELETE":
            package_collection.remove_or_404(package_id)
            resp = (204, '')

        return resp
