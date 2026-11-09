# assistant-core-team07

Dự án Study Assistant - Môn CSC10014 (Practical Track).

* **Lab 3:** Tách script `assistant_monolith.py` thành package `assistant_core`.
* **Lab 4:** Chuyển đổi Study Assistant thành dịch vụ Web API qua HTTP bằng **FastAPI**, JSON, bảo mật API Key, gọi dịch vụ bên ngoài và kiểm thử tự động.
* **Lab 5:** Tích hợp cơ sở dữ liệu **SQLite** qua **SQLModel**, lưu trữ bền vững lịch sử tương tác (`Interaction`) và phản hồi (`Feedback`), bảo vệ quyền riêng tư người dùng.
* **Lab 6:** Tích hợp trí tuệ nhân tạo an toàn (**Safe RAG**) với bộ tìm kiếm BM25, mô hình ngôn ngữ có kiểm định trích dẫn nguồn (**Grounding Check**), cơ chế từ chối khi không chắc chắn (**Abstain / "I Don't Know"**) và bộ tiêu chuẩn đo lường Benchmark 3 đường dẫn.

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
# Chạy toàn bộ unit test của trợ lý
pytest -q

# Kiểm tra bài tập thực hành SQL trên school.db (Q1-Q15)
cd practice && python check.py && cd ..

# Chạy unit test phần Python Database (D1-D3)
pytest -q practice/test_school_repo.py

