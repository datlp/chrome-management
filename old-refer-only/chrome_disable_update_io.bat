@echo off
setlocal EnableDelayedExpansion

echo ========================================================================
echo CHROME CONFIGURATION SCRIPT (YEU CAU QUYEN ADMINISTRATOR)
echo 1. Vo hieu hoa he thong cap nhat Google Omaha (Giu Chrome ^<= 149)
echo 2. Bat buoc duy tri kien truc Manifest V2
echo 3. Tu dong bat danh sach cac tien ich mo rong (Extensions)
echo ========================================================================

echo.
echo [1/4] Dang cau hinh Registry de chan cap nhat Chrome...
reg add "HKLM\SOFTWARE\Policies\Google\Update" /v UpdateDefault /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Google\Update" /v AutoUpdateCheckPeriodMinutes /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Google\Update" /v DisableAutoUpdateChecksCheckboxValue /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Google\Update" /v Update{8A69D345-D564-463C-AFF1-A69D9E530F96} /t REG_DWORD /d 0 /f >nul 2>&1

echo.
echo [2/4] Dang vo hieu hoa Update Services va Scheduled Tasks...
sc stop gupdate >nul 2>&1
sc config gupdate start= disabled >nul 2>&1
sc stop gupdatem >nul 2>&1
sc config gupdatem start= disabled >nul 2>&1

schtasks /change /tn "\GoogleUpdateTaskMachineCore" /disable >nul 2>&1
schtasks /change /tn "\GoogleUpdateTaskMachineUA" /disable >nul 2>&1

echo.
echo [3/4] Dang mo khoa ho tro Manifest V2...
reg add "HKLM\SOFTWARE\Policies\Google\Chrome" /v ExtensionManifestV2Availability /t REG_DWORD /d 2 /f >nul 2>&1

echo.
echo [4/4] Dang ep buoc tai va tu dong bat toan bo Extension trong danh sach...

:: Thay the cac chuoi ID duoi day bang danh sach ma ID (32 ky tu) cac tien ich cua ban.
:: Moi ID duoc cach nhau boi 1 khoang trang (dau cach).
set "EXT_LIST=lhobafahddgcelffkeicbaginigeejlf hnojoemndpdjofcdaonbefcfecpjfflh blpfhbolaobkkaalciociiglbefpglaf eimadpbcbfnmbkopoojfekhnkhdbieeh lmilalhkkdhfieeienjbiicclobibjao oifijhaokejakekmnjmphonojcfkpbbh jnofiabkigekemighcdaejlpgdhmbaog micdllihgoppmejpecmkilggmaagfdmb ddkjiahejlhfcafbddmgiahcphecmpfh"

set /a count=1
for %%i in (%EXT_LIST%) do (
    echo - Dang cau hinh de tu dong bat ID: %%i
    :: Dua vao Whitelist de chan canh bao Developer Mode
    reg add "HKLM\Software\Policies\Google\Chrome\ExtensionInstallWhitelist" /v "!count!" /t REG_SZ /d "%%i" /f >nul 2>&1
    :: Ep buoc luon kich hoat o trang thai ENABLED
    reg add "HKLM\SOFTWARE\Policies\Google\Chrome\ExtensionInstallForcelist" /v "!count!" /t REG_SZ /d "%%i;https://clients2.google.com/service/update2/crx" /f >nul 2>&1
    set /a count+=1
)

echo.
echo ========================================================================
echo HOAN TAT CAU HINH. Vui long khoi dong lai Google Chrome.
echo ========================================================================
pause