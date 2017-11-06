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

from ipsgrouping.database import MongoCollection
from unittest import TestCase

MOCK_DOCK = {"foo": "bar"}


class MockDB(object):
    def insert(self, x):
        return x


class TestMongoCollection(TestCase):

    def test_insert_with_no_id(self):

        collection = MongoCollection()
        collection.collection = MockDB()

        resp = collection.insert(MOCK_DOCK)
        self.assertEqual(set(resp.keys()), set(MOCK_DOCK.keys() + ['_id']))
        resp.pop('_id')
        self.assertEqual(MOCK_DOCK, resp)

    def test_insert_with_id(self):
        collection = MongoCollection()
        collection.collection = MockDB()

        doc = dict([['id', 1234]] + MOCK_DOCK.items())
        resp = collection.insert(doc)
        self.assertEqual(len(resp.keys()), len(doc.keys()))
        self.assertEqual(resp['_id'], 1234)
