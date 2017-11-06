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
import json
from flask import Flask
from ipsgrouping.database import db_mongo
from ipsgrouping.config import CONFIG_PATH


class BaseTestCase(unittest.TestCase):

    def _setup_db(self, config):
        self.app = Flask(__name__)
        self.app.config.update(config)
        db_mongo.init_app(self.app)
        self._tear_down_db()   # ensure there isn't data present

    def _tear_down_db(self):
        with self.app.app_context():
            db_mongo.db.command("dropDatabase")

    def _get_config(self):
        with open(CONFIG_PATH) as json_config:
            config = json.load(json_config)
            if not config.get("TEST"):
                raise Exception("TEST config not set to true")
        return config

    def setUpContext(self):
        # TODO: only check config and create engine once
        config = self._get_config()
        self._setup_db(config)

    def tearDownContext(self):
        self._tear_down_db()
