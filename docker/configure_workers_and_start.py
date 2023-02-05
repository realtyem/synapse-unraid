#!/usr/bin/env python
# Copyright 2021 The Matrix.org Foundation C.I.C.
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

# This script reads environment variables and generates a shared Synapse worker,
# nginx and supervisord configs depending on the workers requested.
#
# The environment variables it reads are:
#   * SYNAPSE_SERVER_NAME: The desired server_name of the homeserver.
#   * SYNAPSE_REPORT_STATS: Whether to report stats.
#   * SYNAPSE_WORKER_TYPES: A comma separated list of worker names as specified in WORKERS_CONFIG
#         below. Leave empty for no workers. Add a ':' and a number at the end to
#         multiply that worker. Append multiple worker types with '+' to merge the
#         worker types into a single worker. Add a name and a '=' to the front of a
#         worker type to give this instance a name in logs and nginx.
#         Examples:
#         SYNAPSE_WORKER_TYPES='event_persister, federation_sender, client_reader'
#         SYNAPSE_WORKER_TYPES='event_persister:2, federation_sender:2, client_reader'
#         SYNAPSE_WORKER_TYPES='stream_writers=account_data+presence+typing'
#   * SYNAPSE_AS_REGISTRATION_DIR: If specified, a directory in which .yaml and .yml files
#         will be treated as Application Service registration files.
#   * SYNAPSE_TLS_CERT: Path to a TLS certificate in PEM format.
#   * SYNAPSE_TLS_KEY: Path to a TLS key. If this and SYNAPSE_TLS_CERT are specified,
#         Nginx will be configured to serve TLS on port 8448.
#   * SYNAPSE_USE_EXPERIMENTAL_FORKING_LAUNCHER: Whether to use the forking launcher,
#         only intended for usage in Complement at the moment.
#         No stability guarantees are provided.
#   * SYNAPSE_LOG_LEVEL: Set this to DEBUG, INFO, WARNING or ERROR to change the
#         log level. INFO is the default.
#   * SYNAPSE_LOG_SENSITIVE: If unset, SQL and SQL values won't be logged,
#         regardless of the SYNAPSE_LOG_LEVEL setting.
#
# NOTE: According to Complement's ENTRYPOINT expectations for a homeserver image (as
# defined in the project's README), this script may be run multiple times, and
# functionality should continue to work if so.

import codecs
import os
import platform
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, NoReturn, Optional, Set

import yaml
from jinja2 import Environment, FileSystemLoader

MAIN_PROCESS_HTTP_LISTENER_PORT = 8080
MAIN_PROCESS_HTTP_METRICS_LISTENER_PORT = 8060
enable_compressor = False
enable_coturn = False
enable_prometheus = False
enable_redis_exporter = False
enable_postgres_exporter = False

