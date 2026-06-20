@echo off
setlocal EnableDelayedExpansion

echo ========================================================================
echo CHROME CONFIGURATION SCRIPT (YEU CAU QUYEN ADMINISTRATOR)
echo Bat buoc duy tri kien truc Manifest V2 va tu dong bat Extensions
echo ========================================================================

echo.
echo Dang mo khoa ho tro Manifest V2...
reg add "HKLM\SOFTWARE\Policies\Google\Chrome" /v ExtensionManifestV2Availability /t REG_DWORD /d 2 /f >nul 2>&1

echo.
echo Dang ep buoc tai va tu dong bat toan bo Extension trong danh sach...

:: Thay the cac chuoi ID duoi day bang danh sach ma ID (32 ky tu) cac tien ich cua ban.
:: Moi ID duoc cach nhau boi 1 khoang trang (dau cach).
set "EXT_LIST=ghbmnnjooekpmoecnnnilnnbdlolhkhi lmjegmlicamnimmfhcmpkclmigmmcbeh mnjggcdmjocbbbhaepdhchncahnbgone lhobafahddgcelffkeicbaginigeejlf hnojoemndpdjofcdaonbefcfecpjfflh blpfhbolaobkkaalciociiglbefpglaf eimadpbcbfnmbkopoojfekhnkhdbieeh lmilalhkkdhfieeienjbiicclobibjao oifijhaokejakekmnjmphonojcfkpbbh jnofiabkigekemighcdaejlpgdhmbaog micdllihgoppmejpecmkilggmaagfdmb ddkjiahejlhfcafbddmgiahcphecmpfh"

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
echo HOAN TAT CAU HINH EXTENSIONS. Vui long khoi dong lai Google Chrome.
echo ========================================================================
pause