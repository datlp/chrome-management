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