# Workers with exposed endpoints needs either "client", "federation", or "media"
#   listener_resources
# Watching /_matrix/client needs a "client" listener
# Watching /_matrix/federation needs a "federation" listener
# Watching /_matrix/media and related needs a "media" listener
# Stream Writers require "client" and "replication" listeners because they
#   have to attach by instance_map to the master process and have client endpoints.
WORKERS_CONFIG: Dict[str, Dict[str, Any]] = {
    "pusher": {
        "app": "synapse.app.generic_worker",
        "listener_resources": [],
        "endpoint_patterns": [],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "user_dir": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["client"],
        "endpoint_patterns": [
            "^/_matrix/client/(api/v1|r0|v3|unstable)/user_directory/search$"
        ],
        "shared_extra_conf": {"update_user_directory_from_worker": "placeholder_name"},
        "worker_extra_conf": "",
    },
    "media_repository": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["media"],
        "endpoint_patterns": [
            "^/_matrix/media/",
            "^/_synapse/admin/v1/purge_media_cache$",
            "^/_synapse/admin/v1/room/.*/media.*$",
            "^/_synapse/admin/v1/user/.*/media.*$",
            "^/_synapse/admin/v1/media/.*$",
            "^/_synapse/admin/v1/room/.*/media/quarantine$",
        ],
        # The first configured media worker will run the media background jobs
        "shared_extra_conf": {
            "enable_media_repo": False,
            "media_instance_running_background_jobs": "placeholder_name",
        },
        "worker_extra_conf": "enable_media_repo: true",
    },
    "appservice": {
        "app": "synapse.app.generic_worker",
        "listener_resources": [],
        "endpoint_patterns": [],
        "shared_extra_conf": {"notify_appservices_from_worker": "placeholder_name"},
        "worker_extra_conf": "",
    },
    "federation_sender": {
        "app": "synapse.app.generic_worker",
        "listener_resources": [],
        "endpoint_patterns": [],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "synchrotron": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["client"],
        "endpoint_patterns": [
            "^/_matrix/client/(r0|v3|unstable)/sync$",
            "^/_matrix/client/(api/v1|r0|v3)/events$",
            "^/_matrix/client/(api/v1|r0|v3)/initialSync$",
            # "^/_matrix/client/(api/v1|r0|v3)/rooms/[^/]+/initialSync$",
        ],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "client_reader": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["client"],
        "endpoint_patterns": [
            "^/_matrix/client/(api/v1|r0|v3|unstable)/publicRooms$",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/rooms/.*/joined_members$",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/rooms/.*/context/.*$",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/rooms/.*/members$",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/rooms/.*/state$",
            "^/_matrix/client/v1/rooms/.*/hierarchy$",
            "^/_matrix/client/(v1|unstable)/rooms/.*/relations/",
            "^/_matrix/client/v1/rooms/.*/threads$",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/login$",
            "^/_matrix/client/(r0|v3|unstable)/account/3pid$",
            "^/_matrix/client/(r0|v3|unstable)/account/whoami$",
            "^/_matrix/client/versions$",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/voip/turnServer$",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/register$",
            "^/_matrix/client/(r0|v3|unstable)/auth/.*/fallback/web$",
            # This one needs to be routed by the .* cuz that's the room name.
            "^/_matrix/client/(api/v1|r0|v3|unstable)/rooms/.*/messages$",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/rooms/.*/event",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/joined_rooms",
            "^/_matrix/client/(r0|v3|unstable/.*)/rooms/.*/aliases",
            "^/_matrix/client/v1/rooms/.*/timestamp_to_event$",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/search",
        ],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "federation_reader": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["federation"],
        "endpoint_patterns": [
            "^/_matrix/federation/(v1|v2)/event/",
            "^/_matrix/federation/(v1|v2)/state/",
            "^/_matrix/federation/(v1|v2)/state_ids/",
            "^/_matrix/federation/(v1|v2)/backfill/",
            "^/_matrix/federation/(v1|v2)/get_missing_events/",
            "^/_matrix/federation/(v1|v2)/publicRooms",
            "^/_matrix/federation/(v1|v2)/query/",
            "^/_matrix/federation/(v1|v2)/make_join/",
            "^/_matrix/federation/(v1|v2)/make_leave/",
            "^/_matrix/federation/(v1|v2)/send_join/",
            "^/_matrix/federation/(v1|v2)/send_leave/",
            "^/_matrix/federation/(v1|v2)/invite/",
            "^/_matrix/federation/(v1|v2)/query_auth/",
            "^/_matrix/federation/(v1|v2)/event_auth/",
            "^/_matrix/federation/v1/timestamp_to_event/",
            "^/_matrix/federation/(v1|v2)/exchange_third_party_invite/",
            "^/_matrix/federation/(v1|v2)/user/devices/",
            "^/_matrix/federation/(v1|v2)/get_groups_publicised$",
            "^/_matrix/key/v2/query",
        ],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "federation_inbound": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["federation"],
        "endpoint_patterns": ["^/_matrix/federation/(v1|v2)/send/"],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "event_persister": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["replication"],
        "endpoint_patterns": [],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "background_worker": {
        "app": "synapse.app.generic_worker",
        "listener_resources": [],
        "endpoint_patterns": [],
        # This worker cannot be sharded. Therefore, there should only ever be one
        # background worker. This is enforced for the safety of your database.
        "shared_extra_conf": {"run_background_tasks_on": "placeholder_name"},
        "worker_extra_conf": "",
    },
    "event_creator": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["client"],
        "endpoint_patterns": [
            "^/_matrix/client/(api/v1|r0|v3|unstable)/rooms/.*/redact",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/rooms/.*/send",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/rooms/.*/(join|invite|leave|ban|unban|kick)$",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/join/",
            "^/_matrix/client/(api/v1|r0|v3|unstable)/profile/",
            "^/_matrix/client/(v1|unstable/org.matrix.msc2716)/rooms/.*/batch_send",
        ],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "frontend_proxy": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["client"],
        "endpoint_patterns": ["^/_matrix/client/(api/v1|r0|v3|unstable)/keys/upload"],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "account_data": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["client", "replication"],
        "endpoint_patterns": [
            "^/_matrix/client/(r0|v3|unstable)/.*/tags",
            "^/_matrix/client/(r0|v3|unstable)/.*/account_data",
        ],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "presence": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["client", "replication"],
        "endpoint_patterns": ["^/_matrix/client/(api/v1|r0|v3|unstable)/presence/"],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "receipts": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["client", "replication"],
        "endpoint_patterns": [
            "^/_matrix/client/(r0|v3|unstable)/rooms/.*/receipt",
            "^/_matrix/client/(r0|v3|unstable)/rooms/.*/read_markers",
        ],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "to_device": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["client", "replication"],
        "endpoint_patterns": ["^/_matrix/client/(r0|v3|unstable)/sendToDevice/"],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
    "typing": {
        "app": "synapse.app.generic_worker",
        "listener_resources": ["client", "replication"],
        "endpoint_patterns": [
            "^/_matrix/client/(api/v1|r0|v3|unstable)/rooms/.*/typing"
        ],
        "shared_extra_conf": {},
        "worker_extra_conf": "",
    },
}

# Templates for sections that may be inserted multiple times in config files
NGINX_LOCATION_CONFIG_BLOCK = """
    location ~* {endpoint} {{
        proxy_pass {upstream};
        proxy_buffering off;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }}
"""

NGINX_UPSTREAM_CONFIG_BLOCK = """
upstream {upstream_worker_base_name} {{
{body}
}}
"""

NGINX_UPSTREAM_HASH_BY_CLIENT_IP_CONFIG_BLOCK = """
upstream {upstream_worker_base_name} {{
    hash $proxy_add_x_forwarded_for;
{body}
}}
"""

NGINX_UPSTREAM_HASH_BY_AUTH_HEADER_BLOCK = """
upstream {upstream_worker_base_name} {{
    hash $http_authorization consistent;
{body}
}}
"""

PROMETHEUS_SCRAPE_CONFIG_BLOCK = """
    - targets: ["127.0.0.1:{metrics_port}"]
      labels:
        instance: "Synapse"
        job: "{name}"
        index: {index}
"""


# Utility functions
def log(txt: str) -> None:
    print(txt, flush=True)


def error(txt: str) -> NoReturn:
    print(txt, file=sys.stderr, flush=True)
    sys.exit(2)


def flush_buffers() -> None:
    sys.stdout.flush()
    sys.stderr.flush()


def convert(src: str, dst: str, **template_vars: object) -> None:
    """Generate a file from a template

    Args:
        src: Path to the input file.
        dst: Path to write to.
        template_vars: The arguments to replace placeholder variables in the template
            with.
    """
    # Read the template file
    # We disable autoescape to prevent template variables from being escaped,
    # as we're not using HTML.
    env = Environment(loader=FileSystemLoader(os.path.dirname(src)), autoescape=False)
    template = env.get_template(os.path.basename(src))

    # Generate a string from the template.
    rendered = template.render(**template_vars)

    # Write the generated contents to a file
    #
    # We use append mode in case the files have already been written to by something
    # else (for instance, as part of the instructions in a dockerfile).
    with open(dst, "a") as outfile:
        # In case the existing file doesn't end with a newline
        outfile.write("\n")

        outfile.write(rendered)


