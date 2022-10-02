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

# Copied heavily from calculate_jobs.py to set various complement jobs.

import json

# Calculate the various types of workers.
#
# For each type of test we only run on Py3.10

complement_worker_tests = [
    {
        "arrangement": "workers",
        "database": "Postgres",
        "worker_types": workers,
    }
    for workers in (
        "account_data",
        # "appservice",
        "background_worker",
        "event_creator",
        "event_persister",
        "federation_inbound",
        "federation_reader",
        "federation_sender",
        "frontend_proxy",
        "media_repository",
        "presence",
        "pusher",
        "receipts",
        "synchrotron",
        "to_device",
        "typing",
        "user_dir",
    )
]

print("::group::Calculated complement jobs")
print(
    json.dumps(
        complement_worker_tests, indent=4
    )
)
print("::endgroup::")

test_matrix = json.dumps(
    complement_worker_tests
)
print(f"::set-output name=complement_test_matrix::{test_matrix}")
