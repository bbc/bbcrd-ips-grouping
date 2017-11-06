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

from ipsgrouping.test import BaseTestCase
from nmoscommon.utils import getLocalIP
from ipsgrouping.constants import DEFAULT_API_VERSION
from ipsgrouping.config import PORT
import requests


class IntegrationBase(BaseTestCase):
    _multiprocess_shared_ = True

    maxDiff = None

    def setUp(self):
        super(IntegrationBase, self).setUpContext()

    @classmethod
    def setUpClass(cls):
        local_ip = getLocalIP()
        version = getattr(cls, 'api_version', DEFAULT_API_VERSION)
        cls._aggr_host = "http://{}:{}/x-ipstudio/grouping/v{}".format(local_ip, PORT, version)

    def tearDown(self):
        # Ensure that each test cleans up completely, leaving the registry clear.
        # This happens after every test.
        # Note: we mess with etcd manually here, for brevity.
        requests.delete("http://127.0.0.1:4001/v2/keys/resource?recursive=true", proxies={'http': ''})
        requests.delete("http://127.0.0.1:4001/v2/keys/health?recursive=true", proxies={'http': ''})
        super(IntegrationBase, self).tearDownContext()

    def assert_uuid(self, text):
        self.assertRegexpMatches(
            text,
            "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )


"""
    mark all integration tests as slow
    you can run all test excluding integration tests by running
    `nosetests -a '!slow'`
"""
IntegrationBase.slow = 1
