#!/bin/bash

TASK=RENDER
RENDER_ID=$1

# Parameter validation
if [ -z "$RENDER_ID" ]; then
    echo "Error: RENDER_ID parameter is required"
    echo "Usage: ./transmit_datasets.sh <render_id>"
    exit 1
fi

# Create local target directory
mkdir -p "../frontend/cache/render/dataset/$RENDER_ID"

# 1. Create compressed package on remote server
echo "Creating compressed package on remote server..."
ssh -p 19567 root@connect.cqa1.seetacloud.com << EOF
cd /root/autodl-tmp/cache/render/dataset || exit 1
tar -czf $RENDER_ID.tar.gz $RENDER_ID
if [ \$? -ne 0 ]; then
    echo "Compression failed on remote server"
    rm -f $RENDER_ID.tar.gz
    exit 1
fi
EOF

# Check if compression succeeded
if [ $? -ne 0 ]; then
    echo "Error: Remote compression failed"
    exit 1
fi

# 2. Transfer the compressed package to local
echo "Transferring compressed package to local..."
scp -P 19567 root@connect.cqa1.seetacloud.com:/root/autodl-tmp/cache/render/dataset/$RENDER_ID.tar.gz "../frontend/cache/render/dataset/"

# Check transfer success
if [ $? -ne 0 ]; then
    echo "Error: Package transfer failed"
    # Clean up remote package
    ssh -p 19567 root@connect.cqa1.seetacloud.com "rm -f /root/autodl-tmp/cache/render/dataset/$RENDER_ID.tar.gz"
    exit 1
fi

# 3. Extract locally and clean up
echo "Extracting package locally..."
tar -xzf "../frontend/cache/render/dataset/$RENDER_ID.tar.gz" -C "../frontend/cache/render/dataset/$RENDER_ID" --strip-components=1
# rm -f "../frontend/cache/render/dataset/$RENDER_ID.tar.gz"

# 4. Clean up remote package
ssh -p 19567 root@connect.cqa1.seetacloud.com "rm -f /root/autodl-tmp/cache/render/dataset/$RENDER_ID.tar.gz"

echo "Dataset $RENDER_ID has been successfully transferred to ../frontend/cache/render/dataset/$RENDER_ID"