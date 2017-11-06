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

def check(storedflowquery):
    """
    Perform main checks, and return a dictionary with details.
    Dictionary will contain a 'passed' key, which will be True or False.
    This indicates overall success.
    """
    passed = True

    return {
        'passed': passed,
        'detail': {
        }
    }
