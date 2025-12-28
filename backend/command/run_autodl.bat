@echo off
chcp 65001 >nul
set RESULT_DIR=D:\autodl_results\train

echo ==== DEBUG START ====
whoami
echo USERPROFILE=%USERPROFILE%
echo ==== DEBUG END ====

echo === Step 1: Execute remote script ===
ssh -p 27100 root@connect.nma1.seetacloud.com "bash /root/autodl-tmp/docker-monitor/main-zyd.sh"

if errorlevel 1 (
    echo Remote script execution failed
    exit /b 1
)

echo.
echo === Step 2: Download CSV file ===

scp -P 27100 root@connect.nma1.seetacloud.com:/root/autodl-tmp/docker-monitor/resource_usage.csv %RESULT_DIR%\

if errorlevel 1 (
    echo CSV file download failed
    exit /b 2
)

echo.
echo Success! CSV saved to %RESULT_DIR%\resource_usage.csv
exit /b 0
