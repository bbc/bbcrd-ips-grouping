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

from ipsgrouping.database import Query, TagQuery
import unittest


class TestQuery(unittest.TestCase):

    def test_queries_can_be_merged(self):
        a = Query({"foo": "bar", "1": "2"})
        b = Query({"foo": "foo", "hello": "bye"})

        z = a.merge(b)
        self.assertEqual(z, {"foo": "foo", "1": "2", "hello": "bye"})

    def test_queries_can_be_merged_using_plus_operator(self):
        a = Query({"foo": "bar", "1": "2"})
        b = Query({"foo": "foo", "hello": "bye"})

        z = a + b
        self.assertEqual(z, {"foo": "foo", "1": "2", "hello": "bye"})


class TestTagQuery(unittest.TestCase):

    def test_forms_a_mongo_query_from_tag_syntax(self):
        t = TagQuery({"tags.foo": [], "tags.bar": ["foo"], "tags.hello": ["foo", "bar"]})

        self.assertEqual(t, {
            "tags.foo": {"$exists": True},
            "tags.bar": {"$all": ["foo"]},
            "tags.hello": {"$all": ["foo", "bar"]}
        })