# Kiểm tra định dạng và chất lượng code
ruff check .
```

---

## 👥 Phân chia công việc Lab 6: Adding AI to the Assistant, Safely (Nhóm 7 thành viên)

> [!IMPORTANT]
> Trọng tâm Lab 6 là xây dựng cơ chế **RAG an toàn (Safe RAG)**, kiểm tra tính có căn cứ (**Grounding Check**), cơ chế từ chối khi không có dữ liệu (**Abstain**), khởi động Mini Search Engine, đo lường Benchmark 3 đường dẫn và giải quyết bài toán xử lý ngôn ngữ thực tế. Mỗi thành viên checkout nhánh riêng theo mã task, hoàn thành công việc, mở PR và pass 100% CI để Tech Lead review và merge.

| STT | Đầu việc (Task) | Mô tả chi tiết phần việc cần làm | File liên quan | Người phụ trách (Assignee) |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **Part E — Task A1: Cơ chế Từ chối Trả lời ("I Don't Know")** | Triển khai TODO A1 trong `RagAnswerer.answer`: kiểm tra nếu không tìm thấy đoạn văn (`not hits`) hoặc điểm BM25 cao nhất nhỏ hơn ngưỡng tin cậy `self.min_score`, lập tức trả về `Response(answer=ESCALATE_MSG, intent=Intent.UNKNOWN, path="abstain", escalate=True, confidence=0.0)` trước khi gọi LLM; gỡ bỏ marker `xfail` trên test `test_abstain_when_nothing_relevant`. Phụ trách review PR, tích hợp nhóm và gắn tag phát hành `v0.6-ai`. | `src/assistant_core/rag/answerer.py`<br>`tests/test_rag.py` | **Danh (Leader)** (`@25127029-DBDANH`) |
| **2** | **Part D — Task A2: Cơ chế Kiểm tra Trích dẫn Nguồn (Grounding Check)** | Triển khai TODO A2 trong hàm `parse_draft`: kiểm tra nếu mô hình không từ chối (`not draft.abstain`) thì bắt buộc phải có ít nhất 1 nguồn trích dẫn và toàn bộ nguồn đó phải là tập con của các đoạn tài liệu tìm thấy (`set(draft.source_ids) <= allowed_ids`), nếu vi phạm thì raise `ProviderError("answer cites sources that were not retrieved")`; gỡ bỏ marker `xfail` trên test `test_citation_of_unretrieved_source_is_rejected`. | `src/assistant_core/llm.py`<br>`tests/test_rag.py` | **Khang** (`@ankhang-maker`) |
| **3** | **Part B — Task S1: Xây dựng Inverted Index (Mini Search)** | Hoàn thiện hàm `build_index(docs: dict[str, str])` trong `practice/mini_search.py`: tách từ qua `tokenize()`, loại bỏ stop words, xây dựng cấu trúc chỉ mục đảo ánh xạ từ từng từ vựng sang tập hợp ID các tài liệu chứa từ khóa đó (`dict[str, set[str]]`). Viết bổ sung test case kiểm tra tính toàn vẹn của chỉ mục với các từ khóa lặp và từ dừng trong `practice/test_mini_search.py`. | `practice/mini_search.py`<br>`practice/test_mini_search.py` | **Đăng** (`@dhdang2523-coder`) |
| **4** | **Part B — Task S2 & S3: Thuật toán Score & Rank (Mini Search)** | Hoàn thiện hàm `search(index, query, k=2)` trong `practice/mini_search.py`: tính điểm tương đồng văn bản dựa trên tần số xuất hiện của các từ khóa câu hỏi trong tài liệu (S2), sau đó sắp xếp các tài liệu theo thứ tự điểm giảm dần và lấy top-$k$ kết quả cao nhất (S3). Chạy và pass 100% bộ test `practice/test_mini_search.py` (4/4 tests). | `practice/mini_search.py`<br>`practice/test_mini_search.py` | **Hạo** (`@DMH554`) |
| **5** | **Part F: Đo lường Benchmark So sánh Ba Đường Dẫn & Báo cáo** | Thực thi kịch bản đo lường `python eval/compare_paths.py` trên 20 test cases mẫu trong `eval/cases.jsonl`, trích xuất bảng số liệu đo lường 3 cơ chế (`deterministic`, `retrieval`, `llm (stub)`). Cập nhật bảng kết quả vào `docs/lab6/path_comparison.md` và viết 3 câu nhận xét phân tích chuyên sâu (lựa chọn luồng cho handbook, lý do kỹ thuật, và đề xuất xử lý trường hợp lỗi E14/E15). | `eval/compare_paths.py`<br>`eval/cases.jsonl`<br>`docs/lab6/path_comparison.md` | **Lam** (`@LamNotNam1607`) |
| **6** | **Homework H1: Thiết kế 5 Test Cases Mới & Tái đo lường Benchmark** | Thiết kế và bổ sung 5 câu hỏi kiểm thử mới (E21–E25) vào `eval/cases.jsonl`: gồm 3 câu hỏi thông thường kèm nguồn đối chiếu chính xác từ kho tài liệu `data/kb/` (`expect_source`), và 2 câu hỏi ngoài phạm vi hoặc xâm phạm quyền riêng tư yêu cầu từ chối (`expect_abstain: true`). Chạy lại benchmark trên tập 25 câu hỏi, cập nhật bảng so sánh mới và phân tích kết quả vào `docs/lab6/path_comparison.md`. | `eval/cases.jsonl`<br>`eval/compare_paths.py`<br>`docs/lab6/path_comparison.md` | **Hưng** (`@pghung2516-netizen`) |
| **7** | **Homework H2 Reflection & Bonus H3: Xử lý Từ vựng Số nhiều (Stemming)** | Soạn thảo đoạn văn Reflection H2 (5 dòng) giải thích nguyên lý hoạt động của RAG theo ẩn dụ "kỳ thi mở sách" và phân tích chốt chặn an toàn của code mà LLM không tự làm được. Đồng thời triển khai Bonus H3: trong `src/assistant_core/rag/index.py`, cải tiến hàm `tokenize` để tự động loại bỏ chữ `"s"` ở cuối các từ dài hơn 4 ký tự (xử lý số nhiều), chạy lại benchmark xác nhận case E14 chuyển sang pass và ghi nhận kết quả vào `docs/lab6/path_comparison.md`. | `docs/lab6/path_comparison.md`<br>`src/assistant_core/rag/index.py`<br>`eval/compare_paths.py` | **Đạt** (`@EddieOuttaHere`) |

## 👥 Phân chia công việc Lab 5: Data & SQL (Nhóm 7 thành viên)

> [!IMPORTANT]
> Trọng tâm bài tập nhóm là **Phần E (Tích hợp Cơ sở dữ liệu vào Study Assistant)** và **Phần F (Phân tích dữ liệu & Bài tập về nhà)**. Mỗi thành viên checkout nhánh riêng theo mã issue, hoàn thành task, mở PR và pass CI để Tech Lead review và merge.

| Issue | Đầu việc (Task) | Mô tả chi tiết phần việc cần làm | File liên quan | Người phụ trách (Assignee) |
| :---: | :--- | :--- | :--- | :---: |
| **[#34](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/34)** | **E.4 (R1): Lưu Feedback bền vững** | Hoàn thiện `add_feedback` trong `Repository`: kiểm tra `exists` của `request_id`, thêm bản ghi `Feedback`, commit và refresh lấy ID tự tăng; gỡ `xfail` trên test `test_feedback_requires_existing_interaction`. | `src/assistant_api/db.py`<br>`tests/test_db.py` | **Danh (Leader)** (`@25127029-DBDANH`) |
| **[#35](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/35)** | **E.5 (R2): Truy vấn Feedback mới nhất** | Hoàn thiện `list_feedback(limit)` trong `Repository` dùng SQLModel (`select(Feedback).order_by(created_at.desc()).limit(limit)`), kiểm tra endpoint `GET /v1/feedback` có bảo vệ quyền Admin. | `src/assistant_api/db.py`<br>`src/assistant_api/main.py`<br>`tests/test_api.py` | **Khang** (`@ankhang-maker`) |
| **[#36](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/36)** | **E.6: Kiểm thử Persistence qua Server Restart** | Viết test case chứng minh tính bền vững: tương tác và feedback được ghi xuống file SQLite vẫn tồn tại sau khi tắt app/engine và khởi động lại server; kiểm thử endpoint `/v1/stats/intents`. | `tests/test_api.py`<br>`src/assistant_api/main.py` | **Đăng** (`@dhdang2523-coder`) |
| **[#37](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/37)** | **F.1 & F.2: Truy vấn Thống kê Intent & Latency** | Seed 300 tương tác mẫu vào `assistant.db`, viết câu lệnh SQL thống kê số request theo từng intent (Q1 - `GROUP BY`) và thời gian xử lý trung bình làm tròn 1 chữ số thập phân (Q2 - `AVG`, `ROUND`). | `sql/my_queries.sql`<br>`scripts/seed.py` | **Hạo** (`@DMH554`) |
| **[#38](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/38)** | **F.3: Truy vấn Topic bị đánh giá tiêu cực (JOIN)** | Viết truy vấn SQL Q3 ghép bảng `feedback` và `interaction` qua `request_id` (`JOIN`), lọc phản hồi tiêu cực (`rating = -1`), đếm và chỉ ra các chủ đề cần cải thiện nội dung tri thức. | `sql/my_queries.sql` | **Lam** (`@LamNotNam1607`) |
| **[#39](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/39)** | **H2: Câu hỏi phân tích dữ liệu mở rộng** | Đặt câu hỏi quản trị thực tế về dữ liệu trợ lý (tỷ lệ fallback, khung giờ cao điểm, v.v.), viết câu truy vấn SQL tương ứng và lưu kết quả trích xuất vào `docs/lab5/h2_analysis.md`. | `sql/my_queries.sql`<br>`docs/lab5/h2_analysis.md` | **Hưng** (`@pghung2516-netizen`) |
| **[#40](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/40)** | **H3 Bonus: Đánh giá Thiết kế Schema (Design Review)** | Phân tích file `sql/bad_schema.sql`, chỉ ra 3 lỗi thiết kế nghiêm trọng (vi phạm bảo vệ dữ liệu cá nhân, thiếu khóa ngoại, chuẩn hóa 1NF) và trình bày cách kiến trúc 3 bảng Lab 5 giải quyết triệt để. | `sql/bad_schema.sql`<br>`docs/lab5/data_model.md` | **Đạt** (`@EddieOuttaHere`) |

---

## 👥 Phân chia công việc Lab 4 (Nhóm 7 thành viên - Đã hoàn thành)

| Issue | Đầu việc (Task) | Mô tả chi tiết phần việc cần làm | File liên quan | Người phụ trách (Assignee) |
| :---: | :--- | :--- | :--- | :---: |
| **[#22](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/22)** | **T1: Core Chat API** | Triển khai endpoint `POST /v1/chat`: nhận `ChatRequest`, chuyển tiếp vào `service.handle()`, sinh `request_id` ngẫu nhiên (12 ký tự hex) và trả về `ChatResponse`. | `src/assistant_api/main.py` | **Danh** (`@25127029-DBDANH`) |
| **[#18](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/18)** | **T2: Create Feedback** | Triển khai endpoint `POST /v1/feedback`: tiếp nhận `FeedbackIn` (chỉ cho phép rating -1, 0, 1), sinh ID tự tăng, lưu thời gian tạo UTC vào `feedback_store`, trả về `FeedbackOut` với mã `201 Created`. | `src/assistant_api/main.py` | **Khang** (`@ankhang-maker`) |
| **[#19](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/19)** | **T3: Admin Feedback Security** | Triển khai endpoint `GET /v1/feedback`: bảo vệ bằng dependency `require_admin` qua header `X-API-Key`, trả về danh sách phản hồi hoặc mã lỗi `401 Unauthorized`. | `src/assistant_api/main.py` | **Đăng** (`@dhdang2523-coder`) |
| **[#23](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/23)** | **T4: Weather API & 503 Handler** | Triển khai endpoint `GET /v1/weather`: kết nối `WeatherClient` (Open-Meteo), xử lý bắt ngoại lệ `ExternalServiceError` để trả về HTTP status `503 Service Unavailable`. | `src/assistant_api/main.py` | **Hạo** (`@DMH554`) |
| **[#20](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/20)** | **H1: Offices Directory & Tests** | Mở rộng class `OfficeDirectory` với method `all()` (sắp xếp danh sách theo tên), tạo route `GET /v1/offices`, và tự viết 2 unit test trong `tests/test_api.py` (check status 200 và có "Library"). | `src/assistant_core/knowledge.py`<br>`src/assistant_api/main.py`<br>`tests/test_api.py` | **Lam** (`@LamNotNam1607`) |
| **[#24](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/24)** | **Part F: Rate Limiting Bonus** | Tích hợp `RateLimiter` vào đầu endpoint `POST /v1/chat` để chặn spam theo IP (trả về mã `429 Too Many Requests`), mở bỏ `@pytest.mark.skip` để làm xanh test `test_rate_limit`. | `src/assistant_api/main.py`<br>`tests/test_api.py` | **Hưng** (`@pghung2516-netizen`) |
| **[#21](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/21)** | **H3 Bonus & H2 Reflection** | Tích hợp thêm 1 Public API bên ngoài (ví dụ Holiday/Currency) áp dụng timeout, retry, cache fallback + Soạn thảo đoạn văn phản tư H2 (5 dòng) giải thích sự khác biệt giữa gọi hàm trực tiếp và Web API. | `src/assistant_api/`<br>`docs/reflection.md` | **Đạt** (`@EddieOuttaHere`) |

---

## 📌 Quy trình làm việc và nộp bài (Áp dụng cho mọi Lab)

1. **Nhánh làm việc:** Mỗi thành viên checkout nhánh mới từ `main`: `feature/issue-<id>-<ten_task>`.
2. **Quy chuẩn Commit:** Đặt tên commit theo chuẩn: `<loại>(<module>): <mô tả> (closes #<issue_id>)`.
   * Ví dụ: `feat(db): implement add_feedback repository method (closes #34)`.
3. **Mở Pull Request (PR):**
   * Đảm bảo `pytest -q` pass toàn bộ test.
   * Chạy kiểm tra chuẩn mã nguồn: `ruff check .` và `ruff format --check .`.
   * Đính kèm kết quả chạy kiểm thử / minh chứng tương ứng trong nội dung PR.
4. **Tích hợp nhóm:** Tech Lead review, merge bản hoàn chỉnh vào `main` và đánh tag Git phiên bản (Lab 5 là `v0.5-data`).
