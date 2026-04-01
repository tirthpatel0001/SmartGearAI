@echo off
echo Starting MySQL file recovery process...

REM Stop MySQL service
echo Stopping MySQL service...
net stop MySQL
if %errorlevel% neq 0 (
    echo Failed to stop MySQL service
    exit /b 1
)

REM Delete existing .ibd files
echo Deleting existing .ibd files...
del /Q "C:\xampp\mysql\data\smartgearai\*.ibd"
if %errorlevel% neq 0 (
    echo Failed to delete .ibd files
    exit /b 1
)

REM Copy .ibd files from backup
echo Copying .ibd files from backup...
xcopy "C:\xampp\mysql\data_old\smartgearai\*.ibd" "C:\xampp\mysql\data\smartgearai\" /Y
if %errorlevel% neq 0 (
    echo Failed to copy .ibd files
    exit /b 1
)

REM Start MySQL service
echo Starting MySQL service...
net start MySQL
if %errorlevel% neq 0 (
    echo Failed to start MySQL service
    exit /b 1
)

echo MySQL file recovery completed successfully.
exit /b 0