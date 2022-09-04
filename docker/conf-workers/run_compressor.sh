#!/bin/sh
synapse_auto_compressor -p postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB -c 500 -n 100

