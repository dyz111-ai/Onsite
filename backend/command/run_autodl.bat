@echo off
chcp 65001 >nul

set TRAINING_ID=%1


if "%TRAINING_ID%"=="" (
    echo [ERROR] No training_id provided!
    exit /b 1
)

set TRAIN_FOLDER=train%TRAINING_ID%


set SCRIPT_DIR=%~dp0
set RESULT_DIR=%SCRIPT_DIR%..\..\cache\train

echo ==== DEBUG START ====
whoami
echo USERPROFILE=%USERPROFILE%
echo SCRIPT_DIR=%SCRIPT_DIR%
echo RESULT_DIR=%RESULT_DIR%
echo TRAINING_ID=%TRAINING_ID%
echo TRAIN_FOLDER=%TRAIN_FOLDER%
echo ==== DEBUG END ====

echo === Step 1: Execute remote script ===
ssh -p 19567 root@connect.cqa1.seetacloud.com bash /root/autodl-tmp/docker-monitor/main-zyd.sh train%TRAINING_ID%

if errorlevel 1 (
    echo Remote script execution failed
    exit /b 1
)

echo.
echo === Step 2: Download train%TRAINING_ID% folder ===

scp -r -P 19567 root@connect.cqa1.seetacloud.com:/root/autodl-tmp/docker-monitor/runs/train%TRAINING_ID% "%RESULT_DIR%"

if errorlevel 1 (
    echo train%TRAINING_ID% folder download failed
    exit /b 2
)

exit /b 0
