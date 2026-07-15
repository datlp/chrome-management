# Chrome Profiles Manager

Phần mềm quản lý và mở hàng loạt Profile Chrome với giao diện tối giản (Dark Mode) viết bằng Python & Tkinter.

## Hướng dẫn cài đặt môi trường chạy thử

### 1. Yêu cầu hệ thống
- Hệ điều hành: Windows
- Đã cài đặt [Python (phiên bản 3.x trở lên)](https://www.python.org/downloads/)

### 2. Cài đặt các thư viện cần thiết
Dự án sử dụng các thư viện chuẩn (built-in) của Python bao gồm `os`, `json`, `subprocess`, `time`, `tkinter`. Do đó, bạn **không cần cài thêm** thư viện bên ngoài để chạy file Python gốc.

Chạy trực tiếp ứng dụng bằng lệnh:
```bash
python chrome_profiles.py
```

---

## Hướng dẫn Build thành file thực thi (.exe)

Để đóng gói mã nguồn Python thành file `.exe` chạy độc lập trên Windows (không cần máy cài Python), chúng ta sử dụng công cụ `PyInstaller`.

### Bước 1: Cài đặt PyInstaller
Mở Command Prompt (cmd) hoặc PowerShell và chạy lệnh sau để cài đặt:
```bash
pip install pyinstaller
```

### Bước 2: Build ứng dụng
Chạy lệnh bên dưới để đóng gói file `chrome_profiles.py` thành một file `.exe` duy nhất:
```bash
pyinstaller --noconsole --onefile chrome_profiles.py
```

Trong đó:
- `--onefile`: Đóng gói tất cả tài nguyên và mã nguồn vào duy nhất một file `.exe`.
- `--noconsole`: Ẩn cửa sổ dòng lệnh màu đen khi chạy ứng dụng (chỉ hiển thị giao diện đồ họa GUI).

*(Tùy chọn) Nếu bạn có file icon (.ico) riêng và muốn đổi icon cho file exe:*
```bash
pyinstaller --noconsole --onefile --icon=your_icon.ico chrome_profiles.py
```

### Bước 3: Nhận kết quả
Sau khi PyInstaller chạy hoàn tất thành công:
1. File `.exe` thành phẩm sẽ nằm trong thư mục **`dist/`** mới được tạo ra:
   - Đường dẫn: `dist/chrome_profiles.exe`
2. Bạn có thể copy file `chrome_profiles.exe` này đi bất cứ máy tính Windows nào khác để chạy trực tiếp.
3. Các thư mục trung gian như `build/` và file `chrome_profiles.spec` có thể được xóa đi nếu không dùng tới.

---

## Hướng dẫn tạo Release trên GitHub và tải lên file .exe

Bạn có thể đưa file `.exe` đã build lên mục **Releases** của GitHub bằng 2 cách dưới đây:

### Cách 1: Sử dụng GitHub CLI (`gh`) (Khuyên dùng - Nhanh nhất)

Nếu máy của bạn đã cài đặt [GitHub CLI](https://cli.github.com/), bạn có thể thực hiện tạo release và tải file lên trực tiếp từ dòng lệnh:

1. **Đăng nhập vào GitHub CLI** (nếu chưa):
   ```bash
   gh auth login
   ```
2. **Tạo Release và đính kèm file `.exe`**:
   ```bash
   gh release create v1.0.0 dist/chrome_profiles.exe --title "Release v1.0.0" --notes "Phiên bản đầu tiên của Chrome Profiles Manager"
   ```
   *(Thay đổi `v1.0.0` bằng tag/phiên bản thực tế của bạn).*

---

### Cách 2: Sử dụng Giao diện Web của GitHub

Nếu không sử dụng GitHub CLI, bạn thực hiện thủ công như sau:

1. **Tạo và đẩy Tag git lên GitHub**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
2. **Tạo Release trên Web**:
   - Truy cập vào repository của bạn trên GitHub.
   - Nhấp vào mục **Releases** ở thanh bên phải (Sidebar) -> Chọn **Draft a new release**.
   - Chọn tag `v1.0.0` bạn vừa push lên.
   - Điền tiêu đề và mô tả cho bản phát hành này.
3. **Đính kèm file `.exe`**:
   - Kéo thả file `chrome_profiles.exe` từ thư mục `dist/` vào khu vực **Attach binaries by dropping them here or selecting them**.
   - Nhấn **Publish release** để hoàn tất.

---

## Nhật ký thay đổi (Changelog) - Phiên bản v1.1.0

Bản cập nhật lớn tái cấu trúc giao diện và nâng cấp trải nghiệm người dùng:

- **Quản lý Profiles (Tab 1):**
  - Đưa danh sách thư mục thực tế của Chrome về dạng bảng thông minh hỗ trợ hiển thị Email/Tên và Trạng thái.
  - Hỗ trợ nhấn giữ và kéo chuột trái (drag-select) để bôi chọn nhanh nhiều profile.
  - Nhấp đúp chuột trái (double-click) để mở nhanh profile tương ứng.
  - Click chuột phải mở menu ngữ cảnh hỗ trợ mở nhanh hoặc xóa vĩnh viễn các profile đã chọn khỏi ổ cứng.
  - Thu gọn thanh cấu hình, di chuyển hộp chọn số lượng "Cùng lúc" (từ 2 đến 9) và nút "Mở profile mới" lên thanh tiêu đề.
  - Lọc bỏ hoàn toàn các profile hệ thống (`System Profile`, `Guest Profile`).

- **Quản lý Extensions (Tab 2):**
  - Chuyển đổi toàn bộ giao diện quản lý sang dạng bảng tính chỉnh sửa trực tiếp (Inline-editable spreadsheet) không cần form nhập liệu phụ.
  - Luôn ghim dòng đầu tiên để thêm mới extension nhanh (`+ Thêm mới...`).
  - Tự động lưu ngầm thay đổi vào file `.bat` sau khi dừng gõ phím 1 giây (Debounce Auto-save) không gây gián đoạn.
  - Hỗ trợ bôi chọn nhiều dòng và click chuột phải để xóa.
  - Tích hợp Import/Export dữ liệu từ file CSV (`chrome_extension.csv`) và nút chạy script Admin trực tiếp ngay góc trên bên phải của bảng.

---

# Hướng dẫn Cập nhật Phiên bản (Version Update & Release)

Khi bạn thực hiện chỉnh sửa code và muốn cập nhật phiên bản mới lên GitHub, hãy thực hiện theo các bước sau:

### Bước 1: Build lại file `.exe` mới
```bash
pyinstaller --noconsole --onefile chrome_profiles.py
pyinstaller --noconsole --onefile windows_management.py
```

### Bước 2: Cập nhật Tag Git (Ví dụ lên v1.1.0)
Nếu bạn muốn tạo một tag mới trên Git:
```bash
git tag v1.1.0
git push origin v1.1.0
```

Nếu bạn muốn cập nhật đè (ghi đè) tag cũ đã tồn tại trên remote:
```bash
# Xóa tag cũ ở local và remote
git tag -d v1.1.0
git push --delete origin v1.1.0

# Tạo lại tag mới và đẩy lên
git tag v1.1.0
git push origin v1.1.0
```

### Bước 3: Đẩy bản Release mới lên GitHub
Sử dụng GitHub CLI để tạo/cập nhật release đính kèm file exe mới:
```bash
gh release create v1.1.0 dist/chrome_profiles.exe dist/windows_management.exe --title "Release v1.1.0" --notes "Cập nhật các tính năng mới trong Changelog"
```
*(Nếu Release đã tồn tại và bạn muốn cập nhật đè file exe vào release đó, thêm tham số `--overwrite` hoặc upload đè: `gh release upload v1.1.0 dist/chrome_profiles.exe dist/windows_management.exe --clobber`)*

---

# Windows Debloat Manager

Phần mềm quản lý và gỡ bỏ hàng loạt ứng dụng debloatware mặc định trên Windows (Appx Packages) với giao diện tối giản (Dark Mode) viết bằng Python & Tkinter, tham khảo từ file cấu hình của `windows-debloatware-apps.ps1`.

## Hướng dẫn chạy thử
Chạy trực tiếp ứng dụng bằng lệnh:
```bash
python windows_management.py
```
> [!IMPORTANT]
> Để thực hiện gỡ cài đặt các gói hệ thống một cách hiệu quả nhất, bạn nên mở Terminal/PowerShell với quyền **Administrator** trước khi chạy.

---

## Nhật ký thay đổi (Changelog) - Phiên bản v2.0.1 (Windows Debloat Manager)
# Chrome Profiles Manager

Phần mềm quản lý và mở hàng loạt Profile Chrome với giao diện tối giản (Dark Mode) viết bằng Python & Tkinter.

## Hướng dẫn cài đặt môi trường chạy thử

### 1. Yêu cầu hệ thống
- Hệ điều hành: Windows
- Đã cài đặt [Python (phiên bản 3.x trở lên)](https://www.python.org/downloads/)

### 2. Cài đặt các thư viện cần thiết
Dự án sử dụng các thư viện chuẩn (built-in) của Python bao gồm `os`, `json`, `subprocess`, `time`, `tkinter`. Do đó, bạn **không cần cài thêm** thư viện bên ngoài để chạy file Python gốc.

Chạy trực tiếp ứng dụng bằng lệnh:
```bash
python chrome_profiles.py
```

---

## Hướng dẫn Build thành file thực thi (.exe)

Dự án đã tích hợp sẵn một script build tự động giúp cài đặt PyInstaller và đóng gói cả hai ứng dụng (`chrome_profiles.py` và `windows_management.py`) thành các file `.exe` chạy độc lập, đồng thời dọn dẹp các tệp tin tạm thừa.

### Chạy lệnh Build tự động:
Mở CMD hoặc PowerShell tại thư mục dự án và chạy:
```bash
python build.py
```

### Cách thức hoạt động:
1. Tự động kiểm tra và cài đặt `pyinstaller` nếu máy bạn chưa có.
2. Build song song cả hai file thành `dist/chrome_profiles.exe` và `dist/windows_management.exe`.
3. Tự động xóa thư mục tạm `build/` và các file `.spec` sau khi hoàn thành.

3. Các thư mục trung gian như `build/` và file `chrome_profiles.spec` có thể được xóa đi nếu không dùng tới.

---

## Hướng dẫn tạo Release trên GitHub và tải lên file .exe

Bạn có thể đưa file `.exe` đã build lên mục **Releases** của GitHub bằng 2 cách dưới đây:

### Cách 1: Sử dụng GitHub CLI (`gh`) (Khuyên dùng - Nhanh nhất)

Nếu máy của bạn đã cài đặt [GitHub CLI](https://cli.github.com/), bạn có thể thực hiện tạo release và tải file lên trực tiếp từ dòng lệnh:

1. **Đăng nhập vào GitHub CLI** (nếu chưa):
   ```bash
   gh auth login
   ```
2. **Tạo Release và đính kèm file `.exe`**:
   ```bash
   gh release create v1.0.0 dist/chrome_profiles.exe --title "Release v1.0.0" --notes "Phiên bản đầu tiên của Chrome Profiles Manager"
   ```
   *(Thay đổi `v1.0.0` bằng tag/phiên bản thực tế của bạn).*

---

### Cách 2: Sử dụng Giao diện Web của GitHub

Nếu không sử dụng GitHub CLI, bạn thực hiện thủ công như sau:

1. **Tạo và đẩy Tag git lên GitHub**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
2. **Tạo Release trên Web**:
   - Truy cập vào repository của bạn trên GitHub.
   - Nhấp vào mục **Releases** ở thanh bên phải (Sidebar) -> Chọn **Draft a new release**.
   - Chọn tag `v1.0.0` bạn vừa push lên.
   - Điền tiêu đề và mô tả cho bản phát hành này.
3. **Đính kèm file `.exe`**:
   - Kéo thả file `chrome_profiles.exe` từ thư mục `dist/` vào khu vực **Attach binaries by dropping them here or selecting them**.
   - Nhấn **Publish release** để hoàn tất.

---

## Nhật ký thay đổi (Changelog) - Phiên bản v1.1.0

Bản cập nhật lớn tái cấu trúc giao diện và nâng cấp trải nghiệm người dùng:

- **Quản lý Profiles (Tab 1):**
  - Đưa danh sách thư mục thực tế của Chrome về dạng bảng thông minh hỗ trợ hiển thị Email/Tên và Trạng thái.
  - Hỗ trợ nhấn giữ và kéo chuột trái (drag-select) để bôi chọn nhanh nhiều profile.
  - Nhấp đúp chuột trái (double-click) để mở nhanh profile tương ứng.
  - Click chuột phải mở menu ngữ cảnh hỗ trợ mở nhanh hoặc xóa vĩnh viễn các profile đã chọn khỏi ổ cứng.
  - Thu gọn thanh cấu hình, di chuyển hộp chọn số lượng "Cùng lúc" (từ 2 đến 9) và nút "Mở profile mới" lên thanh tiêu đề.
  - Lọc bỏ hoàn toàn các profile hệ thống (`System Profile`, `Guest Profile`).

- **Quản lý Extensions (Tab 2):**
  - Chuyển đổi toàn bộ giao diện quản lý sang dạng bảng tính chỉnh sửa trực tiếp (Inline-editable spreadsheet) không cần form nhập liệu phụ.
  - Luôn ghim dòng đầu tiên để thêm mới extension nhanh (`+ Thêm mới...`).
  - Tự động lưu ngầm thay đổi vào file `.bat` sau khi dừng gõ phím 1 giây (Debounce Auto-save) không gây gián đoạn.
  - Hỗ trợ bôi chọn nhiều dòng và click chuột phải để xóa.
  - Tích hợp Import/Export dữ liệu từ file CSV (`chrome_extension.csv`) và nút chạy script Admin trực tiếp ngay góc trên bên phải của bảng.

---

# Hướng dẫn Cập nhật Phiên bản (Version Update & Release)

Khi bạn thực hiện chỉnh sửa code và muốn cập nhật phiên bản mới lên GitHub, hãy thực hiện theo các bước sau:

### Bước 1: Cập nhật phiên bản và Tag Git tự động
Chạy lệnh sau để tăng phiên bản (ví dụ tăng patch `1.2.0` -> `1.2.1`):
```bash
python upversion.py patch
```
*(Bạn cũng có thể dùng tham số `minor` hoặc `major`, hoặc chạy không tham số `python upversion.py` để nhập thủ công).*
Script này sẽ tự động thay đổi phiên bản trong `version.txt`, `chrome_profiles.py`, `windows_management.py`, `Readme.md` và chạy lệnh `git commit`, `git tag` cục bộ.

### Bước 2: Build lại file `.exe` mới
```bash
python build.py
```

### Bước 3: Đẩy bản Release mới lên GitHub
1. Đẩy mã nguồn và thẻ Tag mới lên remote repository:
   ```bash
   git push origin main --tags
   ```
2. Sử dụng GitHub CLI để tạo release và upload các file exe mới:
   ```bash
   gh release create v2.0.1 dist/chrome_profiles.exe dist/windows_management.exe --title "Release v2.0.1" --notes "Cập nhật các tính năng mới trong Changelog"
   ```
*(Nếu Release đã tồn tại và bạn muốn cập nhật đè file exe vào release đó, thêm tham số `--overwrite` hoặc upload đè: `gh release upload v1.1.0 dist/chrome_profiles.exe dist/windows_management.exe --clobber`)*

---

# Windows Debloat Manager

Phần mềm quản lý và gỡ bỏ hàng loạt ứng dụng debloatware mặc định trên Windows (Appx Packages) với giao diện tối giản (Dark Mode) viết bằng Python & Tkinter, tham khảo từ file cấu hình của `windows-debloatware-apps.ps1`.

## Hướng dẫn chạy thử
Chạy trực tiếp ứng dụng bằng lệnh:
```bash
python windows_management.py
```
> [!NOTE]
> Ứng dụng hỗ trợ tự động kích hoạt hộp thoại xác nhận quyền quản trị (UAC Prompt) khi chỉnh sửa Registry, do đó bạn **không cần** chạy ứng dụng với quyền Administrator ngay từ đầu.

---

## Nhật ký thay đổi (Changelog) - Phiên bản v2.0.1 (Windows Debloat Manager)
- **Quản lý Debloat (Tab 1):**
  - Tải danh sách mặc định gồm hơn 60+ ứng dụng debloatware phổ biến của Windows từ script PowerShell.
  - Hỗ trợ lưu trữ danh sách cá nhân hóa trong thư mục người dùng (`%USERPROFILE%\dsoft\windows-debloat-management\windows_debloat_config.json`).
  - Hỗ trợ thêm mới (`+ Thêm mới...`), chỉnh sửa trực tiếp (Inline Editing) kiểu khớp (Exact / Wildcard) và xóa gói khỏi danh sách.
  - Quét kiểm tra trạng thái cài đặt thực tế của các gói Appx trên hệ thống một cách nhanh chóng qua luồng chạy ngầm PowerShell (không đơ UI).
  - Hỗ trợ Import/Export cấu hình danh sách debloat qua file CSV.
- **Get-AppxPackage Live System (Tab 2):**
  - Quét trực tiếp toàn bộ các gói Appx đang được cài đặt trên máy tính mà không cần quyền Administrator.
  - Chỉ hiển thị cột **Tên Gói** và **Package ID** để giao diện hiển thị gọn gàng, rõ ràng hơn.
  - Hỗ trợ tìm kiếm và lọc thời gian thực (Real-time Filter) theo từ khóa.
  - Chọn nhanh và thêm các gói tìm thấy vào danh sách Debloat ở Tab 1.
  - Hỗ trợ gỡ cài đặt trực tiếp (Direct Uninstall) gói được chọn thông qua chạy ngầm lệnh `Remove-AppxPackage`.
- **Target Release Version (Tab 3):**
  - Dò tìm trực quan thông tin hệ điều hành (Hệ điều hành hiện tại, Display Version, Current Build và UBR).
  - Đọc trạng thái cấu hình Target Release hiện tại từ Registry Policies của máy tính.
  - Cung cấp danh sách giới hạn các phiên bản từ Windows 10 21H2 đến Windows 11 26H2.
  - Tự động gợi ý mặc định theo phiên bản Windows hiện tại của máy để dễ dàng khóa tại chỗ.
  - Hỗ trợ ghi đè Registry (`ProductVersion`, `TargetReleaseVersionInfo`, `TargetReleaseVersion`) hoặc xóa bỏ giới hạn trực tiếp từ giao diện thông qua kích hoạt hộp thoại UAC tự động (không bắt buộc chạy ứng dụng dưới quyền Admin).
  - **Tối ưu hóa hiệu năng**: Bổ sung nút bấm **Kích hoạt Ultimate Performance Power Plan** chạy ngầm câu lệnh `powercfg` với quyền quản trị UAC để mở khóa gói điện năng tối đa của Windows.


