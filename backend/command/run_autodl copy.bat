@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

set TRAINING_ID=%1

if "%TRAINING_ID%"=="" (
    echo [ERROR] No training_id provided!
    exit /b 1
)

set SCRIPT_DIR=%~dp0
set RESULT_DIR=%SCRIPT_DIR%..\..\cache\train
set TEMP_DIR=%SCRIPT_DIR%temp

if not exist "%RESULT_DIR%" mkdir "%RESULT_DIR%"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM 使用training_id作为临时文件名，避免冲突
set TEMP1=%TEMP_DIR%\gpu_%TRAINING_ID%_1.txt
set TEMP2=%TEMP_DIR%\gpu_%TRAINING_ID%_2.txt
set TEMP_PROC1=%TEMP_DIR%\proc_%TRAINING_ID%_1.txt
set TEMP_PROC2=%TEMP_DIR%\proc_%TRAINING_ID%_2.txt

REM 服务器配置
set SERVER1_PORT=44939
set SERVER2_PORT=19567
set SERVER_HOST=connect.cqa1.seetacloud.com
set SERVER_USER=root
set SERVER_PATH=/root/autodl-tmp/docker-monitor
set GPU_THRESHOLD=15000

echo === Checking available servers ===

REM 检查服务器1
echo Checking Server 1 (port %SERVER1_PORT%)...

REM 先检查是否有训练进程在运行
ssh -p %SERVER1_PORT% %SERVER_USER%@%SERVER_HOST% "ps aux | grep -E '(train\.py|torch\.distributed\.launch)' | grep -v grep | wc -l" > "%TEMP_PROC1%" 2>nul
if %errorlevel% equ 0 (
    set /p PROC_COUNT1=<"%TEMP_PROC1%"
    echo Server 1 training processes: !PROC_COUNT1!
    
    if !PROC_COUNT1! EQU 0 (
        REM 没有训练进程，检查显存
        ssh -p %SERVER1_PORT% %SERVER_USER%@%SERVER_HOST% "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1" > "%TEMP1%" 2>nul
        if %errorlevel% equ 0 (
            set /p GPU1=<"%TEMP1%"
            echo Server 1 GPU free: !GPU1! MB
            if !GPU1! GTR %GPU_THRESHOLD% (
                set SELECTED_PORT=%SERVER1_PORT%
                REM 清理临时文件
                if exist "%TEMP_PROC1%" del "%TEMP_PROC1%" 2>nul
                if exist "%TEMP1%" del "%TEMP1%" 2>nul
                goto :run
            )
            if exist "%TEMP1%" del "%TEMP1%" 2>nul
        ) else (
            echo Server 1 GPU check failed
        )
    ) else (
        echo Server 1 has !PROC_COUNT1! training jobs running, skipping...
    )
    if exist "%TEMP_PROC1%" del "%TEMP_PROC1%" 2>nul
) else (
    echo Server 1 unavailable
    if exist "%TEMP_PROC1%" del "%TEMP_PROC1%" 2>nul
)

REM 检查服务器2
echo Checking Server 2 (port %SERVER2_PORT%)...

REM 先检查是否有训练进程在运行
ssh -p %SERVER2_PORT% %SERVER_USER%@%SERVER_HOST% "ps aux | grep -E '(train\.py|torch\.distributed\.launch)' | grep -v grep | wc -l" > "%TEMP_PROC2%" 2>nul
if %errorlevel% equ 0 (
    set /p PROC_COUNT2=<"%TEMP_PROC2%"
    echo Server 2 training processes: !PROC_COUNT2!
    
    if !PROC_COUNT2! EQU 0 (
        REM 没有训练进程，检查显存
        ssh -p %SERVER2_PORT% %SERVER_USER%@%SERVER_HOST% "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n 1" > "%TEMP2%" 2>nul
        if %errorlevel% equ 0 (
            set /p GPU2=<"%TEMP2%"
            echo Server 2 GPU free: !GPU2! MB
            if !GPU2! GTR %GPU_THRESHOLD% (
                set SELECTED_PORT=%SERVER2_PORT%
                REM 清理临时文件
                if exist "%TEMP_PROC2%" del "%TEMP_PROC2%" 2>nul
                if exist "%TEMP2%" del "%TEMP2%" 2>nul
                goto :run
            )
            if exist "%TEMP2%" del "%TEMP2%" 2>nul
        ) else (
            echo Server 2 GPU check failed
        )
    ) else (
        echo Server 2 has !PROC_COUNT2! training jobs running, skipping...
    )
    if exist "%TEMP_PROC2%" del "%TEMP_PROC2%" 2>nul
) else (
    echo Server 2 unavailable
    if exist "%TEMP_PROC2%" del "%TEMP_PROC2%" 2>nul
)

echo [ERROR] 暂无可用服务器
exit /b 3

:run
echo Using server port: %SELECTED_PORT%
ssh -p %SELECTED_PORT% %SERVER_USER%@%SERVER_HOST% bash %SERVER_PATH%/main-zyd.sh train%TRAINING_ID%
if errorlevel 1 exit /b 1

scp -r -P %SELECTED_PORT% %SERVER_USER%@%SERVER_HOST%:%SERVER_PATH%/runs/train%TRAINING_ID% "%RESULT_DIR%"
if errorlevel 1 exit /b 2

REM 清理可能遗留的临时文件
if exist "%TEMP_DIR%\*_%TRAINING_ID%_*.txt" del "%TEMP_DIR%\*_%TRAINING_ID%_*.txt" 2>nul

exit /b 0