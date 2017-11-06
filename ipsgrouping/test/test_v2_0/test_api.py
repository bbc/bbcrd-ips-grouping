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

from ipsgrouping.v2_0.routes import parse_tags_query
import unittest


class TestApiHelpers(unittest.TestCase):

    def test_parse_tags_query_single_pair(self):
        test = {"tags.key": "value"}
        resp = parse_tags_query(test)
        self.assertEqual(resp, {"tags.key": ["value"]})

    def test_parse_tags_query_multi(self):
        test = {"tags.key": "value", "tags.bar": "foo", "tags.dog": "bob"}
        resp = parse_tags_query(test)
        self.assertEqual(resp, {"tags.key": ["value"],
                                "tags.bar": ["foo"],
                                "tags.dog": ["bob"]})
