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

_default_config = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'test_config/config.json')

CONFIG_PATH = os.getenv("IPSGROUPING_CONFIG", _default_config)
PORT = 12370

v2_0 = {
    "ACCEPTED_QUERY_PARAMS_GROUPS": ['resource_type', 'label', 'description'],
    "ACCEPTED_QUERY_PARAMS_PACKAGES": ['label', 'description', 'group_id', 'max_ts', 'min_ts']
}
