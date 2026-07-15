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

echo Google Translate & set "EXT_LIST=!EXT_LIST! aapbdbdomjkkjkaonfhkkikfgjllcleb"
echo Just Black & set "EXT_LIST=!EXT_LIST! aghfnjkcakhmadgdomlmlhhaocbkloab"
echo JSON Formatter & set "EXT_LIST=!EXT_LIST! bcjindcccaagfpapjjmafapmmgkkhgoa"
echo Copy link text & set "EXT_LIST=!EXT_LIST! blpfhbolaobkkaalciociiglbefpglaf"
echo HttpWatch: HTTP Debugger & set "EXT_LIST=!EXT_LIST! dajhhgiioackgdldomhppobgjbinhimh"
echo uBlock Origin Lite & set "EXT_LIST=!EXT_LIST! ddkjiahejlhfcafbddmgiahcphecmpfh"
echo Save Page WE & set "EXT_LIST=!EXT_LIST! dhhpefjklgkmgeafimnjhojgjamoafof"
echo Dark Reader & set "EXT_LIST=!EXT_LIST! eimadpbcbfnmbkopoojfekhnkhdbieeh"
echo Volume Booster & set "EXT_LIST=!EXT_LIST! ejkiikneibegknkgimmihdpcbcedgmpo"
echo Google Analytics Opt-out Add-on (by Google) & set "EXT_LIST=!EXT_LIST! fllaojicojecljbmefodhfapmkghcbnh"
echo React Developer Tools & set "EXT_LIST=!EXT_LIST! fmkadmapgofadopljbjfkapdkoienihi"
echo Google Docs Offline & set "EXT_LIST=!EXT_LIST! ghbmnnjooekpmoecnnnilnnbdlolhkhi"
echo AdBlock — block ads across the web & set "EXT_LIST=!EXT_LIST! gighmmpiobklfepjocnamgkkbiglidom"
echo IE Tab & set "EXT_LIST=!EXT_LIST! hehijbfgiekmjfkfjpbkbammjbdenadd"
echo Picture-in-Picture Extension (by Google) & set "EXT_LIST=!EXT_LIST! hkgfoiooedgoejojocmhlaklaeopbecg"
echo Allow CSP: Content-Security-Policy & set "EXT_LIST=!EXT_LIST! hnojoemndpdjofcdaonbefcfecpjfflh"
echo TimeTags for YouTube & set "EXT_LIST=!EXT_LIST! hpbmedimnlknflpbgfbllklgelbnelef"
echo Chrome Remote Desktop & set "EXT_LIST=!EXT_LIST! inomeogfingihgjfjlpeplalcfajhgai"
echo Simple Auto HD (Open Source) & set "EXT_LIST=!EXT_LIST! jnofiabkigekemighcdaejlpgdhmbaog"
echo Google Apps Script GitHub Assistant & set "EXT_LIST=!EXT_LIST! lfjcgcmkmjjlieihflfhjopckgpelofo"
echo Allow CORS: Access-Control-Allow-Origin & set "EXT_LIST=!EXT_LIST! lhobafahddgcelffkeicbaginigeejlf"
echo Run Javascript & set "EXT_LIST=!EXT_LIST! lmilalhkkdhfieeienjbiicclobibjao"
echo Application Launcher For Drive (by Google) & set "EXT_LIST=!EXT_LIST! lmjegmlicamnimmfhcmpkclmigmmcbeh"
echo Google Keep Chrome Extension & set "EXT_LIST=!EXT_LIST! lpcaedmchfhocbbapmcbpinfpgnhiddi"
echo Google Dictionary (by Google) & set "EXT_LIST=!EXT_LIST! mgijmajocgfcbeboacabfgobmjgjcoja"
echo Tab Copy & set "EXT_LIST=!EXT_LIST! micdllihgoppmejpecmkilggmaagfdmb"
echo SponsorBlock for YouTube - Skip Sponsorships & set "EXT_LIST=!EXT_LIST! mnjggcdmjocbbbhaepdhchncahnbgone"
echo IDM Integration Module & set "EXT_LIST=!EXT_LIST! ngpampappnmepgilojfohadhhmbhlaek"
echo Chrome Web Store Payments & set "EXT_LIST=!EXT_LIST! nmmhkkegccagdldgiimedpiccmgmieda"
echo Open Multiple URLs & set "EXT_LIST=!EXT_LIST! oifijhaokejakekmnjmphonojcfkpbbh"
echo Gmail Dark Mode & set "EXT_LIST=!EXT_LIST! pmdghmdjjojjeajflmpgnambocpnpiea"


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