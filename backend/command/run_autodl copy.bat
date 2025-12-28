@echo off
chcp 65001 >nul

REM 获取当前脚本所在目录
set SCRIPT_DIR=%~dp0
REM 设置结果目录为项目根目录下的 cache（backend 的上级目录）
set RESULT_DIR=%SCRIPT_DIR%..\..\cache\train



echo ==== DEBUG START ====
whoami
echo USERPROFILE=%USERPROFILE%
echo SCRIPT_DIR=%SCRIPT_DIR%
echo RESULT_DIR=%RESULT_DIR%
echo ==== DEBUG END ====

echo === Step 1: Execute remote script ===
ssh -p 19567 root@connect.cqa1.seetacloud.com "bash /root/autodl-tmp/docker-monitor/main-zyd.sh train02"

if errorlevel 1 (
    echo Remote script execution failed
    exit /b 1
)

echo.
echo === Step 2: Download train02 folder ===

scp -r -P 19567 root@connect.cqa1.seetacloud.com:/root/autodl-tmp/docker-monitor/runs/train02 "%RESULT_DIR%"

if errorlevel 1 (
    echo train02 folder download failed
    exit /b 2
)


exit /b 0

