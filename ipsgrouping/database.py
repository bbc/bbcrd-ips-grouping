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

from pymongo import MongoClient
import uuid
from nmoscommon.webapi import abort
from nmoscommon.rql import convert_to_mongo, ParserError
from nmoscommon.rql.query.mongodb import UnparseError
from ipsgrouping.constants import API_VERSION_KEY


class Nothing(object):
    def __call__(self, *args, **kwargs):
        pass

    def __getattribute__(self, *args, **kwargs):
        return Nothing()


def marshall(item):
    item["id"] = str(item.pop("_id"))
    return item


class ChildNotFound(Exception):
    pass


class Query(dict):

    def __add__(self, other):
        return self.merge(other)

    def merge(self, other):
        z = self.copy()
        z.update(other)
        return Query(z)


class TagQuery(Query):

    def __init__(self, tags):
        raw_query = {
            key:
            {"$all": values} if values else {"$exists": True}
            for key, values in tags.items()
        }
        super(TagQuery, self).__init__(raw_query)


class RQLQuery(Query):

    def __init__(self, rql_str):
        try:
            q = convert_to_mongo(rql_str)
        except UnparseError:
            abort(501)
        except ParserError as e:
            abort(400, e.message)
        super(RQLQuery, self).__init__(q)


class ApiVersionQuery(Query):
    def __init__(self, bounds):
        raw_query = {
            API_VERSION_KEY:
            {"$gte": bounds[0]} if isinstance(bounds, list) else {"$eq": bounds}
        }
        super(ApiVersionQuery, self).__init__(raw_query)


class MongoCollection(object):

    def register(self, db, collection, logger=Nothing()):
        self.collection = db[collection]
        self.logger = logger
        # self.collection.createIndex({"tags": 1})  # TODO: explore indexes

    def count(self):
        return self.collection.count()

    def insert(self, doc):
        doc = doc.copy()
        doc["_id"] = doc.pop("id", unicode(uuid.uuid4()))
        return self.collection.insert(doc)

    def get(self, resource_id):
        self.logger.writeInfo('find {}'.format(resource_id))
        return self.collection.find_one({"_id": resource_id})

    def get_or_404(self, resource_id):
        return self._or_404(self.get, resource_id)

    def find(self, query, projection=None):
        self.logger.writeInfo('find with query: {}\nprojection:{}'.format(query, projection))
        return self.collection.find(query, projection)

    def find_and_modify(self, *args, **kwargs):
        return self.collection.find_and_modify(*args, **kwargs)

    def find_all(self, query, projection=None):
        return [marshall(r) for r in self.find(query, projection)]

    def update(self, resource_id, doc):
        query = {"_id": resource_id}
        update_cmd = {"$set": doc}
        return self.collection.find_and_modify(query, update_cmd, new=True)

    def update_or_404(self, resource_id, doc):
        return self._or_404(self.update, resource_id, doc)

    def remove(self, resource_id):
        """ removes item from collection. returns removed item in full. returns None if none found"""
        return self.collection.find_and_modify({"_id": resource_id}, remove=True)

    def remove_or_404(self, resource_id):
        return self._or_404(self.remove, resource_id)

    def _or_404(self, func, *args, **kwargs):
        item = func(*args, **kwargs)
        return marshall(item) if item else abort(404)


class GroupMixin(object):

    def _remove_group_orphans(self, group_id):
        return self.package_collection.find_and_modify({"group_id": group_id}, remove=True)

    def remove_group_or_404(self, group_id):
        self.group_collection.remove_or_404(group_id)
        self._remove_group_orphans(group_id)


class PackageMixin(object):

    def insert_package(self, doc):
        if self.group_collection.find({"_id": doc["group_id"]}):
            return self.package_collection.insert(doc)
        else:
            raise ChildNotFound("Cannot save package as group_id refers to \
                                    a Group that does not exist")


class FlaskDatabase(GroupMixin, PackageMixin):

    def __init__(self):
        self.package_collection = MongoCollection()
        self.group_collection = MongoCollection()

    def __repr__(self):
        return "Groups: {}\nPackages: {}".format(
            self.group_collection.count(), self.package_collection.count()
        )

    def init_app(self, app, db_name='ipsgrouping', logger=Nothing()):
        self.logger = logger

        _db_uri = app.config["MONGO_DATABASE_URI"]
        _db_name = _db_uri.split("/")[-1].split("?")[0]

        _mongoclient = MongoClient(_db_uri)
        self.db = _db = _mongoclient[_db_name]

        self.package_collection.register(_db, 'packages', logger)
        self.group_collection.register(_db, 'groups', logger)


db_mongo = FlaskDatabase()
