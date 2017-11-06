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

import unittest
from ipsgrouping.test.fixtures.factories import group_factory_v2_0
from ipsgrouping.test.fixtures.factories import package_factory_v2_0
from jsonschema import ValidationError
from ipsgrouping.v2_0.validation import validate_group, validate_package


class TestValidation(unittest.TestCase):

    def test_group_validation_success(self):
        validate_group(group_factory_v2_0())

    def test_group_validation_fail(self):
        self.assertRaises(ValidationError, validate_group, 1234)

    def test_package_validation_success(self):
        validate_package(package_factory_v2_0())

    def test_package_validation_fail(self):
        self.assertRaises(ValidationError, validate_package, 1234)
