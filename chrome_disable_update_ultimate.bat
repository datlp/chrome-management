@echo off
setlocal EnableDelayedExpansion

echo ========================================================================
echo CHROME CONFIGURATION SCRIPT (YEU CAU QUYEN ADMINISTRATOR)
echo Vo hieu hoa he thong cap nhat Google Omaha (Giu Chrome ^<= 149)
echo ========================================================================

echo.
echo Dang cau hinh Registry de chan cap nhat Chrome...
reg add "HKLM\SOFTWARE\Policies\Google\Update" /v UpdateDefault /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Google\Update" /v AutoUpdateCheckPeriodMinutes /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Google\Update" /v DisableAutoUpdateChecksCheckboxValue /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Google\Update" /v Update{8A69D345-D564-463C-AFF1-A69D9E530F96} /t REG_DWORD /d 0 /f >nul 2>&1

echo.
echo Dang vo hieu hoa Update Services va Scheduled Tasks...
sc stop gupdate >nul 2>&1
sc config gupdate start= disabled >nul 2>&1
sc stop gupdatem >nul 2>&1
sc config gupdatem start= disabled >nul 2>&1

schtasks /change /tn "\GoogleUpdateTaskMachineCore" /disable >nul 2>&1
schtasks /change /tn "\GoogleUpdateTaskMachineUA" /disable >nul 2>&1

echo.
echo ========================================================================
echo HOAN TAT CAU HINH VO HIEU HOA CAP NHAT. Vui long khoi dong lai Google Chrome.
echo ========================================================================
pause