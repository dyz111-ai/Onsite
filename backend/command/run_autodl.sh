#!/bin/bash

TRAINING_ID=$1

if [ -z "$TRAINING_ID" ]; then
    echo "[ERROR] No training_id provided!"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULT_DIR="$SCRIPT_DIR/../../cache/train"
TEMP_DIR="$SCRIPT_DIR/temp"

mkdir -p "$RESULT_DIR"
mkdir -p "$TEMP_DIR"

# 使用training_id作为临时文件名，避免冲突
TEMP1="$TEMP_DIR/gpu_${TRAINING_ID}_1.txt"
TEMP2="$TEMP_DIR/gpu_${TRAINING_ID}_2.txt"
TEMP_PROC1="$TEMP_DIR/proc_${TRAINING_ID}_1.txt"
TEMP_PROC2="$TEMP_DIR/proc_${TRAINING_ID}_2.txt"

# 服务器配置
SERVER1_PORT=44939
SERVER2_PORT=19567
SERVER_HOST="connect.cqa1.seetacloud.com"
SERVER_USER="root"
SERVER_PASSWORD="ZjDV3iDiZMNV"
SERVER_PATH="/root/autodl-tmp/docker-monitor"
GPU_THRESHOLD=15000

echo "=== Checking available servers ==="

# 检查服务器1
echo "Checking Server 1 (port $SERVER1_PORT)..."

# 先检查是否有训练进程在运行
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER1_PORT $SERVER_USER@$SERVER_HOST "ps aux | grep -E '(train\.py|torch\.distributed\.launch)' | grep -v grep | wc -l" > "$TEMP_PROC1" 2>/dev/null
if [ $? -eq 0 ]; then
    PROC_COUNT1=$(cat "$TEMP_PROC1")
    echo "Server 1 training processes: $PROC_COUNT1"
    
    if [ "$PROC_COUNT1" -eq 0 ]; then
        # 没有训练进程，检查显存
        sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER1_PORT $SERVER_USER@$SERVER_HOST "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1" > "$TEMP1" 2>/dev/null
        if [ $? -eq 0 ]; then
            GPU1=$(cat "$TEMP1")
            echo "Server 1 GPU free: $GPU1 MB"
            if [ "$GPU1" -gt "$GPU_THRESHOLD" ]; then
                SELECTED_PORT=$SERVER1_PORT
                # 清理临时文件
                rm -f "$TEMP_PROC1" "$TEMP1" 2>/dev/null
                # 跳转到运行部分
                echo "Using server port: $SELECTED_PORT"
                sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SELECTED_PORT $SERVER_USER@$SERVER_HOST "bash $SERVER_PATH/main-zyd.sh train$TRAINING_ID"
                if [ $? -ne 0 ]; then
                    exit 1
                fi
                
                sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no -r -P $SELECTED_PORT $SERVER_USER@$SERVER_HOST:$SERVER_PATH/runs/train$TRAINING_ID "$RESULT_DIR"
                if [ $? -ne 0 ]; then
                    exit 2
                fi
                
                # 清理可能遗留的临时文件
                rm -f "$TEMP_DIR"/*_${TRAINING_ID}_*.txt 2>/dev/null
                
                exit 0
            fi
            rm -f "$TEMP1" 2>/dev/null
        else
            echo "Server 1 GPU check failed"
        fi
    else
        echo "Server 1 has $PROC_COUNT1 training jobs running, skipping..."
    fi
    rm -f "$TEMP_PROC1" 2>/dev/null
else
    echo "Server 1 unavailable"
    rm -f "$TEMP_PROC1" 2>/dev/null
fi

# 检查服务器2
echo "Checking Server 2 (port $SERVER2_PORT)..."

# 先检查是否有训练进程在运行
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER2_PORT $SERVER_USER@$SERVER_HOST "ps aux | grep -E '(train\.py|torch\.distributed\.launch)' | grep -v grep | wc -l" > "$TEMP_PROC2" 2>/dev/null
if [ $? -eq 0 ]; then
    PROC_COUNT2=$(cat "$TEMP_PROC2")
    echo "Server 2 training processes: $PROC_COUNT2"
    
    if [ "$PROC_COUNT2" -eq 0 ]; then
        # 没有训练进程，检查显存
        sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER2_PORT $SERVER_USER@$SERVER_HOST "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1" > "$TEMP2" 2>/dev/null
        if [ $? -eq 0 ]; then
            GPU2=$(cat "$TEMP2")
            echo "Server 2 GPU free: $GPU2 MB"
            if [ "$GPU2" -gt "$GPU_THRESHOLD" ]; then
                SELECTED_PORT=$SERVER2_PORT
                # 清理临时文件
                rm -f "$TEMP_PROC2" "$TEMP2" 2>/dev/null
                # 跳转到运行部分
                echo "Using server port: $SELECTED_PORT"
                sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SELECTED_PORT $SERVER_USER@$SERVER_HOST "bash $SERVER_PATH/main-zyd.sh train$TRAINING_ID"
                if [ $? -ne 0 ]; then
                    exit 1
                fi
                
                sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no -r -P $SELECTED_PORT $SERVER_USER@$SERVER_HOST:$SERVER_PATH/runs/train$TRAINING_ID "$RESULT_DIR"
                if [ $? -ne 0 ]; then
                    exit 2
                fi
                
                # 清理可能遗留的临时文件
                rm -f "$TEMP_DIR"/*_${TRAINING_ID}_*.txt 2>/dev/null
                
                exit 0
            fi
            rm -f "$TEMP2" 2>/dev/null
        else
            echo "Server 2 GPU check failed"
        fi
    else
        echo "Server 2 has $PROC_COUNT2 training jobs running, skipping..."
    fi
    rm -f "$TEMP_PROC2" 2>/dev/null
else
    echo "Server 2 unavailable"
    rm -f "$TEMP_PROC2" 2>/dev/null
fi

echo "[ERROR] 暂无可用服务器"
exit 3
