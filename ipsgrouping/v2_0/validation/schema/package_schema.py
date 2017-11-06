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

from .tag_schema import tag_schema

_tai_s_ns_regex = "^\d+:\d+"

package_schema = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "description": "Register a new Package or update an existing resource",
  "title": "Package registration",
  "required": [
    "label",
    "description",
    "group_id",
    "min_ts",
    "tags"
  ],
  "properties": {
    "group_id": {
        "description": "Globally unique identifier for packaged Group",
        "type": "string",
        "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    },
    "label": {
        "description": "Freeform string label for the Package",
        "type": "string"
    },
    "description": {
        "description": "Freeform string description for the Package",
        "type": "string"
    },
    "min_ts": {
        "description": "TAI timestamp formatted as <s>:<ns>",
        "type": "string",
        "pattern": _tai_s_ns_regex
    },
    "max_ts": {
        "description": "TAI timestamp formatted as <s>:<ns>",
        "type": "string",
        "pattern": _tai_s_ns_regex
    },
    "tags": tag_schema
  },
  "additionalProperties": False
}
