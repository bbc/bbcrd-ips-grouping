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

from nose.loader import TestLoader
from nose import run
from nose.suite import LazySuite

TESTS = {
    'generic': [
        'test_database'
    ],
    'versioned': [
        'test_v2_0'
    ]
}


all_tests = TestLoader().loadTestsFromNames(TESTS["generic"] + TESTS["versioned"])
latest_tests = TestLoader().loadTestsFromNames(TESTS["generic"] + [TESTS["versioned"][-1]])


def runner(tests):
    def _run():
        suite = LazySuite(tests)
        run(suite=suite)
    return _run

run_all = runner(all_tests)
run_latest = runner(latest_tests)

if __name__ == '__main__':
    run_latest()
