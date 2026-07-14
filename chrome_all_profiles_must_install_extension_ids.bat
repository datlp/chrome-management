@echo off
chcp 65001>nul
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

set "EXT_LIST="

echo Allow CORS: Access-Control-Allow-Origin & set "EXT_LIST=!EXT_LIST! lhobafahddgcelffkeicbaginigeejlf"
echo Allow CSP: Content-Security-Policy & set "EXT_LIST=!EXT_LIST! hnojoemndpdjofcdaonbefcfecpjfflh"
echo Application Launcher For Drive (by Google) & set "EXT_LIST=!EXT_LIST! lmjegmlicamnimmfhcmpkclmigmmcbeh"
echo Copy link text & set "EXT_LIST=!EXT_LIST! blpfhbolaobkkaalciociiglbefpglaf"
echo Dark Reader & set "EXT_LIST=!EXT_LIST! eimadpbcbfnmbkopoojfekhnkhdbieeh"
echo Google Docs Offline & set "EXT_LIST=!EXT_LIST! ghbmnnjooekpmoecnnnilnnbdlolhkhi"
echo HttpWatch: HTTP Debugger & set "EXT_LIST=!EXT_LIST! dajhhgiioackgdldomhppobgjbinhimh"
echo IDM Integration Module & set "EXT_LIST=!EXT_LIST! ngpampappnmepgilojfohadhhmbhlaek"
echo Just Black & set "EXT_LIST=!EXT_LIST! aghfnjkcakhmadgdomlmlhhaocbkloab"
echo Open Multiple URLs & set "EXT_LIST=!EXT_LIST! oifijhaokejakekmnjmphonojcfkpbbh"
echo Run Javascript & set "EXT_LIST=!EXT_LIST! lmilalhkkdhfieeienjbiicclobibjao"
echo Simple Auto HD (Open Source) & set "EXT_LIST=!EXT_LIST! jnofiabkigekemighcdaejlpgdhmbaog"
echo SponsorBlock for YouTube - Skip Sponsorships & set "EXT_LIST=!EXT_LIST! mnjggcdmjocbbbhaepdhchncahnbgone"
echo Tab Copy & set "EXT_LIST=!EXT_LIST! micdllihgoppmejpecmkilggmaagfdmb"
echo TimeTags for YouTube & set "EXT_LIST=!EXT_LIST! hpbmedimnlknflpbgfbllklgelbnelef"
echo uBlock Origin Lite & set "EXT_LIST=!EXT_LIST! ddkjiahejlhfcafbddmgiahcphecmpfh"
echo Immersive Translate & set "EXT_LIST=!EXT_LIST! bpoadfkcbjbfhfodiogcnhhhpibjhbnh"


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
echo HOAN TAT CAU HINH EXTENSIONS. Vui long khoi dong lai Google Chrome. (exit sau 5 giay)
echo ========================================================================
@REM sẽ thoát chương trình sau 5 giây
timeout /t 5 >nul