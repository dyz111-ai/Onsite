
RENDER_ID=$1

# Server information
SERVER_USER="root"
SERVER_HOST="connect.cqa1.seetacloud.com"
SERVER_PORT="19567"
REMOTE_CACHE_DIR="/root/autodl-tmp/cache"

# generate video
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST "/root/autodl-tmp/carla_data_collect/scripts/generate_video.sh $RENDER_ID"

# transmit video to local
REMOTE_VIDEO_FILE="/root/autodl-tmp/cache/video/${RENDER_ID}.mp4"
LOCAL_VIDEO_PATH="../cache/video/"

scp -P $SERVER_PORT $SERVER_USER@$SERVER_HOST:$REMOTE_VIDEO_FILE $LOCAL_VIDEO_PATH
