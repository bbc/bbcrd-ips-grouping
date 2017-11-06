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

import gevent
from gevent import monkey
monkey.patch_all()

import signal
import json
import os

from nmoscommon.httpserver import HttpServer
from nmoscommon.logger import Logger
from nmoscommon.facade import Facade
from ipsgrouping.database import db_mongo
from ipsgrouping.api import GroupingAPI, APINAME, APIVERSIONS, APINAMESPACE
from ipsgrouping.config import CONFIG_PATH, PORT


class GroupingService:
    def __init__(self, interactive=False):
        self.facades = {}
        for version in APIVERSIONS:
            self.facades[version] = Facade("{}/{}".format(APINAME, version))
        self.logger = Logger("grouping", None)
        self.running = False
        self.httpServer = None
        with open(CONFIG_PATH) as config_fp:
            self.config = json.load(config_fp)

    def _sig_handler(self):
        self.logger.writeInfo("Stopping...")
        self._stop()

    def _start(self):
        gevent.signal(signal.SIGINT,  self._sig_handler)
        gevent.signal(signal.SIGTERM, self._sig_handler)

        self.httpServer = HttpServer(GroupingAPI, PORT, '0.0.0.0', ssl=self.config.get("ssl"))
        self.httpServer.start()
        while not self.httpServer.started.is_set():
            self.logger.writeInfo('Waiting for httpserver to start...')
            self.httpServer.started.wait()

        if self.httpServer.failed is not None:
            raise self.httpServer.failed

        self.httpServer.api.app.config.update(self.config)
        db_mongo.init_app(self.httpServer.api.app, logger=self.logger)
        self.logger.writeInfo("Running on port: {}".format(self.httpServer.port))

    def run(self):
        self.running = True
        self._start()
        for version in APIVERSIONS:
            self.facades[version].register_service("http://127.0.0.1:" + str(PORT), "{}/{}/{}/".format(APINAMESPACE, APINAME, version))
        itercount = 0
        while self.running:
            if itercount % 5 == 0:
                for facade in self.facades:
                    self.facades[facade].heartbeat_service()
            gevent.sleep(1)
            itercount += 1
            if itercount == 10:
                itercount = 0
        for facade in self.facades:
            self.facades[facade].unregister_service()
        self._cleanup()

    def _cleanup(self):
        self.httpServer.stop()
        self.logger.writeInfo("Stopped")

    def _stop(self):
        self.running = False
