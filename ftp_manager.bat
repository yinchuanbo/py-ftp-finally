@echo off
echo ============================
echo FTP File Upload Tool - Operation Menu
echo ============================
echo.
echo Please select environment:
echo [1] Test Environment
echo [2] Production Environment
echo [0] Exit
echo.
set /p env_choice=Enter your choice: 

if "%env_choice%"=="0" goto :end
if "%env_choice%"=="1" (
    set env=test
    set env_name=Test Environment
) else if "%env_choice%"=="2" (
    set env=pro
    set env_name=Production Environment
) else (
    echo Invalid choice, please run again
    goto :end
)

:operation_menu
cls
echo ============================
echo FTP File Upload Tool - %env_name%
echo ============================
echo.
echo Please select operation:
echo [1] Get File List
echo [2] Upload Files
echo [3] Get and Upload Files
echo [0] Back to Main Menu
echo.
set /p op_choice=Enter your choice: 

if "%op_choice%"=="0" goto :eof
if "%op_choice%"=="1" (
    echo Getting file list...
    python ftp_manager.py get %env%
    echo Done!
    pause
    goto :operation_menu
) else if "%op_choice%"=="2" (
    echo Starting file upload...
    python ftp_manager.py upload %env%
    echo Done!
    pause
    goto :operation_menu
) else if "%op_choice%"=="3" (
    echo Step 1: Getting file list...
    python ftp_manager.py get %env%
    echo.
    echo Step 2: Confirm upload files? (Y/N)
    set /p confirm=
    if /i "%confirm%"=="Y" (
        echo Starting file upload...
        python ftp_manager.py upload %env%
    ) else (
        echo Upload operation cancelled
    )
    echo Done!
    pause
    goto :operation_menu
) else (
    echo Invalid choice, please select again
    pause
    goto :operation_menu
)

:end
echo Thank you for using FTP File Upload Tool 