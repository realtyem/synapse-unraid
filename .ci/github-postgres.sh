#!/bin/bash

set -e

psql -v ON_ERROR_STOP=1 --username "postgres" --dbname "postgres" <<-EOSQL
ALTER SYSTEM SET max_connections = '100';
ALTER SYSTEM SET shared_buffers = '1792MB';
ALTER SYSTEM SET effective_cache_size = '5376MB';
ALTER SYSTEM SET maintenance_work_mem = '448MB';
ALTER SYSTEM SET checkpoint_completion_target = '0.9';
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = '100';
ALTER SYSTEM SET random_page_cost = '1.1';
ALTER SYSTEM SET effective_io_concurrency = '200';
ALTER SYSTEM SET work_mem = '9175kB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';
EOSQL