def getenv_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("yes", "y", "true", "1", "t", "on")


def add_worker_roles_to_shared_config(
    shared_config: dict,
    worker_type_list: list,
    worker_name: str,
    worker_port: int,
) -> None:
    """Given a dictionary representing a config file shared across all workers,
    append appropriate worker information to it for the current worker_type instance.

    Args:
        shared_config: The config dict that all worker instances share (after being
            converted to YAML)
        worker_type_list: The type of worker (one of those defined in WORKERS_CONFIG).
            This list can be a single worker type or multiple.
        worker_name: The name of the worker instance.
        worker_port: The HTTP replication port that the worker instance is listening on.
    """
    # The instance_map config field marks the workers that write to various replication
    # streams
    instance_map = shared_config.setdefault("instance_map", {})

    # This is a list of the stream_writers that there can be only one of. Events can be
    # sharded, and therefore doesn't belong here.
    singular_stream_writers = [
        "account_data",
        "presence",
        "receipts",
        "to_device",
        "typing",
    ]

    # Worker-type specific sharding config. Now a single worker can fulfill multiple
    # roles, check each.
    if "pusher" in worker_type_list:
        shared_config.setdefault("pusher_instances", []).append(worker_name)

    if "federation_sender" in worker_type_list:
        shared_config.setdefault("federation_sender_instances", []).append(worker_name)

    if "event_persister" in worker_type_list:
        # Event persisters write to the events stream, so we need to update
        # the list of event stream writers
        shared_config.setdefault("stream_writers", {}).setdefault("events", []).append(
            worker_name
        )

        # Map of stream writer instance names to host/ports combos
        instance_map[worker_name] = {
            "host": "localhost",
            "port": worker_port,
        }

    # Update the list of stream writers. It's convenient that the name of the worker
    # type is the same as the stream to write. Iterate over the whole list in case there
    # is more than one.
    for worker in worker_type_list:
        if worker in singular_stream_writers:
            shared_config.setdefault("stream_writers", {}).setdefault(
                worker, []
            ).append(worker_name)

            # Map of stream writer instance names to host/ports combos
            # For now, all stream writers need http replication ports
            instance_map[worker_name] = {
                "host": "localhost",
                "port": worker_port,
            }


