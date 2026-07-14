# ========================================================================
#    CHROME DISABLE SELF-XSS (ALLOW PASTING) FOR ALL PROFILES
# ========================================================================
# Yêu cầu chạy bằng quyền Administrator (Run as Administrator)
# ========================================================================

# 1. Kiểm tra quyền Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "Ban phai chay script nay bang quyen Administrator (Run as Administrator)!"
    Exit
}

# 2. Tắt tất cả tiến trình Google Chrome đang hoạt động để mở khóa tệp tin Preferences
$chromeProcesses = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
if ($chromeProcesses) {
    Write-Host "Dang dong Google Chrome de mo khoa cac tep tin Preferences..." -ForegroundColor Yellow
    Stop-Process -Name "chrome" -Force
    Start-Sleep -Seconds 2
}
else {
    Write-Host "Google Chrome khong chay. Bat dau cau hinh..." -ForegroundColor Green
}

# 3. Định vị đường dẫn thư mục User Data của Chrome
$UserDataPath = "$env:LOCALAPPDATA\Google\Chrome\User Data"

if (Test-Path $UserDataPath) {
    # Quét tất cả thư mục Profile có chứa tệp tin "Preferences"
    $Profiles = Get-ChildItem -Path $UserDataPath -Directory | Where-Object { 
        Test-Path (Join-Path $_.FullName "Preferences") 
    }

    foreach ($Profile in $Profiles) {
        Write-Host "-> Dang cau hinh cho Profile: $($Profile.Name)..." -ForegroundColor Cyan
        $PrefFile = Join-Path $Profile.FullName "Preferences"

        try {
            # Đọc nội dung file JSON gốc (sử dụng -Raw để lấy toàn bộ chuỗi)
            $JSON = Get-Content -Path $PrefFile -Raw -Encoding UTF8 | ConvertFrom-Json

            # Khởi tạo nhánh devtools.preferences nếu chưa tồn tại
            if (-not $JSON.devtools) {
                $JSON | Add-Member -MemberType NoteProperty -Name "devtools" -Value ([PSCustomObject]@{ preferences = [PSCustomObject]@{} })
            }
            elseif (-not $JSON.devtools.preferences) {
                $JSON.devtools | Add-Member -MemberType NoteProperty -Name "preferences" -Value ([PSCustomObject]@{})
            }

            # Chèn thuộc tính tắt cảnh báo Self-XSS (bắt buộc lưu ở dạng chuỗi "true")
            if (-not $JSON.devtools.preferences.PSObject.Properties['disable-self-xss-warning']) {
                $JSON.devtools.preferences | Add-Member -MemberType NoteProperty -Name "disable-self-xss-warning" -Value "true" -Force
            }
            else {
                $JSON.devtools.preferences.'disable-self-xss-warning' = "true"
            }

            # Chuyển đổi ngược lại JSON với Depth tối đa (100) để bảo toàn cấu trúc tệp của Chrome
            $NewJSON = ConvertTo-Json $JSON -Depth 100 -Compress

            # Ghi đè file Preferences dưới dạng UTF-8 không có BOM (tránh làm lỗi parser của Chrome)
            [System.IO.File]::WriteAllText($PrefFile, $NewJSON, [System.Text.Encoding]::UTF8)

            Write-Host "   [SUCCESS] Da bypass yeu cau 'allow pasting' tren console F12!" -ForegroundColor Green
        }
        catch {
            Write-Host "   [ERROR] Khong the xử ly file Preferences cho profile nay: $_" -ForegroundColor Red
        }
    }
}
else {
    Write-Host "[WARNING] Khong tim thay thu muc User Data mac dinh cua Google Chrome." -ForegroundColor Yellow
}

Write-Host "`n========================================================================" -ForegroundColor Green
Write-Host " HOAN TAT! Ban co the khoi dong lai Chrome va paste code vao F12 Console." -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green