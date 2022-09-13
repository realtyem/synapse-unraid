#!/usr/bin/env python
# Copyright 2022 The Matrix.org Foundation C.I.C.
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

# Calculate the trial jobs to run based on if we're in a PR or not.

import json

# First calculate the various trial jobs.
#
# For each type of test we only run on Pypy3.9 on PRs

trial_sqlite_tests = [
    {
        "python-version": "pypy3.9",
        "database": "sqlite",
        "extras": "all",
    }
]

trial_postgres_tests = [
    {
        "python-version": "pypy3.9",
        "database": "postgres",
        "postgres-version": "14",
        "extras": "all",
    },
    {
        "python-version": "pypy3.9",
        "database": "postgres",
        "postgres-version": "13",
        "extras": "all",
    },
]

trial_no_extra_tests = [
    {
        "python-version": "pypy3.9",
        "database": "sqlite",
        "extras": "",
    }
]

print("::group::Calculated trial jobs")
print(
    json.dumps(
        trial_sqlite_tests + trial_postgres_tests + trial_no_extra_tests, indent=4
    )
)
print("::endgroup::")

test_matrix = json.dumps(
    trial_sqlite_tests + trial_postgres_tests + trial_no_extra_tests
)
print(f"::set-output name=trial_test_matrix::{test_matrix}")


# First calculate the various sytest jobs.
#
# For each type of test we only run on focal on PRs


sytest_tests = [
    {
        "sytest-tag": "bookworm-python3.10",
    },
    {
        "sytest-tag": "bookworm-python3.10",
        "postgres": "postgres",
    },
    {
        "sytest-tag": "bookworm-python3.10",
        "postgres": "multi-postgres",
        "workers": "workers",
    },
    {
        "sytest-tag": "testing",
    },
    {
        "sytest-tag": "testing",
        "postgres": "postgres",
        "workers": "workers",
    },
]

print("::group::Calculated sytest jobs")
print(json.dumps(sytest_tests, indent=4))
print("::endgroup::")

test_matrix = json.dumps(sytest_tests)
print(f"::set-output name=sytest_test_matrix::{test_matrix}")