def merge_worker_template_configs(
    existing_dict: Dict[str, Any],
    to_be_merged_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """When given an existing dict of worker template configuration, merge new template
        data from WORKERS_CONFIG and return new dict.

    Args:
        existing_dict: Either an existing worker template or a fresh blank one.
        to_be_merged_dict: The template from WORKERS_CONFIGS to be merged into
            existing_dict.
    Returns: The newly merged together dict values.
    """
    new_dict: Dict[str, Any] = {}
    for i in to_be_merged_dict.keys():
        if (i == "endpoint_patterns") or (i == "listener_resources"):
            # merge the two lists, remove duplicates
            new_dict[i] = list(set(existing_dict[i] + to_be_merged_dict[i]))
        elif i == "shared_extra_conf":
            # merge dictionary's, the worker name will be replaced below after counting
            new_dict[i] = {**existing_dict[i], **to_be_merged_dict[i]}
        elif i == "worker_extra_conf":
            # There is only one worker type that has a 'worker_extra_conf' and it is
            # the media_repo. Since duplicate worker types on the same worker don't
            # work, this is fine.
            new_dict[i] = existing_dict[i] + to_be_merged_dict[i]
        else:
            # Everything else should be identical, like "app", which only works because
            # all apps are now generic_workers.
            new_dict[i] = to_be_merged_dict[i]
    return new_dict


def insert_worker_name_for_worker_config(
    existing_dict: Dict[str, Any], worker_name: str
) -> Dict[str, Any]:
    """Insert a given worker name into the worker's configuration dict.

    Args:
        existing_dict: The worker_config dict that is imported into shared_config.
        worker_name: The name of the worker to insert.
    Returns: Copy of the dict with newly inserted worker name
    """
    dict_to_edit = existing_dict.copy()
    for k, v in dict_to_edit["shared_extra_conf"].items():
        # Only proceed if it's a string as some values are boolean
        if isinstance(dict_to_edit["shared_extra_conf"][k], str):
            # This will be ignored if the text isn't the placeholder.
            dict_to_edit["shared_extra_conf"][k] = v.replace(
                "placeholder_name", worker_name
            )
    return dict_to_edit


def is_sharding_allowed_for_worker_type(worker_type: str) -> bool:
    """Helper to check to make sure worker types that cannot have multiples do not.

    Args:
        worker_type: The type of worker to check against.
    Returns: True if allowed, False if not
    """
    if worker_type in [
        "background_worker",
        "account_data",
        "presence",
        "receipts",
        "typing",
        "to_device",
    ]:
        return False
    else:
        return True


def increment_counter(worker_type_counter: Dict[str, int], worker_type: str) -> int:
    """Given a dict of worker_type:int, increment int

    Args:
        worker_type_counter: dict to increment
        worker_type: str of worker_type
    Returns: int of new value of counter
    """
    new_worker_count = worker_type_counter.setdefault(worker_type, 0) + 1
    worker_type_counter[worker_type] = new_worker_count
    return new_worker_count


def is_name_allowed_for_worker(
    worker_type_counter: Dict[str, str], worker_base_name: str, worker_type: str
) -> bool:
    """Given a dict of worker_base_name:worker_type, check if this worker_base_name has
        been seen before.

    Args:
        worker_type_counter: dict of worker_base_name:worker_type.
        worker_base_name: str of the base worker name, no appended number.
        worker_type: str of the worker_type, including combo workers.
    Returns: True if allowed, False if not
    """
    counter_to_check = worker_type_counter.get(worker_base_name)
    if counter_to_check is not None:
        if counter_to_check == worker_type:
            # Key exists, and they match so it should be ok.
            return True
        else:
            return False
    else:
        # Key doesn't exist, it's ok to use.
        return True


def split_and_strip_string(given_string: str, split_char: str) -> List:
    # Removes whitespace from ends of result strings before adding to list.
    return [x.strip() for x in given_string.split(split_char)]


def generate_base_homeserver_config() -> None:
    """Starts Synapse and generates a basic homeserver config, which will later be
    modified for worker support.

    Raises: CalledProcessError if calling start.py returned a non-zero exit code.
    """
    # start.py already does this for us, so just call that.
    # note that this script is copied in in the official, monolith dockerfile
    os.environ["SYNAPSE_HTTP_PORT"] = str(MAIN_PROCESS_HTTP_LISTENER_PORT)
    os.environ["SYNAPSE_METRICS_HTTP_PORT"] = str(
        MAIN_PROCESS_HTTP_METRICS_LISTENER_PORT
    )
    subprocess.run(["/usr/local/bin/python", "/start.py", "migrate_config"], check=True)


def generate_worker_files(
    environ: Mapping[str, str], config_path: str, data_dir: str
) -> None:
    """Read the desired list of workers from environment variables and generate
    shared homeserver, nginx and supervisord configs.

    Args:
        environ: os.environ instance.
        config_path: The location of the generated Synapse main worker config file.
        data_dir: The location of the synapse data directory. Where log and
            user-facing config files live.
    """
    # Note that yaml cares about indentation, so care should be taken to insert lines
    # into files at the correct indentation below.

    # shared_config is the contents of a Synapse config file that will be shared amongst
    # the main Synapse process as well as all workers.
    # It is intended mainly for disabling functionality when certain workers are spun
    # up, and adding a replication listener.

    # pass through global variables for the add-ons
    # the auto compressor is taken care of in main
    global enable_prometheus
    global enable_redis_exporter
    enable_manhole_workers = getenv_bool("SYNAPSE_MANHOLE_WORKERS", False)

    # First read the original config file and extract the listeners block. Then we'll
    # add another listener for replication. Later we'll write out the result to the
    # shared config file.
    listeners = [
        {
            "port": 9093,
            "bind_address": "127.0.0.1",
            "type": "http",
            "resources": [{"names": ["replication"]}],
        }
    ]
    with open(config_path) as file_stream:
        original_config = yaml.safe_load(file_stream)
        original_listeners = original_config.get("listeners")
        if original_listeners:
            listeners += original_listeners

    # Only activate the manhole if the environment says to do so. SYNAPSE_MANHOLE_MASTER
    if getenv_bool("SYNAPSE_MANHOLE_MASTER", False):
        # The manhole listener is basically the same as other listeners. Needs a type
        # "manhole". The workers have ports starting with 17009, so we'll take one just
        # prior to that. In practice, we don't need to bind address because we are in
        # docker and are not going to expose this outside.
        manhole_listener = [
            {
                "type": "manhole",
                "port": 17008,
            }
        ]
        listeners += manhole_listener

    # The shared homeserver config. The contents of which will be inserted into the
    # base shared worker jinja2 template.
    #
    # This config file will be passed to all workers, included Synapse's main process.
    shared_config: Dict[str, Any] = {"listeners": listeners}

    # List of dicts that describe workers.
    # We pass this to the Supervisor template later to generate the appropriate
    # program blocks.
    worker_descriptors: List[Dict[str, Any]] = []

    # Upstreams for load-balancing purposes. This dict takes the form of a worker type
    # to the ports of each worker. For example:
    # {
    #   worker_type: {1234, 1235, ...}}
    # }
    # and will be used to construct 'upstream' nginx directives.
    nginx_upstreams: Dict[str, Set[int]] = {}

    # A map of: {"endpoint": "upstream"}, where "upstream" is a str representing what
    # will be placed after the proxy_pass directive. The main benefit to representing
    # this data as a dict over a str is that we can easily deduplicate endpoints across
    # multiple instances of the same worker.
    #
    # An nginx site config that will be amended to depending on the workers that are
    # spun up. To be placed in /etc/nginx/conf.d.
    nginx_locations = {}

    # Read the desired worker configuration from the environment
    worker_types_env = environ.get("SYNAPSE_WORKER_TYPES", "").strip()
    # Some shortcuts.
    if worker_types_env == "full":
        worker_types_env = (
            "account_data,background_worker,event_creator,"
            "event_persister,federation_inbound,federation_reader,"
            "federation_sender,frontend_proxy,media_repository,"
            "presence,pusher,receipts,to_device,typing,synchrotron,"
            "user_dir"
        )

    if worker_types_env == "BLOW_IT_UP":
        # 500 Postgres connections means about 48 workers. Challenge accepted.
        # Note: my machine only seems to be ok with 45 workers, so use that.
        worker_types_env = (
            "account_data+presence+receipts+to_device+typing, "
            "background_worker, client_reader:2, event_creator:2, "
            "event_persister:5, federation_inbound:4, "
            "federation_reader:4, federation_sender:16, "
            "frontend_proxy, media_repository:2, pusher:2, "
            "synchrotron:4, user_dir"
        )

    if not worker_types_env:
        # No workers, just the main process
        worker_types = []
    else:
        # Split type names by comma, ignoring whitespace.
        worker_types = [x.strip() for x in worker_types_env.split(",")]

    # Create the worker configuration directory if it doesn't already exist
    os.makedirs("/conf/workers", exist_ok=True)

    # Start worker ports from this arbitrary port
    worker_port = 18009

    # Start worker metrics port from this arbitrary port
    worker_metrics_port = 19009

    # Start worker manhole ports from this port
    worker_manhole_port = 17009

    # A counter of worker_type -> int. Used for determining the name for a given
    # worker type when generating its config file, as each worker's name is just
    # worker_type(s) + instance #
    worker_type_counter: Dict[str, int] = {}

    # Similar to above, but more finely grained. This is used to determine we don't have
    # more than a single worker for cases where multiples would be bad(e.g. presence).
    worker_type_shard_counter: Dict[str, int] = {}

    # Similar to above, but for worker name's. This has two uses:
    # 1. Can be used to check that worker names for different worker types or
    #       combinations of types is not used, as it will error with 'Address in
    #       use'(e.g. "to_device, to_device=typing" would not work).
    # 2. Convenient way to get the combination of worker types from worker_name after
    #       processing and merging.
    # Follows the pattern:
    # ["worker_name": "worker_type(s)"]
    worker_name_type_list: Dict[str, str] = {}

    # A list of internal endpoints to healthcheck, starting with the main process
    # which exists even if no workers do.
    healthcheck_urls = ["http://localhost:8080/health"]

    # Expand worker_type multiples if requested in shorthand(e.g. worker:2). Checking
    # for not an actual defined type of worker is done later.
    # Checking performed:
    # 1. if worker:2 or more is declared, it will create additional workers up to number
    # 2. if worker:1, it will create a single copy of this worker as if no number was
    #   given
    # 3. if worker:0 is declared, this worker will be ignored. This is to allow for
    #   scripting and automated expansion and is intended behaviour.
    # 4. if worker:NaN or is a negative number, it will error and log it.
    new_worker_types = []
    for worker_type in worker_types:
        if ":" in worker_type:
            worker_type_components = split_and_strip_string(worker_type, ":")
            count = 0
            # Should only be 2 components, a type of worker(s) and an integer as a
            # string. Cast the number as an int then it can be used as a counter.
            if (
                len(worker_type_components) == 2
                and worker_type_components[-1].isdigit()
            ):
                count = int(worker_type_components[1])
            else:
                error(
                    "Multiplier signal(:) for worker found, but incorrect components: "
                    + worker_type
                    + ". Please fix."
                )
            # As long as there are more than 0, we add one to the list to make below.
            while count > 0:
                new_worker_types.append(worker_type_components[0])
                count -= 1
        else:
            # If it's not a real worker, it will error out below
            new_worker_types.append(worker_type)

    # worker_types is now an expanded list of worker types.
    worker_types = new_worker_types

    # For each worker type specified by the user, create config values
    for worker_type in worker_types:
        # pre-template the worker_config so when updating we don't get a KeyError
        worker_config: Dict[str, Any] = {
            "app": "",
            "listener_resources": [],
            "endpoint_patterns": [],
            "shared_extra_conf": {},
            "worker_extra_conf": "",
        }

        # Peel off any name designated before a '=' to use later.
        requested_worker_name = ""
        if "=" in worker_type:
            # Split on "=", remove extra whitespace from ends then make list
            worker_type_split = split_and_strip_string(worker_type, "=")
            if len(worker_type_split) > 2:
                error(
                    "To many worker names requested for a single worker, or to many "
                    "'='. Please fix: " + worker_type
                )
            # if there was no name given, this will still be an empty string
            requested_worker_name = worker_type_split[0]
            # Uncommon mistake that will cause problems. Name string containing spaces.
            if len(requested_worker_name.split(" ")) > 1:
                error(
                    "Requesting a worker name containing a space is not allowed, "
                    "as it would raise a FileNotFoundError. Please use an "
                    "underscore instead."
                )
            # Reassign the worker_type string with no name on it.
            worker_type = worker_type_split[1]

        # Split on "+", remove whitespace from ends then make a list.
        workers_to_combo_list = split_and_strip_string(worker_type, "+")

        # Check for duplicates in the split worker type list. No advantage in having
        # duplicated worker types on the same worker. Two would consolidate into one.
        # (e.g. "pusher + pusher" would resolve to a single "pusher" which may not be
        # what was intended.)
        if len(workers_to_combo_list) != len(set(workers_to_combo_list)):
            error("Duplicate worker type found in " + worker_type + "! Please fix.")

        # Merge all worker config templates for this worker into a single config
        for worker in workers_to_combo_list:
            # Verify this is a real defined worker type. If it's not, stop everything so
            # it can be fixed.
            copy_of_template_config = WORKERS_CONFIG.get(worker)
            if copy_of_template_config:
                # So it's not a reference pointer
                copy_of_template_config = copy_of_template_config.copy()
            else:
                error(
                    worker
                    + " is an unknown worker type! Was found in "
                    + worker_type
                    + ". Please fix!"
                )

            # Merge worker type template configuration data.
            worker_config = merge_worker_template_configs(
                worker_config, copy_of_template_config
            )

            # Check if there is to many of a worker there can only be one of.
            # Will error and stop if it is a problem, e.g. 'background_worker'.
            if worker in worker_type_shard_counter:
                if not is_sharding_allowed_for_worker_type(worker):
                    error(
                        "There can be only a single worker with "
                        + worker
                        + " type. Please recount and remove."
                    )
            # Not in shard counter, add it. Don't need return value
            increment_counter(worker_type_shard_counter, worker)

        # Name workers by their type or requested name concatenated with an
        # incrementing number. e.g. federation_reader1 or event_creator+event_persister1
        worker_base_name: str
        if requested_worker_name:
            worker_base_name = requested_worker_name
            # It'll be useful to have this in the log in case it's a complex of many
            # workers merged together. Note for Complement: it would only be seen in the
            # logs for blueprint construction(which are not collected).
            log(
                "Worker name request found: "
                + requested_worker_name
                + ", for: "
                + str(workers_to_combo_list)
            )

        else:
            # The worker name will be the worker_type, however if spaces exist
            # between concatenated worker_types and the "+" because of readability,
            # it will error on startup. Recombine worker_types without spaces and log.
            if len(workers_to_combo_list) > 1:
                worker_base_name = "+".join(workers_to_combo_list)
                if worker_base_name != worker_type:
                    log(
                        "Default worker name would have contained spaces, which is not "
                        "allowed(" + worker_type + "). Reformed name to not contain "
                        "spaces: " + worker_base_name
                    )
            else:
                worker_base_name = worker_type
        # This counter is used for names with broader worker type definitions.
        new_worker_count = increment_counter(worker_type_counter, worker_type)
        worker_name = worker_base_name + str(new_worker_count)

        # Now that the worker name is settled, check this name isn't used for a
        # different worker_type. If it's not allowed, will error and stop. If no issues,
        # it will be added to the counter.
        if is_name_allowed_for_worker(
            worker_name_type_list,
            worker_base_name,
            worker_type,
        ):
            worker_name_type_list.setdefault(worker_base_name, worker_type)

        else:
            error(
                "Can not use "
                + worker_name
                + " for "
                + worker_type
                + ". It is already in use by "
                # This is cast as a str because mypy thinks it could be None
                + str(worker_name_type_list.get(worker_base_name))
            )

        # Replace placeholder names in the config template with the actual worker name.
        worker_config = insert_worker_name_for_worker_config(worker_config, worker_name)

        worker_config.update(
            {
                "name": worker_name,
                "group": worker_base_name,
                "type": worker_type,
                "port": str(worker_port),
                "metrics_port": str(worker_metrics_port),
                "enable_manhole_workers": str(enable_manhole_workers),
                "manhole_port": str(worker_manhole_port),
                "config_path": config_path,
                "index": str(new_worker_count),
            }
        )

        # Update the shared config with any worker-type specific options. Do a dance so
        # the first of a given worker type gets to stay assigned.
        worker_config["shared_extra_conf"].update(shared_config)
        shared_config.update(worker_config["shared_extra_conf"])

        healthcheck_urls.append("http://localhost:%d/health" % (worker_port,))

        # Check if more than one instance of this worker type has been specified
        worker_type_total_count = worker_types.count(worker_type)

        # Update the shared config with sharding-related options if necessary
        add_worker_roles_to_shared_config(
            shared_config, workers_to_combo_list, worker_name, worker_port
        )

        # Enable the worker in supervisord
        worker_descriptors.append(worker_config)

        # Add nginx location blocks for this worker's endpoints (if any are defined)
        for pattern in worker_config["endpoint_patterns"]:
            # Determine whether we need to load-balance this worker
            if worker_type_total_count > 1:
                # Create or add to a load-balanced upstream for this worker
                nginx_upstreams.setdefault(worker_base_name, set()).add(worker_port)

                # Upstreams are named after the worker_base_name
                upstream = "http://" + worker_base_name
            else:
                upstream = "http://localhost:%d" % (worker_port,)

            # Note that this endpoint should proxy to this upstream
            nginx_locations[pattern] = upstream

        # Write out the worker's logging config file
        log_config_filepath = generate_worker_log_config(environ, worker_name, data_dir)

        # Then a worker config file
        convert(
            "/conf/worker.yaml.j2",
            "/conf/workers/{name}.yaml".format(name=worker_name),
            **worker_config,
            worker_log_config_filepath=log_config_filepath,
        )

        worker_port += 1
        worker_metrics_port += 1
        worker_manhole_port += 1

    # Build the nginx location config blocks
    nginx_location_config = ""
    for endpoint, upstream in nginx_locations.items():
        nginx_location_config += NGINX_LOCATION_CONFIG_BLOCK.format(
            endpoint=endpoint,
            upstream=upstream,
        )

    # Determine the load-balancing upstreams to configure
    nginx_upstream_config = ""

    worker_type_load_balance_header_list = ["synchrotron"]
    worker_type_load_balance_ip_list = ["federation_inbound"]

    for upstream_worker_base_name, upstream_worker_ports in nginx_upstreams.items():
        body = ""
        for port in upstream_worker_ports:
            body += "    server localhost:%d;\n" % (port,)
        log("upstream_worker_base_name: " + upstream_worker_base_name)

        # This presents a dilemma. Some endpoints are better load-balanced by
        # Authorization header, and some by remote IP. What do you do if a combo
        # worker was requested that has endpoints for both? As it is likely but not
        # impossible that a user will be on the same IP if they have multiple
        # devices(like at home on Wi-Fi), I believe that balancing by IP would be the
        # broader reaching choice. This is probably only slightly better than
        # round-robin. As such, leave balancing by remote IP as the first of the
        # conditionals below, so if both would apply the first is used.

        # Three additional notes:
        #   1. Federation endpoints shouldn't (necessarily) have Authorization headers,
        #       so using them on these endpoints would be a moot point.
        #   2. For Complement, this situation is reversed as there is only ever a single
        #       IP used during tests, 127.0.0.1.
        #   3. IIRC, it may be possible to hash by both at once, or at least have both
        #       hashes on the same line. If I understand that correctly, the one that
        #       doesn't exist is effectively ignored. However, that requires increasing
        #       the hashmap size in the nginx master config file, which would take more
        #       jinja templating(or at least a 'sed'), and may not be accepted upstream.
        #       Based on previous experiments, increasing this value was required for
        #       hashing by room id, so may end up being a path forward anyway.

        # Some endpoints should be load-balanced by client IP. This way, if it comes
        # from the same IP, it goes to the same worker and should be a smarter way to
        # cache data. This works well for federation.
        if any(
            x in worker_type_load_balance_ip_list
            for x in str(worker_name_type_list.get(upstream_worker_base_name)).split(
                "+"
            )
        ):
            nginx_upstream_config += (
                NGINX_UPSTREAM_HASH_BY_CLIENT_IP_CONFIG_BLOCK.format(
                    upstream_worker_base_name=upstream_worker_base_name,
                    body=body,
                )
            )
        # Some endpoints should be load-balanced by Authorization header. This means
        # that even with a different IP, a user should get the same data from the same
        # upstream source, like a synchrotron worker, with smarter caching of data.
        elif any(
            x in worker_type_load_balance_header_list
            for x in str(worker_name_type_list.get(upstream_worker_base_name)).split(
                "+"
            )
        ):
            nginx_upstream_config += NGINX_UPSTREAM_HASH_BY_AUTH_HEADER_BLOCK.format(
                upstream_worker_base_name=upstream_worker_base_name,
                body=body,
            )
        # Everything else, just use the default basic round-robin scheme.
        else:
            nginx_upstream_config += NGINX_UPSTREAM_CONFIG_BLOCK.format(
                upstream_worker_base_name=upstream_worker_base_name,
                body=body,
            )

    log("nginx_upstream_config block: " + nginx_upstream_config)
    # Setup the metric end point locations, names and indexes
    prom_endpoint_config = ""
    for worker in worker_descriptors:
        prom_endpoint_config += PROMETHEUS_SCRAPE_CONFIG_BLOCK.format(
            name=worker["group"],
            metrics_port=worker["metrics_port"],
            index=worker["index"],
        )

    # Finally, we'll write out the config files.

    # log config for the master process
    master_log_config = generate_worker_log_config(environ, "master", data_dir)
    shared_config["log_config"] = master_log_config

    # Find application service registrations
    appservice_registrations = None
    appservice_registration_dir = os.environ.get("SYNAPSE_AS_REGISTRATION_DIR")
    if appservice_registration_dir:
        # Scan for all YAML files that should be application service registrations.
        appservice_registrations = [
            str(reg_path.resolve())
            for reg_path in Path(appservice_registration_dir).iterdir()
            if reg_path.suffix.lower() in (".yaml", ".yml")
        ]

    workers_in_use = len(worker_types) > 0

    # Shared homeserver config
    convert(
        "/conf/shared.yaml.j2",
        "/conf/workers/shared.yaml",
        shared_worker_config=yaml.dump(shared_config),
        appservice_registrations=appservice_registrations,
        enable_redis=workers_in_use,
        workers_in_use=workers_in_use,
    )

    # Nginx config
    convert(
        "/conf/nginx.conf.j2",
        "/etc/nginx/conf.d/matrix-synapse.conf",
        worker_locations=nginx_location_config,
        upstream_directives=nginx_upstream_config,
        tls_cert_path=os.environ.get("SYNAPSE_TLS_CERT"),
        tls_key_path=os.environ.get("SYNAPSE_TLS_KEY"),
    )

    # Prometheus config
    convert(
        "/conf/prometheus.yml.j2",
        "/etc/prometheus/prometheus.yml",
        metric_endpoint_locations=prom_endpoint_config,
    )

    # Supervisord config
    os.makedirs("/etc/supervisor", exist_ok=True)
    convert(
        "/conf/supervisord.conf.j2",
        "/etc/supervisor/supervisord.conf",
        main_config_path=config_path,
        enable_redis=workers_in_use,
        enable_redis_exporter=enable_redis_exporter,
        enable_postgres_exporter=enable_postgres_exporter,
        enable_prometheus=enable_prometheus,
        enable_compressor=enable_compressor,
        enable_coturn=enable_coturn,
    )

    convert(
        "/conf/synapse.supervisord.conf.j2",
        "/etc/supervisor/conf.d/synapse.conf",
        workers=worker_descriptors,
        main_config_path=config_path,
        use_forking_launcher=environ.get("SYNAPSE_USE_EXPERIMENTAL_FORKING_LAUNCHER"),
    )

    # healthcheck config
    convert(
        "/conf/healthcheck.sh.j2",
        "/healthcheck.sh",
        healthcheck_urls=healthcheck_urls,
    )

    # Ensure the logging directory exists
    log_dir = data_dir + "/logs"
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)


