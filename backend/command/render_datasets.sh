#!/bin/bash

# Get task ID (no spaces around = in shell variables)
TASK=$1
RENDER_ID=$2

# Validate task parameter
if [ -z "$TASK" ]; then
    echo "Error: No task type provided"
    echo "Usage: $0 <task_type> <task_id>"
    echo "Valid task types: competition, render"
    exit 1
fi

# Validate task type is either "competition" or "render"
if [[ "$TASK" != "competition" && "$TASK" != "render" ]]; then
    echo "Error: Invalid task type '$TASK'"
    echo "Valid task types: competition, render"
    exit 1
fi

# Validate task ID
if [ -z "$RENDER_ID" ]; then
    echo "Error: No task ID provided"
    echo "Usage: $0 <task_id>"
    exit 1
fi

# Local file paths
LOCAL_CACHE_DIR="../frontend/cache/$TASK"
LOCAL_DESTINATION_PATH="$LOCAL_CACHE_DIR/destination/$RENDER_ID.json"
LOCAL_XOSC_PATH="$LOCAL_CACHE_DIR/OpenSCENARIO/$RENDER_ID.xosc"
LOCAL_VIDEO_PATH="$LOCAL_CACHE_DIR/video/$RENDER_ID.mp4"

# Server information
SERVER_USER="root"
SERVER_HOST="connect.cqa1.seetacloud.com"
SERVER_PORT="44939"
REMOTE_CACHE_DIR="/root/autodl-tmp/cache/$TASK"

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
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST "bash /root/autodl-tmp/carla_data_collect/scripts/main.sh $TASK $RENDER_ID"
if [ $? -ne 0 ]; then
    echo "Failed to start render task"
    # exit 1
fi

echo "Render task started successfully with ID: $RENDER_ID"

# generate video
echo "Generating video..."
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST "/root/autodl-tmp/carla_data_collect/scripts/generate_video.sh $TASK $RENDER_ID"

# transmit video to local
echo "Transmitting video to local..."
REMOTE_VIDEO_FILE="/root/autodl-tmp/cache/$TASK/video/${RENDER_ID}.mp4"
LOCAL_VIDEO_PATH="../frontend/cache/$TASK/video/"
mkdir -p $LOCAL_VIDEO_PATH
scp -P $SERVER_PORT $SERVER_USER@$SERVER_HOST:$REMOTE_VIDEO_FILE $LOCAL_VIDEO_PATH

exit 0