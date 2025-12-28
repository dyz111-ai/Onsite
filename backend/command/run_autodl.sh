#!/bin/bash

RESULT_DIR="/mnt/autodl_results/train"

echo "==== DEBUG START ===="
whoami
echo "USER=$USER"
echo "HOME=$HOME"
echo "==== DEBUG END ===="

echo "=== Step 1: Execute remote script ==="
ssh -p 27100 root@connect.nma1.seetacloud.com "bash /root/autodl-tmp/docker-monitor/main-zyd.sh"

if [ $? -ne 0 ]; then
    echo "Remote script execution failed"
    exit 1
fi

echo ""
echo "=== Step 2: Download CSV file ==="

scp -P 27100 root@connect.nma1.seetacloud.com:/root/autodl-tmp/docker-monitor/resource_usage.csv "$RESULT_DIR/"

if [ $? -ne 0 ]; then
    echo "CSV file download failed"
    exit 2
fi

echo ""
echo "Success! CSV saved to $RESULT_DIR/resource_usage.csv"
exit 0