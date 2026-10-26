# assistant-core-team07

Dự án Study Assistant - Môn CSC10014 (Practical Track).

* **Lab 3:** Tách script `assistant_monolith.py` thành package `assistant_core`.
* **Lab 4:** Chuyển đổi Study Assistant thành dịch vụ Web API qua HTTP bằng **FastAPI**, JSON, bảo mật API Key, gọi dịch vụ bên ngoài và kiểm thử tự động.

---

## 🚀 Cài đặt & Khởi chạy (Windows, Git Bash)

### 1. Cài đặt môi trường

```bash
# Clone repository về máy
git clone git@github.com:25127029-DBDANH/assistant-core-lab-team07.git
cd assistant-core-lab-team07

# Tạo và kích hoạt môi trường ảo
py -3 -m venv .venv
source .venv/Scripts/activate

# Cài đặt thư viện và cài đặt package dạng editable
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Thiết lập biến môi trường
cp .env.example .env        # Lưu ý: .env chứa API Key và KHÔNG được commit
```

### 2. Khởi chạy Web Server

Chạy server FastAPI ở chế độ reload tự động:
```bash
uvicorn assistant_api.main:create_app --factory --reload
```

* Truy cập trang kiểm tra: `http://127.0.0.1:8000/`
* Mở trang tài liệu tương tác Swagger UI: `http://127.0.0.1:8000/docs`

### 3. Kiểm thử tự động

```bash
# Chạy toàn bộ unit test
pytest -q

# Chạy kịch bản kiểm thử API bằng cURL
bash api-tests/curl_tests.sh

# Kiểm tra định dạng và chất lượng code
ruff check .
```

---

## 👥 Phân chia công việc Lab 4 (Nhóm 7 thành viên)

> [!NOTE]
> Mọi thành viên trước khi thực hiện task được giao đều phải tự hoàn thành 5 bài tập warm-up P1–P5 trong thư mục `practice/hello_api.py` trên nhánh riêng và đảm bảo `pytest -q practice/test_hello_api.py` pass 100%.

| STT | Đầu việc (Task) | Mô tả chi tiết phần việc cần làm | File liên quan | Người phụ trách |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **T1: Core Chat API** | Triển khai endpoint `POST /v1/chat`: nhận `ChatRequest`, chuyển tiếp vào `service.handle()`, sinh `request_id` ngẫu nhiên (12 ký tự hex) và trả về `ChatResponse`. | `src/assistant_api/main.py` | ` ` |
| **2** | **T2: Create Feedback** | Triển khai endpoint `POST /v1/feedback`: tiếp nhận `FeedbackIn` (chỉ cho phép rating -1, 0, 1), sinh ID tự tăng, lưu thời gian tạo UTC vào `feedback_store`, trả về `FeedbackOut` với mã `201 Created`. | `src/assistant_api/main.py` | ` ` |
| **3** | **T3: Admin Feedback Security** | Triển khai endpoint `GET /v1/feedback`: bảo vệ bằng dependency `require_admin` qua header `X-API-Key`, trả về danh sách phản hồi hoặc mã lỗi `401 Unauthorized`. | `src/assistant_api/main.py` | ` ` |
| **4** | **T4: Weather API & 503 Handler** | Triển khai endpoint `GET /v1/weather`: kết nối `WeatherClient` (Open-Meteo), xử lý bắt ngoại lệ `ExternalServiceError` để trả về HTTP status `503 Service Unavailable`. | `src/assistant_api/main.py` | ` ` |
| **5** | **H1: Offices Directory & Tests** | Mở rộng class `OfficeDirectory` với method `all()` (sắp xếp danh sách theo tên), tạo route `GET /v1/offices`, và tự viết 2 unit test trong `tests/test_api.py` (check status 200 và có "Library"). | `src/assistant_core/knowledge.py`<br>`src/assistant_api/main.py`<br>`tests/test_api.py` | ` ` |
| **6** | **Part F: Rate Limiting Bonus** | Tích hợp `RateLimiter` vào đầu endpoint `POST /v1/chat` để chặn spam theo IP (trả về mã `429 Too Many Requests`), mở bỏ `@pytest.mark.skip` để làm xanh test `test_rate_limit`. | `src/assistant_api/main.py`<br>`tests/test_api.py` | ` ` |
| **7** | **H3 Bonus & H2 Reflection** | Tích hợp thêm 1 Public API bên ngoài (ví dụ Holiday/Currency) áp dụng timeout, retry, cache fallback + Soạn thảo đoạn văn phản tư H2 (5 dòng) giải thích sự khác biệt giữa gọi hàm trực tiếp và Web API. | `src/assistant_api/`<br>`docs/reflection.md` | ` ` |

---

## 📌 Quy trình làm việc và nộp bài

1. **Nhánh làm việc:** Mỗi thành viên checkout nhánh mới từ `main`: `feature/issue-<id>-<ten_task>`.
2. **Quy chuẩn Commit:** Đặt tên commit theo chuẩn: `<loại>(<module>): <mô tả> (closes #<issue_id>)`.
   * Ví dụ: `feat(api): implement /v1/chat endpoint (closes #1)`.
3. **Mở Pull Request (PR):**
   * Đảm bảo `pytest -q` pass toàn bộ test.
   * Đính kèm ảnh chụp màn hình `/docs` thực hiện gọi thành công `/v1/chat`.
   * Ghi rõ giải thích và nội dung reflection H2.
4. **Tích hợp nhóm:** Tech Lead review, merge bản hoàn chỉnh vào `main` và đánh tag Git `v0.4-api`.
