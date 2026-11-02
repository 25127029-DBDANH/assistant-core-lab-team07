# assistant-core-team07

Dự án Study Assistant - Môn CSC10014 (Practical Track).

* **Lab 3:** Tách script `assistant_monolith.py` thành package `assistant_core`.
* **Lab 4:** Chuyển đổi Study Assistant thành dịch vụ Web API qua HTTP bằng **FastAPI**, JSON, bảo mật API Key, gọi dịch vụ bên ngoài và kiểm thử tự động.
* **Lab 5:** Tích hợp cơ sở dữ liệu **SQLite** qua **SQLModel**, lưu trữ bền vững lịch sử tương tác (`Interaction`) và phản hồi (`Feedback`), bảo vệ quyền riêng tư người dùng.

---

## 🚀 Cài đặt & Khởi chạy (Windows, Git Bash)

### 1. Cài đặt môi trường

```bash
# Clone repository về máy
git clone https://github.com/25127029-DBDANH/assistant-core-lab-team07.git
cd assistant-core-lab-team07

# Tạo và kích hoạt môi trường ảo
py -3 -m venv .venv
source .venv/Scripts/activate

# Cài đặt thư viện và cài đặt package dạng editable
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Thiết lập biến môi trường
cp .env.example .env        # Lưu ý: .env chứa API Key, Salt và KHÔNG được commit
```

### 2. Khởi tạo Cơ sở dữ liệu và Migration

```bash
# Khởi tạo schema bằng script migrate
python scripts/migrate.py assistant.db

# Tạo 300 tương tác mẫu để kiểm thử truy vấn
python scripts/seed.py assistant.db 300
```

### 3. Khởi chạy Web Server

Chạy server FastAPI ở chế độ reload tự động:
```bash
uvicorn assistant_api.main:create_app --factory --reload
```

* Truy cập trang kiểm tra: `http://127.0.0.1:8000/`
* Mở trang tài liệu tương tác Swagger UI: `http://127.0.0.1:8000/docs`

### 4. Kiểm thử tự động

```bash
# Chạy toàn bộ unit test
pytest -q

# Kiểm tra bài tập thực hành SQL (15 câu)
cd practice && python check.py && cd ..

# Chạy unit test phần Python Database (D1-D3)
pytest -q practice/test_school_repo.py

# Kiểm tra định dạng và chất lượng code
ruff check .
```
