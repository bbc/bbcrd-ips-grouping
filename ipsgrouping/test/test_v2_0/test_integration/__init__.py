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

from ipsgrouping.test.fixtures.factories import group_factory_v2_0, package_factory_v2_0
from ipsgrouping.test.integration import IntegrationBase
from ipsgrouping.database import db_mongo
from ipsgrouping.constants import API_VERSION_KEY


group_collection = db_mongo.group_collection
package_collection = db_mongo.package_collection


class IntegationWithMockData(IntegrationBase):

    def _create_tags(self, collection, ids):
        """ add some tags to each of the test """
        resources = collection.find_all({"_id": {"$in": ids}})
        for r in resources:
            r["tags"] = {"label": [r["label"]], "foo": ["bar"]}
            r_id = r.pop("id")
            collection.update(r_id, r)

    def create_tags(self):
        for collection in ((group_collection, self.group_ids), (package_collection, self.package_ids)):
            self._create_tags(*collection)

    def _create_groups(self):
        self.group_labels = ["group_1", "group_2", "group_3"]
        self.group_types = ["flow", "source", "group"]
        self.group_representations = [
            group_factory_v2_0(label=n, resource_type=t, **{API_VERSION_KEY: self.api_version}) for n, t in zip(self.group_labels, self.group_types)
        ]

        self.group_ids = [group_collection.insert(doc) for doc in self.group_representations]

    def _create_packages(self, group_ids):
        self.package_labels = ["package_1", "package_2", "package_3"]
        packages = [package_factory_v2_0(label=n, group_id=gid, **{API_VERSION_KEY: self.api_version}) for n, gid in zip(self.package_labels, group_ids)]

        self.package_ids = [package_collection.insert(doc) for doc in packages]
        self.packages_marshalled = package_collection.find_all({"_id": {"$in": self.package_ids}})

    def setUp(self):
        # create the db tables
        super(IntegationWithMockData, self).setUpContext()
        self._create_groups()
        self._create_packages(self.group_ids)
        self.create_tags()

        # an id not used in the db
        self.unused_id = '9946b65e-6804-4dc8-a09e-f4890bcdafaa'
