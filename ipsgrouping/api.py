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

import json
from flask.helpers import get_root_path
from nmoscommon.webapi import WebAPI, secure_route
from nmoscommon.logger import Logger

import ipsgrouping.selfcheck as selfcheck
from ipsgrouping.config import CONFIG_PATH
from ipsgrouping.v2_0 import routes as v2_0

APINAMESPACE = "x-ipstudio"
APINAME = "grouping"
APIVERSIONS = ["v2.0"]
APIBASE = "/{}/{}/{}/".format(APINAMESPACE, APINAME, APIVERSIONS)


class GroupingAPI(WebAPI):
    def __init__(self):
        self.logger = Logger("grouping")
        self.config = {}
        try:
            with open(CONFIG_PATH, 'rt') as config_fp:
                self.config = json.load(config_fp)
        except Exception as e:
            self.logger.writeInfo("Did not read config file: {}".format(e))

        super(GroupingAPI, self).__init__(oauth_config=self.config.get('oauth'))

        self.api_v2_0 = v2_0.Routes(self.logger, self.config.get('oauth'), self.app)

        self.add_routes(self.api_v2_0, basepath="/{}/{}/v2.0".format(APINAMESPACE, APINAME))

        self.app.root_path = get_root_path("ipsgrouping")

    @secure_route('/')
    def root(self):
        return [APINAMESPACE + "/"]

    @secure_route('/' + APINAMESPACE + '/')
    def namespaceroot(self):
        return [APINAME + "/"]

    @secure_route('/' + APINAMESPACE + '/' + APINAME + "/")
    def nameroot(self):
        return [v + "/" for v in APIVERSIONS]

    @secure_route(APIBASE + 'selfcheck/', methods=['GET'])
    def selfcheck(self):
        """
        Return diagnostics as JSON, and an overall code:
            200 if "all ok".
            400 otherwise.
        """
        result = selfcheck.check(self._sfq)
        code = 200
        if not result.get('passed'):
            code = 400
        return (code, result)
