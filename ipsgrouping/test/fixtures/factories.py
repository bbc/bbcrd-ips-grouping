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

from ipsgrouping.test.fixtures.valid_group import valid_group_v2_0
from ipsgrouping.test.fixtures.valid_package import valid_package_v2_0
from copy import copy


def factory(original):
    def factory_instance(**kwargs):
        base = copy(original)
        base.update(kwargs)
        return base
    return factory_instance


def make_payload(template):
    copy_template = copy(template)
    # representations don't have ids, remove.
    copy_template.pop("id", None)
    return copy_template


group_factory_v2_0 = factory(make_payload(valid_group_v2_0))

package_factory_v2_0 = factory(make_payload(valid_package_v2_0))

group_factory = group_factory_v2_0     # default to v2_0
package_factory = package_factory_v2_0
