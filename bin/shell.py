#!/usr/bin/env python
#
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

import os
import readline      # noqa
from pprint import pprint     # noqa

from flask import *     # noqa
from ipsgrouping import service


from ipsgrouping.database import db_mongo, Query, TagQuery     # noqa

groups = db_mongo.group_collection
packages = db_mongo.package_collection

s = service.GroupingService()
s._start()
s.httpServer.api.app.app_context().push()

os.environ['PYTHONINSPECT'] = 'True'
