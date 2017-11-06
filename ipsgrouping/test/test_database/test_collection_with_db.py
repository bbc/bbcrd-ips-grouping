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

from werkzeug.exceptions import NotFound
from pymongo.errors import DuplicateKeyError
from ipsgrouping.test import BaseTestCase
from ipsgrouping.database import db_mongo


class TestCollectionWithDatabase(BaseTestCase):

    slow = 1

    def setUp(self):
        super(TestCollectionWithDatabase, self).setUpContext()

    def test_update_or_404_throws(self):
        with self.assertRaises(NotFound):
            db_mongo.package_collection.update_or_404('1234', {'1': 2})

    def test_multiple_inserts_fail(self):
        with self.assertRaises(DuplicateKeyError):
            db_mongo.package_collection.insert({'id': '1234', 'group_id': 123})
            db_mongo.package_collection.insert({'id': '1234', 'group_id': 123})

    def test_update_or_404(self):
        db_mongo.package_collection.insert({'id': '1234', 'group_id': 123})

        item = db_mongo.package_collection.update_or_404('1234', {'group_id': 123})
        self.assertEqual(item, {'id': '1234', 'group_id': 123})

        item = db_mongo.package_collection.update_or_404('1234', {'group_id': 123})
        self.assertEqual(item, {'id': '1234', 'group_id': 123})
