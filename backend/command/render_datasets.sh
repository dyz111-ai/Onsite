#!/bin/bash

# Get task ID (no spaces around = in shell variables)
RENDER_ID=$1

# Local file paths
LOCAL_DESTINATION_PATH="../cache/destination/$RENDER_ID.json"
LOCAL_XOSC_PATH="../cache/OpenSCENARIO/$RENDER_ID.xosc"

# Server information
SERVER_USER="root"
SERVER_HOST="connect.cqa1.seetacloud.com"
SERVER_PORT="19567"
REMOTE_CACHE_DIR="/root/autodl-tmp/cache"

# Validate task ID
if [ -z "$RENDER_ID" ]; then
    echo "Error: No task ID provided"
    echo "Usage: $0 <task_id>"
    exit 1
fi

# Check if local files exist
if [ ! -f "$LOCAL_DESTINATION_PATH" ]; then
    echo "Error: DESTINATION file not found at $LOCAL_DESTINATION_PATH"
    exit 1
fi

if [ ! -f "$LOCAL_XOSC_PATH" ]; then
    echo "Error: XOSC file not found at $LOCAL_XOSC_PATH"
    exit 1
fi

# Create remote directories if they don't exist
echo "Creating remote directories on file server..."
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST "mkdir -p $REMOTE_CACHE_DIR/destination && mkdir -p $REMOTE_CACHE_DIR/OpenSCENARIO"

# Upload DESTINATION file to file server
echo "Uploading DESTINATION file to $SERVER_HOST:$SERVER_PORT..."
scp -P $SERVER_PORT $LOCAL_DESTINATION_PATH $SERVER_USER@$SERVER_HOST:$REMOTE_CACHE_DIR/destination/$RENDER_ID.json
if [ $? -ne 0 ]; then
    echo "Failed to upload DESTINATION file"
    exit 1
fi

# Upload XOSC file to file server
echo "Uploading XOSC file to $SERVER_HOST:$SERVER_PORT..."
scp -P $SERVER_PORT $LOCAL_XOSC_PATH $SERVER_USER@$SERVER_HOST:$REMOTE_CACHE_DIR/OpenSCENARIO/$RENDER_ID.xosc
if [ $? -ne 0 ]; then
    echo "Failed to upload XOSC file"
    exit 1
fi

# Start render task on render server
echo "Starting render task on $SERVER_HOST:$SERVER_PORT..."
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST "bash /root/autodl-tmp/carla_data_collect/scripts/main.sh $RENDER_ID"
if [ $? -ne 0 ]; then
    echo "Failed to start render task"
    exit 1
fi

echo "Render task started successfully with ID: $RENDER_ID"
exit 0