def generate_worker_log_config(
    environ: Mapping[str, str], worker_name: str, data_dir: str
) -> str:
    """Generate a log.config file for the given worker.

    Returns: the path to the generated file
    """
    # Check whether we should write worker logs to disk, in addition to the console
    extra_log_template_args: Dict[str, Optional[str]] = {}
    if environ.get("SYNAPSE_WORKERS_WRITE_LOGS_TO_DISK"):
        extra_log_template_args["LOG_FILE_PATH"] = f"{data_dir}/logs/{worker_name}.log"

    extra_log_template_args["SYNAPSE_LOG_LEVEL"] = environ.get("SYNAPSE_LOG_LEVEL")
    extra_log_template_args["SYNAPSE_LOG_SENSITIVE"] = environ.get(
        "SYNAPSE_LOG_SENSITIVE"
    )

    # Render and write the file
    log_config_filepath = f"/conf/workers/{worker_name}.log.config"
    convert(
        "/conf/log.config",
        log_config_filepath,
        worker_name=worker_name,
        **extra_log_template_args,
        include_worker_name_in_log_line=environ.get(
            "SYNAPSE_USE_EXPERIMENTAL_FORKING_LAUNCHER"
        ),
    )
    return log_config_filepath


def main(args: List[str], environ: MutableMapping[str, str]) -> None:
    config_dir = environ.get("SYNAPSE_CONFIG_DIR", "/data")
    config_path = environ.get("SYNAPSE_CONFIG_PATH", config_dir + "/homeserver.yaml")
    data_dir = environ.get("SYNAPSE_DATA_DIR", "/data")
    # Enable add-ons from environment string
    global enable_compressor
    global enable_coturn
    global enable_prometheus
    global enable_redis_exporter
    global enable_postgres_exporter
    enable_compressor = (
        getenv_bool("SYNAPSE_ENABLE_COMPRESSOR", False)
        and "POSTGRES_PASSWORD" in environ
    )
    enable_coturn = getenv_bool("SYNAPSE_ENABLE_BUILTIN_COTURN", False)
    enable_prometheus = getenv_bool("SYNAPSE_METRICS", False)
    enable_redis_exporter = (
        getenv_bool("SYNAPSE_ENABLE_REDIS_METRIC_EXPORT", False)
        and enable_prometheus is True
    )
    enable_postgres_exporter = (
        getenv_bool("SYNAPSE_ENABLE_POSTGRES_METRIC_EXPORT", False)
        and "POSTGRES_PASSWORD" in environ
    )

    # override SYNAPSE_NO_TLS, we don't support TLS in worker mode,
    # this needs to be handled by a frontend proxy
    environ["SYNAPSE_NO_TLS"] = "yes"

    # Sanitize the environment to keep a bunch of junk out of the jinja templates
    environ["SYNAPSE_METRICS"] = str(getenv_bool("SYNAPSE_METRICS", False))
    environ["SYNAPSE_ENABLE_REGISTRATION"] = str(
        getenv_bool("SYNAPSE_ENABLE_REGISTRATION", False)
    )
    environ["SYNAPSE_ALLOW_GUEST"] = str(getenv_bool("SYNAPSE_ALLOW_GUEST", False))
    environ["SYNAPSE_URL_PREVIEW_ENABLED"] = str(
        getenv_bool("SYNAPSE_URL_PREVIEW_ENABLED", False)
    )
    environ["SYNAPSE_SERVE_SERVER_WELLKNOWN"] = str(
        getenv_bool("SYNAPSE_SERVE_SERVER_WELLKNOWN", False)
    )
    environ["SYNAPSE_EMAIL"] = str(getenv_bool("SYNAPSE_EMAIL", False))
    if enable_coturn is True:
        if "SYNAPSE_TURN_SECRET" not in environ:
            log("Generating a random secret for SYNAPSE_TURN_SECRET")
            value = codecs.encode(os.urandom(32), "hex").decode()
            environ["SYNAPSE_TURN_SECRET"] = value

        if "SYNAPSE_TURN_URIS" not in environ:
            log("Make sure you setup port forwarding for port 3478")
            value = "turn:%s:3478?transport=udp,turn:%s:3478?transport=tcp" % (
                environ["SYNAPSE_SERVER_NAME"],
                environ["SYNAPSE_SERVER_NAME"],
            )
            environ["SYNAPSE_TURN_URIS"] = value

        if "COTURN_EXTERNAL_IP" not in environ:
            value = urllib.request.urlopen("https://v4.ident.me").read().decode("utf8")
            environ["COTURN_EXTERNAL_IP"] = value

        if "COTURN_INTERNAL_IP" not in environ:
            value = str(socket.gethostbyname(socket.gethostname()))
            environ["COTURN_INTERNAL_IP"] = value

        if "COTURN_MIN_PORT" not in environ:
            value = "49153"
            environ["COTURN_MIN_PORT"] = value

        if "COTURN_MAX_PORT" not in environ:
            value = "49173"
            environ["COTURN_MAX_PORT"] = value

        environ["COTURN_METRICS"] = str(getenv_bool("COTURN_METRICS", False))

    # Generate the base homeserver config if one does not yet exist
    if not os.path.exists(config_path):
        log("Generating base homeserver config")
        generate_base_homeserver_config()

    # This script may be run multiple times (mostly by Complement, see note at top of
    # file). Don't re-configure workers in this instance.
    mark_filepath = "/conf/workers_have_been_configured"
    if not os.path.exists(mark_filepath):
        # This gets added here instead of above so it only runs one time.
        # Add cron service and crontab file if enabled in environment.
        if enable_compressor is True:
            shutil.copy("/conf/synapse_auto_compressor.job", "/etc/cron.d/")
            convert(
                "/conf/run_compressor.sh.j2",
                "/conf/run_compressor.sh",
                postgres_user=os.environ.get("POSTGRES_USER"),
                postgres_password=os.environ.get("POSTGRES_PASSWORD"),
                postgres_db=os.environ.get("POSTGRES_DB"),
                postgres_host=os.environ.get("POSTGRES_HOST"),
                postgres_port=os.environ.get("POSTGRES_PORT"),
            )
            # Make the custom script we just made executable, as it's run by cron.
            subprocess.run(
                ["chmod", "0755", "/conf/run_compressor.sh"], stdout=subprocess.PIPE
            ).stdout.decode("utf-8")
            # Actually add it to cron explicitly.
            subprocess.run(
                ["crontab", "/etc/cron.d/synapse_auto_compressor.job"],
                stdout=subprocess.PIPE,
            ).stdout.decode("utf-8")

        # Make postgres_exporter custom script if enabled in environment.
        if enable_postgres_exporter is True:
            convert(
                "/conf/run_pg_exporter.sh.j2",
                "/conf/run_pg_exporter.sh",
                postgres_user=os.environ.get("POSTGRES_USER"),
                postgres_password=os.environ.get("POSTGRES_PASSWORD"),
                postgres_db=os.environ.get("POSTGRES_DB"),
                postgres_host=os.environ.get("POSTGRES_HOST"),
                postgres_port=os.environ.get("POSTGRES_PORT"),
            )
            # Make the custom script we just made executable, as it's run by cron.
            subprocess.run(
                ["chmod", "0755", "/conf/run_pg_exporter.sh"], stdout=subprocess.PIPE
            ).stdout.decode("utf-8")

        if enable_coturn is True:
            convert(
                "/conf/turnserver.conf.j2",
                "/conf/turnserver.conf",
                server_name=environ["SYNAPSE_SERVER_NAME"],
                coturn_secret=environ["SYNAPSE_TURN_SECRET"],
                min_port=environ["COTURN_MIN_PORT"],
                max_port=environ["COTURN_MAX_PORT"],
                internal_ip=environ["COTURN_INTERNAL_IP"],
                external_ip=environ["COTURN_EXTERNAL_IP"],
                enable_coturn_metrics=environ["COTURN_METRICS"],
            )
        # Always regenerate all other config files
        generate_worker_files(environ, config_path, data_dir)

        # Mark workers as being configured
        with open(mark_filepath, "w") as f:
            f.write("")

    # Lifted right out of start.py
    jemallocpath = "/usr/lib/%s-linux-gnu/libjemalloc.so.2" % (platform.machine(),)

    if os.path.isfile(jemallocpath):
        environ["LD_PRELOAD"] = jemallocpath
    else:
        log("Could not find %s, will not use" % (jemallocpath,))

    # Start supervisord, which will start Synapse, all of the configured worker
    # processes, redis, nginx etc. according to the config we created above.
    log("Starting supervisord")
    flush_buffers()
    os.execle(
        "/usr/local/bin/supervisord",
        "supervisord",
        "-c",
        "/etc/supervisor/supervisord.conf",
        environ,
    )


if __name__ == "__main__":
    main(sys.argv, os.environ)
