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


group_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "description": "Register a new Group or update an existing resource",
    "title": "Group registration",
    "required": [
        "label",
        "description",
        "resource_type",
        "members",
        "tags"
    ],
    "properties": {
        "label": {
            "description": "Freeform string label for the Group",
            "type": "string"
        },
        "description": {
            "description": "Freeform string description for the Group",
            "type": "string"
        },
        "resource_type": {
            "description": "Type of the resources refered to in members",
            "type": "string"
        },
        "members": {
            "description": "Hash of UUIDs representing the IDs of resources to be grouped together by this group",
            "type": "object",
            "patternProperties": {
              "^.*$": {
                "type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
              }
            },
            "additionalProperties": False
        },
        "tags": tag_schema
    },
    "additionalProperties": False
 }
