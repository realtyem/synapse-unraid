/* Copyright 2022 The Matrix.org Foundation C.I.C
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

-- Allow there to be multiple summaries per user/room.
DROP INDEX IF EXISTS event_push_summary_unique_index;

INSERT INTO background_updates (ordering, update_name, progress_json, depends_on) VALUES
  (7306, 'event_push_actions_thread_id_null', '{}', 'event_push_backfill_thread_id');

INSERT INTO background_updates (ordering, update_name, progress_json, depends_on) VALUES
  (7306, 'event_push_summary_thread_id_null', '{}', 'event_push_backfill_thread_id');
