param(
  [switch]$SilentMap,
  [switch]$ForceStop
)

# Thêm thư viện WinForms và Drawing để vẽ giao diện trực quan
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 1. KIỂM TRA ĐIỀU KIỆN TIÊN QUYẾT (RCLONE)
if (-not (Get-Command rclone -ErrorAction SilentlyContinue)) {
  if (-not $SilentMap) {
    [System.Windows.Forms.MessageBox]::Show("Không tìm thấy lệnh 'rclone' trong Environment Variables!", "Lỗi Hệ Thống", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
  }
  return
}

# Khởi tạo đường dẫn đến file API_KEY.txt lưu cấu hình
$apiKeyPath = Join-Path $PSScriptRoot "API_KEY.txt"
$initialText = ""
if (Test-Path $apiKeyPath) {
  $initialText = Get-Content -Path $apiKeyPath -Raw
}

# 2. HÀM ĐĂNG KÝ KHỞI ĐỘNG CÙNG WINDOWS QUA FILE VBS (SILENT STARTUP) - ĐỌC ĐỘNG SCRIPT (NẾU DÙNG CLI)
function Register-StartupVBS {
  $startupFolder = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs\Startup")
  $vbsPath = Join-Path $startupFolder "MapRCloneDrives.vbs"
    
  # Xác định đường dẫn thực tế của script hiện tại
  $scriptPath = $PSCommandPath
  if (-not $scriptPath) {
    $scriptPath = Join-Path $PSScriptRoot "config.ps1"
  }
    
  # Nội dung file VBS chạy ẩn hoàn toàn PowerShell với tham số -SilentMap (cần file config.ps1 và API_KEY.txt)
  $vbsContent = @"
Dim WshShell
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File ""$scriptPath"" -SilentMap", 0, False
"@
  try {
    $vbsContent | Out-File -FilePath $vbsPath -Encoding ascii -Force
  }
  catch {
    # Bỏ qua nếu không có quyền ghi
  }
}

# 3. HÀM ĐĂNG KÝ KHỞI ĐỘNG HARDCODE - KHÔNG CẦN CHẠY LẠI SCRIPT & KHÔNG ĐỌC API_KEY.TXT KHI MỞ MÁY
function Register-StartupHardcoded {
  $startupFolder = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs\Startup")
  $vbsPath = Join-Path $startupFolder "MapRCloneDrives_GoogleDrive.vbs"
    
  # Đọc nhanh cấu hình hiện tại trong khung textbox hoặc file text
  if (-not (Test-Path $apiKeyPath)) {
    [System.Windows.Forms.MessageBox]::Show("Không tìm thấy dữ liệu cấu hình trong API_KEY.txt để thiết lập Hardcode!", "Lỗi", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    return
  }
    
  $lines = Get-Content -Path $apiKeyPath
  $vbsCommands = @()
  $mapCount = 0
    
  foreach ($line in $lines) {
    $trimmed = $line.Trim()
    if ([string]::IsNullOrEmpty($trimmed) -or $trimmed.StartsWith("#")) { continue }
        
    $parts = [regex]::Split($trimmed, '(?<=\")\s+(?=\")')
    if ($parts.Count -ge 5) {
      $driveLetter = $parts[0].Trim().Trim('"').ToUpper() + ":"
      $volName = $parts[1].Trim().Trim('"')
      $account = $parts[2].Trim().Trim('"')
      $remoteName = "google_drive_${account}"
            
      # Khử dấu nháy kép bên trong tên nhãn để tránh lỗi cú pháp trong VBScript
      $escapedVolName = $volName -replace '"', '""'
            
      # Sử dụng dấu nháy đơn trong PowerShell giúp kiểm soát chính xác cặp nháy kép kép (""Tên Ổ"") cho VBScript chạy ngầm
      $vbsLine = 'WshShell.Run "rclone mount ' + $remoteName + ': ' + $driveLetter + ' --vfs-cache-mode writes --network-mode --dir-cache-time 24h --links --volname ""' + $escapedVolName + '"" --log-level CRITICAL", 0, False'
            
      $vbsCommands += $vbsLine
      $mapCount++
    }
  }
    
  if ($mapCount -eq 0) {
    [System.Windows.Forms.MessageBox]::Show("Không tìm thấy cấu hình ổ đĩa hợp lệ trong API_KEY.txt để tạo file khởi động!", "Thông Báo", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
    return
  }
    
  # Gom nội dung file VBS tự tắt rclone cũ và bật danh sách ổ đĩa hardcoded mới lên
  $vbsHeader = @"
Dim WshShell
Set WshShell = CreateObject("WScript.Shell")
On Error Resume Next
WshShell.Run "taskkill /F /IM rclone.exe", 0, True
WScript.Sleep 2000
"@
  $vbsBody = $vbsCommands -join "`r`n"
  $fullVbsContent = $vbsHeader + "`r`n" + $vbsBody
    
  try {
    # Đảm bảo dọn sạch file startup động kiểu cũ để tránh xung đột
    $oldVbsPath = Join-Path $startupFolder "MapRCloneDrives.vbs"
    if (Test-Path $oldVbsPath) { Remove-Item -Path $oldVbsPath -Force -ErrorAction SilentlyContinue }
        
    $fullVbsContent | Out-File -FilePath $vbsPath -Encoding ascii -Force
    [System.Windows.Forms.MessageBox]::Show("Đăng ký khởi động cùng Windows thành công!`n`nĐã đóng gói cứng thông tin của $mapCount ổ đĩa trực tiếp vào file khởi động.`nTừ nay khi mở máy, ổ đĩa sẽ tự map ngầm không cần mở tool và hoàn toàn không phụ thuộc vào file API_KEY.txt nữa!`n`nĐường dẫn lưu:`n$vbsPath", "Đăng Ký Thành Công", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
  }
  catch {
    [System.Windows.Forms.MessageBox]::Show("Không thể ghi file khởi động vào thư mục Startup. Chi tiết lỗi:`n$_", "Lỗi Hệ Thống", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
  }
}

# 4. HÀM QUÉT PROFILE CHROME TỪ EMAIL TỰ ĐỘNG GHÉP
function Get-ChromeProfile {
  param([string]$targetEmail)
  $chromeUserDataDir = Join-Path $env:LOCALAPPDATA "Google\Chrome\User Data"
  if (-not (Test-Path $chromeUserDataDir)) { return $null }
      
  $profileDirs = Get-ChildItem -Path $chromeUserDataDir -Directory | Where-Object { $_.Name -match "^Profile*" -or $_.Name -eq "Default" }
  foreach ($profileDir in $profileDirs) {
    $preferencesPath = Join-Path $profileDir.FullName "Preferences"
    if (Test-Path $preferencesPath) {
      try {
        $content = Get-Content -Path $preferencesPath -Raw
        $content = $content -replace '^\^\)\]\}\''\n', ''
        $json = $content | ConvertFrom-Json
        if ($json.account_info[0].email -eq $targetEmail) {
          return $profileDir.Name
        }
      }
      catch {}
    }
  }
  return $null
}

# 5. HÀM XỬ LÝ ÁNH XẠ (MAP) Ổ ĐĨA HÀNG LOẠT
function Start-MappingProcess {
  param([bool]$silent = $false)
    
  # 1. Tắt tận gốc rclone cũ đang chạy
  Stop-Process -Name "rclone" -Force -ErrorAction SilentlyContinue
  Start-Sleep -Seconds 2

  if (-not (Test-Path $apiKeyPath)) {
    if (-not $silent) {
      [System.Windows.Forms.MessageBox]::Show("Không tìm thấy file API_KEY.txt để đọc cấu hình!", "Lỗi", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    }
    return
  }

  $lines = Get-Content -Path $apiKeyPath
  $mapCount = 0

  # 2. Đọc cấu hình map ổ đĩa
  foreach ($line in $lines) {
    $trimmed = $line.Trim()
    if ([string]::IsNullOrEmpty($trimmed) -or $trimmed.StartsWith("#")) { continue }
          
    $parts = [regex]::Split($trimmed, '(?<=\")\s+(?=\")')
    if ($parts.Count -ge 5) {
      $driveLetter = $parts[0].Trim().Trim('"').ToUpper() + ":"
      $volName = $parts[1].Trim().Trim('"')
      $account = $parts[2].Trim().Trim('"')
      $remoteName = "google_drive_${account}"
              
      # Cấu hình lệnh mount gán cứng ổ đĩa và gán tên hiển thị bằng '--volname'
      $arguments = "mount ${remoteName}: ${driveLetter} --vfs-cache-mode writes --network-mode --dir-cache-time 24h --links --volname `"$volName`" --log-level CRITICAL"
              
      # Kích hoạt chạy ẩn danh dưới nền
      Start-Process -FilePath "rclone" -ArgumentList $arguments -WindowStyle Hidden
      $mapCount++
    }
  }

  if (-not $silent) {
    if ($mapCount -gt 0) {
      [System.Windows.Forms.MessageBox]::Show("Đã dọn dẹp rclone cũ và ánh xạ thành công $mapCount ổ đĩa theo đúng chữ cái chỉ định trong danh sách!`nHãy kiểm tra lại trong This PC.", "Map Thành Công", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    }
    else {
      [System.Windows.Forms.MessageBox]::Show("Không đọc được dữ liệu nào hợp lệ để Map ổ đĩa. Hãy kiểm tra lại cấu trúc file!", "Thông Báo", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
    }
  }
}

# 6. KIỂM TRA THAM SỐ CHẠY DÒNG LỆNH (CLI) TRƯỚC KHI MỞ GUI
if ($ForceStop) {
  Stop-Process -Name "rclone" -Force -ErrorAction SilentlyContinue
  Stop-Process -Name "explorer" -Force -ErrorAction SilentlyContinue
  exit
}

if ($SilentMap) {
  Start-MappingProcess -silent $true
  exit
}

# 7. KHỞI TẠO FORM GIAO DIỆN (UI) KHI CHẠY THÔNG THƯỜNG
$form = New-Object System.Windows.Forms.Form
$form.Text = "Rclone Google Drive Manager (Phú Đạt) - V3"
$form.Size = New-Object System.Drawing.Size(650, 540)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

# Tiêu đề giao diện
$labelTitle = New-Object System.Windows.Forms.Label
$labelTitle.Text = "DANH SÁCH CONFIG TÀI KHOẢN (API_KEY.TXT)"
$labelTitle.Location = New-Object System.Drawing.Point(15, 15)
$labelTitle.Size = New-Object System.Drawing.Size(400, 20)
$labelTitle.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($labelTitle)

# Ô Textbox lớn hiển thị/sửa nội dung API_KEY.txt
$textBoxConfig = New-Object System.Windows.Forms.TextBox
$textBoxConfig.Multiline = $true
$textBoxConfig.Location = New-Object System.Drawing.Point(15, 40)
$textBoxConfig.Size = New-Object System.Drawing.Size(600, 300)
$textBoxConfig.ScrollBars = "Both"
$textBoxConfig.Font = New-Object System.Drawing.Font("Consolas", 9.5)
$textBoxConfig.Text = $initialText
$form.Controls.Add($textBoxConfig)

# DÒNG NÚT 1: CHỨA CÁC THAO TÁC CHẠY CHÍNH VÀ FORCE STOP KHẨN CẤP
# NÚT BẤM 1: BẮT ĐẦU ALLOW TỰ ĐỘNG
$btnAllow = New-Object System.Windows.Forms.Button
$btnAllow.Text = "▶ Bắt Đầu ALLOW"
$btnAllow.Location = New-Object System.Drawing.Point(15, 355)
$btnAllow.Size = New-Object System.Drawing.Size(190, 40)
$btnAllow.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$btnAllow.BackColor = [System.Drawing.Color]::LightGreen
$btnAllow.Cursor = [System.Windows.Forms.Cursors]::Hand

$btnAllow.Add_Click({
    $textBoxConfig.Text | Out-File -FilePath $apiKeyPath -Encoding utf8 -Force
    $existingRemotes = rclone listremotes | ForEach-Object { $_.Trim().TrimEnd(':') }
    $lines = $textBoxConfig.Lines
    
    $runConsole = [System.Windows.Forms.MessageBox]::Show("Hệ thống sẽ quét và tự động mở đúng Profile Chrome chứa tài khoản tương ứng. Bấm OK để chạy!", "Xác Nhận Chạy", [System.Windows.Forms.MessageBoxButtons]::OKCancel, [System.Windows.Forms.MessageBoxIcon]::Information)
    if ($runConsole -ne "OK") { return }

    foreach ($line in $lines) {
      $trimmed = $line.Trim()
      if ([string]::IsNullOrEmpty($trimmed) -or $trimmed.StartsWith("#")) { continue }
          
      # Tách chuỗi theo định dạng bộ 5 tham số
      $parts = [regex]::Split($trimmed, '(?<=\")\s+(?=\")')
      if ($parts.Count -ge 5) {
        $account = $parts[2].Trim().Trim('"')
        $id = $parts[3].Trim().Trim('"')
        $secret = $parts[4].Trim().Trim('"')
              
        $remoteName = "google_drive_${account}"
        $autoEmail = "${account}@gmail.com"
              
        if ($existingRemotes -contains $remoteName) { continue }
              
        $profileName = Get-ChromeProfile -targetEmail $autoEmail
        if ($profileName) {
          Start-Process -FilePath "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "--profile-directory=`"$profileName`"", "https://accounts.google.com"
          Start-Sleep -Seconds 2
        }
              
        rclone config create $remoteName drive client_id=$id client_secret=$secret scope=drive
      }
    }
    [System.Windows.Forms.MessageBox]::Show("Đã hoàn tất tiến trình cấu hình tài khoản!", "Thành Công", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
  })
$form.Controls.Add($btnAllow)

# NÚT BẤM 2: MAP Ổ ĐĨA CHỈ ĐỊNH
$btnMap = New-Object System.Windows.Forms.Button
$btnMap.Text = "🗺️ Map Ổ Đĩa Chỉ Định"
$btnMap.Location = New-Object System.Drawing.Point(220, 355)
$btnMap.Size = New-Object System.Drawing.Size(190, 40)
$btnMap.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$btnMap.BackColor = [System.Drawing.Color]::SkyBlue
$btnMap.Cursor = [System.Windows.Forms.Cursors]::Hand

$btnMap.Add_Click({
    # Lưu lại văn bản trong khung cấu hình trước khi chạy map
    $textBoxConfig.Text | Out-File -FilePath $apiKeyPath -Encoding utf8 -Force
    Start-MappingProcess -silent $false
  })
$form.Controls.Add($btnMap)

# NÚT BẤM 3: DỪNG KHẨN CẤP RCLONE
$btnForceStop = New-Object System.Windows.Forms.Button
$btnForceStop.Text = "🛑 Force Stop Rclone"
$btnForceStop.Location = New-Object System.Drawing.Point(425, 355)
$btnForceStop.Size = New-Object System.Drawing.Size(190, 40)
$btnForceStop.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$btnForceStop.BackColor = [System.Drawing.Color]::Orange
$btnForceStop.Cursor = [System.Windows.Forms.Cursors]::Hand

$btnForceStop.Add_Click({
    Stop-Process -Name "rclone" -Force -ErrorAction SilentlyContinue
    Stop-Process -Name "explorer" -Force -ErrorAction SilentlyContinue
    [System.Windows.Forms.MessageBox]::Show("Đã dừng khẩn cấp toàn bộ các tiến trình rclone và tải lại Windows Explorer!", "Force Stop", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
  })
$form.Controls.Add($btnForceStop)


# DÒNG NÚT 2: CHỨA CÁC THIẾT LẬP HỆ THỐNG VÀ TIỆN ÍCH DỌN DẸP KHỞI ĐỘNG
# NÚT BẤM 4: ĐĂNG KÝ KHỞI ĐỘNG CÙNG WIN CỨNG (HARDCODED)
$btnStartup = New-Object System.Windows.Forms.Button
$btnStartup.Text = "🚀 Đăng Ký Khởi Động (Hardcode)"
$btnStartup.Location = New-Object System.Drawing.Point(15, 405)
$btnStartup.Size = New-Object System.Drawing.Size(290, 40)
$btnStartup.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$btnStartup.BackColor = [System.Drawing.Color]::MediumPurple
$btnStartup.ForeColor = [System.Drawing.Color]::White
$btnStartup.Cursor = [System.Windows.Forms.Cursors]::Hand

$btnStartup.Add_Click({
    # Lưu dữ liệu từ TextBox vào file trước khi nén cứng cấu hình
    $textBoxConfig.Text | Out-File -FilePath $apiKeyPath -Encoding utf8 -Force
    Register-StartupHardcoded
  })
$form.Controls.Add($btnStartup)

# NÚT BẤM 5: XÓA TOÀN BỘ CONFIG
$btnClear = New-Object System.Windows.Forms.Button
$btnClear.Text = "🗑 Xóa Toàn Bộ Config"
$btnClear.Location = New-Object System.Drawing.Point(325, 405)
$btnClear.Size = New-Object System.Drawing.Size(290, 40)
$btnClear.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$btnClear.BackColor = [System.Drawing.Color]::LightCoral
$btnClear.Cursor = [System.Windows.Forms.Cursors]::Hand

$btnClear.Add_Click({
    $confirm = [System.Windows.Forms.MessageBox]::Show("Bạn có CHẮC CHẮN muốn XÓA SẠCH toàn bộ cấu hình Rclone và xóa các file Khởi động tự động hiện tại trên máy không?", "Cảnh Báo Nguy Hiểm", [System.Windows.Forms.MessageBoxButtons]::YesNo, [System.Windows.Forms.MessageBoxIcon]::Warning)
    if ($confirm -eq "Yes") {
      # 1. Tắt rclone
      Stop-Process -Name "rclone" -Force -ErrorAction SilentlyContinue
        
      # 2. Xóa các file khởi động .vbs tự động map
      $startupFolder = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs\Startup")
      $oldVbs = Join-Path $startupFolder "MapRCloneDrives.vbs"
      $newVbs = Join-Path $startupFolder "MapRCloneDrives_GoogleDrive.vbs"
      if (Test-Path $oldVbs) { Remove-Item -Path $oldVbs -Force -ErrorAction SilentlyContinue }
      if (Test-Path $newVbs) { Remove-Item -Path $newVbs -Force -ErrorAction SilentlyContinue }

      # 3. Tìm và xóa file config rclone.conf
      $configFileInfo = rclone config file | Out-String
      $configPath = ($configFileInfo -split "`r`n" | Where-Object { $_ -like "*rclone.conf" }).Trim()
          
      if ($configPath -and (Test-Path $configPath)) {
        Remove-Item -Path $configPath -Force
        [System.Windows.Forms.MessageBox]::Show("Đã xóa sạch thành công cấu hình Rclone và dọn dẹp các tệp khởi động!", "Thông Báo", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
      }
      else {
        [System.Windows.Forms.MessageBox]::Show("Đã dọn dẹp file khởi động. Không tìm thấy file rclone.conf nào đang hoạt động.", "Thông Báo", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
      }
    }
  })
$form.Controls.Add($btnClear)


# Footer hướng dẫn sử dụng nhanh và các tham số CLI
$labelFooter = New-Object System.Windows.Forms.Label
$labelFooter.Text = "Chuẩn: `"Ổ`" `"Tên`" `"Acc`" `"ID`" `"Secret`"`nKhởi động Hardcode sẽ đóng gói cấu hình trực tiếp vào VBS trong 'shell:startup'"
$labelFooter.Location = New-Object System.Drawing.Point(15, 460)
$labelFooter.Size = New-Object System.Drawing.Size(600, 35)
$labelFooter.ForeColor = [System.Drawing.Color]::Gray
$labelFooter.Font = New-Object System.Drawing.Font("Segoe UI", 8.5, [System.Drawing.FontStyle]::Italic)
$form.Controls.Add($labelFooter)

# 8. KHỞI CHẠY GIAO DIỆN
$form.ShowDialog() | Out-Null