# assistant-core-team07

Dự án Study Assistant - Môn CSC10014 (Practical Track).

* **Lab 3:** Tách script `assistant_monolith.py` thành package `assistant_core`.
* **Lab 4:** Chuyển đổi Study Assistant thành dịch vụ Web API qua HTTP bằng **FastAPI**, JSON, bảo mật API Key, gọi dịch vụ bên ngoài và kiểm thử tự động.
* **Lab 5:** Tích hợp cơ sở dữ liệu **SQLite** qua **SQLModel**, lưu trữ bền vững lịch sử tương tác (`Interaction`) và phản hồi (`Feedback`), bảo vệ quyền riêng tư người dùng.
* **Lab 6:** Tích hợp trí tuệ nhân tạo an toàn (**Safe RAG**) với bộ tìm kiếm BM25, mô hình ngôn ngữ có kiểm định trích dẫn nguồn (**Grounding Check**), cơ chế từ chối khi không chắc chắn (**Abstain / "I Don't Know"**) và bộ tiêu chuẩn đo lường Benchmark 3 đường dẫn.
* **Lab 7:** Xây dựng Giao diện Người dùng Web (**Streamlit UI**) thuần Python, kết nối Web API qua HTTP, xử lý các trạng thái lỗi và chuyển tiếp lịch thiệp (**Escalation**), thu thập phản hồi 👍/👎 và thử nghiệm Usability thực tế với người dùng bên ngoài.
* **Lab 8:** Kiểm thử hồi quy (**Regression Tests**) từ báo cáo lỗi thực tế, sử dụng VS Code Debugger và JSON logs, bảo vệ bí mật (**Secrets**), phòng thủ tấn công **Prompt Injection (G1)**, trao đổi kịch bản **Red-Team** với nhóm bạn và tổng hợp danh mục sự cố ($\ge 3$ Mitigations).

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

### 3. Khởi chạy Ứng dụng (2 Servers, 2 Terminals)

Hệ thống yêu cầu khởi chạy đồng thời cả Backend API và Giao diện Web:

* **Terminal 1 — Khởi chạy Backend API:**
  ```bash
  uvicorn assistant_api.main:create_app --factory --reload
  ```
  *(API chạy tại: `http://127.0.0.1:8000/`, Swagger UI: `http://127.0.0.1:8000/docs`)*

* **Terminal 2 — Khởi chạy Streamlit Web UI:**
  ```bash
  streamlit run ui/app.py
  ```
  *(Giao diện mở tự động trên trình duyệt tại: `http://localhost:8501`)*

### 4. Kiểm thử tự động

```bash
# Chạy toàn bộ unit test của trợ lý (bao gồm API, DB, RAG và UI)
pytest -q

# Chạy riêng bộ kiểm thử giao diện Web
pytest -q tests/test_ui.py

# Chạy bộ kiểm thử bài tập Streamlit cơ bản (U1-U4)
pytest -q practice/test_hello_streamlit.py

# Chạy bộ kiểm thử bảo mật, hồi quy & Red-Team (Lab 8)
pytest -q tests/test_security.py
pytest -q tests/test_my_regressions.py
pytest -q practice/test_grades_utils.py
python redteam/run_redteam.py

# Kiểm tra định dạng và chất lượng code
ruff check .
ruff format --check .
```

---

## 👥 Phân chia công việc Lab 8: Testing, Debugging & Red Teaming (Nhóm 7 thành viên)

> [!IMPORTANT]
> Trọng tâm Lab 8 là xây dựng **lưới an toàn (safety net)** cho toàn bộ trợ lý: sửa 3 seeded bugs với regression test, gỡ lỗi bằng Debugger & JSON logs, triển khai **Prompt Injection Guard (G1 — 12/12)**, viết $\ge 3$ regression tests cho các lỗi từ Tuần 7, trao đổi **Red-Team Exchange**, lập **Failure Catalogue ($\ge 3$ Mitigations đã kiểm thử)**, kiểm chứng hàm AI (**H1**), phản tư OWASP (**H2**) và điểm thưởng Bonus. Mỗi thành viên checkout nhánh riêng theo mã issue, hoàn thành task, mở PR và pass 100% CI để Tech Lead review và merge.

| Issue | Đầu việc (Task) | Mô tả chi tiết phần việc cần làm | File liên quan | Người phụ trách (Assignee) |
| :---: | :--- | :--- | :--- | :---: |
| **[#78](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/78)** | **Part D — Task G1: Prompt Injection Guard (12/12), Tích hợp CI & Tag `v0.8-tested`** | Bổ sung 2 regex còn thiếu vào `INJECTION_PATTERNS` trong `src/assistant_core/guard.py` (`reveal/show/print/repeat...` và `\byou are now\b`), gỡ `xfail` trong `tests/test_security.py`, đạt **12/12 passed** với `python redteam/run_redteam.py`. Cập nhật `.github/workflows/ci.yml` chạy thêm `run_redteam.py` trên mỗi PR, điều phối review/merge và gắn tag `v0.8-tested`. | `src/assistant_core/guard.py`<br>`tests/test_security.py`<br>`.github/workflows/ci.yml` | **Danh (Leader)** (`@25127029-DBDANH`) |
| **[#79](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/79)** | **Part B — Sửa Seeded Bugs (BUG-1 & BUG-2) kèm Regression Tests** | Áp dụng quy trình 4 bước (Reproduce $\rightarrow$ Failing Test $\rightarrow$ Fix $\rightarrow$ Keep Regression Test) cho BUG-1 (`average([])` crash `ZeroDivisionError`) và BUG-2 (`top_n` slice `ranked[:n - 1]` trả thiếu sinh viên). Viết 2 regression tests tương ứng trong `practice/test_grades_utils.py`. | `practice/grades_utils.py`<br>`practice/test_grades_utils.py` | **Khang** (`@ankhang-maker`) |
| **[#80](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/80)** | **Part B (BUG-3) & Part C: Sửa Mutable Default & Bug Report BUG-7** | Khắc phục lỗi mutable default `book={}` trong `add_grade` thành `book=None`, viết regression test chứng minh các lớp độc lập và hoàn thiện đủ **7/7 passing tests** cho `practice/test_grades_utils.py`. Tái hiện và lập báo cáo lỗi chuẩn cho **BUG-7** (*"two retakes"*) theo mẫu `worksheets/bug_report_template.md` vào `docs/lab8/bug_reports/BUG-7.md`. | `practice/grades_utils.py`<br>`practice/test_grades_utils.py`<br>`docs/lab8/bug_reports/BUG-7.md` | **Đăng** (`@dhdang2523-coder`) |
| **[#81](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/81)** | **Part E — $\ge 3$ Regression Tests Tuần 7 & Mitigation #2 (BUG-7)** | Triển khai bản vá Mitigation #2 trong `src/assistant_core/tools.py` xử lý số viết bằng chữ tiếng Anh (`"one"`–`"ten"`, khắc phục BUG-7 `"two retakes"`). Viết tối thiểu **3 regression tests** chuẩn hành vi trong `tests/test_my_regressions.py` cho BUG-7 và các quan sát Usability Lab 7. | `tests/test_my_regressions.py`<br>`src/assistant_core/tools.py` | **Hạo** (`@DMH554`) |
| **[#82](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/82)** | **Part F (F.2 & F.3) — Kịch bản Tấn công Red-Team & Báo cáo `redteam/report.md`** | Thiết kế **8–10 attack cases** phủ đủ 6 nhóm tấn công + 1–2 control cases trong `redteam/cases_for_partner.jsonl`. Chạy `python redteam/run_redteam.py` trên bộ test chuẩn và bộ test trao đổi từ nhóm bạn, lưu đầy đủ bảng kết quả vào `redteam/report.md`. | `redteam/cases_for_partner.jsonl`<br>`redteam/report.md` | **Lam** (`@LamNotNam1607`) |
| **[#83](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/83)** | **Part E & F.4 — Red-Team Exchange & Failure Catalogue ($\ge 3$ Mitigations)** | Hoàn thiện bảng debrief mọi ca FAIL vào `worksheets/redteam_exchange.md` và danh mục sự cố `worksheets/failure_catalogue.md` tổng hợp đủ $\ge 3$ mitigations đã triển khai, kiểm thử kèm tên test tương ứng. | `worksheets/redteam_exchange.md`<br>`worksheets/failure_catalogue.md` | **Hưng** (`@pghung2516-netizen`) |
| **[#84](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/84)** | **Homework H1, H2 & Bonus (+1.0đ Mitigation)** | H1: Chọn 1 hàm AI tạo từ các tuần trước, viết $\ge 5$ edge tests trong `tests/test_ai_proven.py` (rỗng, 0, số lớn, tiếng Việt, sai kiểu), sửa nếu fail và ghi `docs/ai-use-log.md`. H2: Viết 2 câu phản tư OWASP vào `docs/lab8/reflection.md`. Bonus: Triển khai thêm 1 mitigation mới cho phát hiện Red-Team kèm regression test. | `tests/test_ai_proven.py`<br>`docs/ai-use-log.md`<br>`docs/lab8/reflection.md`<br>`src/assistant_core/guard.py` | **Đạt** (`@EddieOuttaHere`) |

---

## 👥 Phân chia công việc Lab 7: A User Interface for the Assistant (Nhóm 7 thành viên)

> [!IMPORTANT]
> Trọng tâm Lab 7 là đưa Trợ lý vào môi trường tương tác thực tế với người dùng qua **Streamlit Web UI**, tuân thủ 4 nguyên tắc thiết kế AI (Google PAIR Guidebook): minh bạch khả năng, hiển thị nguồn trích dẫn (**Task L1**), xử lý lỗi và chuyển tiếp con người lịch thiệp (**Task L2**), thu thập phản hồi tiêu cực (**Task F1**), hoàn thiện Usability Checklist, thử nghiệm người dùng thực tế (**H1**) và điểm thưởng Bonus (**Streaming / Nicer Sources**). Mỗi thành viên checkout nhánh riêng theo mã issue, hoàn thành task, mở PR và pass 100% CI để Tech Lead review và merge.

| Issue | Đầu việc (Task) | Mô tả chi tiết phần việc cần làm | File liên quan | Người phụ trách (Assignee) |
| :---: | :--- | :--- | :--- | :---: |
| **[#64](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/64)** | **Part D — Task F1: Nút Đánh giá Tiêu cực 👎 & Quản lý Session State** | Triển khai nút `👎` tại cột `c2` trong `ui/app.py`: gửi feedback rating `-1` tới API backend qua `client.send_feedback(rid, -1)`, ghi nhận `rid` vào `st.session_state.rated` để ẩn nút sau khi vote, và hiển thị thông báo toast `"Thanks — we will look at this answer."`. Phụ trách review PR, cập nhật `README.md` hướng dẫn chạy 2 server, đóng milestone và gắn tag phát hành `v0.7-mvp`. | `ui/app.py`<br>`README.md` | **Danh (Leader)** (`@25127029-DBDANH`) |
| **[#65](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/65)** | **Part B — Task U1 & U2: Nhập liệu Tương tác & Phản hồi Lời chào (Streamlit Basics)** | Hoàn thiện Task U2 trong `practice/hello_streamlit.py`: tiếp nhận chuỗi tên từ `st.text_input("Your name")`, kiểm tra nếu `name` không rỗng thì hiển thị lời chào màu xanh `st.success(f"Hello, {name}!")`. Bổ sung test cases kiểm tra chuỗi rỗng và ký tự đặc biệt, pass 100% test `test_u1_title` và `test_u2_greeting` trong `practice/test_hello_streamlit.py`. | `practice/hello_streamlit.py`<br>`practice/test_hello_streamlit.py` | **Khang** (`@ankhang-maker`) |
| **[#66](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/66)** | **Part B — Task U3 & U4: Quản lý State Bộ Đếm & Xác thực Ràng buộc Tín chỉ** | Hoàn thiện Task U3 & U4 trong `practice/hello_streamlit.py`: duy trì bộ đếm qua `st.session_state.count`, tăng đếm khi nhấn nút `Click me`; xác thực input tín chỉ qua `st.number_input(...)`, hiển thị `st.error` nếu $>30$ tín chỉ và `st.info` nếu bình thường. Làm xanh 100% bộ test `practice/test_hello_streamlit.py` (4/4 passed). | `practice/hello_streamlit.py`<br>`practice/test_hello_streamlit.py` | **Đăng** (`@dhdang2523-coder`) |
| **[#67](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/67)** | **Part D — Task L1 & L2: Định dạng Nguồn Trích dẫn & Chỉ báo Escalation (UI Logic)** | Triển khai hàm `format_sources(sources)` (Task L1) ghép chuỗi trích dẫn nguồn quy chế và `status_note(result)` (Task L2) xử lý thông điệp chuyển tiếp Phòng Đào tạo I.101 (`escalate`) hoặc thông báo fallback tài liệu gốc (`degraded`) trong `ui/logic.py`. Gỡ bỏ nhãn `xfail` trên 2 test trong `tests/test_ui.py`, đảm bảo pass 100% test suite `test_ui.py` (7/7 passed). | `ui/logic.py`<br>`tests/test_ui.py` | **Hạo** (`@DMH554`) |
| **[#68](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/68)** | **Part E & D.4: Kiểm chứng 6 Trạng thái UI & Hoàn thiện Usability Checklist** | Khởi chạy song song 2 server, kiểm chứng thực tế 6 trạng thái giao diện theo Bảng D.4 (câu hỏi mẫu sidebar, hỏi quy chế, câu hỏi ngoài phạm vi, input rỗng, vote nút, lỗi sập backend). Kiểm tra hiển thị responsive trên kích thước điện thoại (`phone-width`), tích hoàn thành 10 tiêu chí trong `worksheets/usability_checklist.md` và lập báo cáo minh chứng tại `docs/lab7/ui_states_report.md`. | `worksheets/usability_checklist.md`<br>`docs/lab7/ui_states_report.md` | **Lam** (`@LamNotNam1607`) |
| **[#69](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/69)** | **Homework H1: Thử nghiệm Người dùng Thực tế (10-minute Usability Test) & Sửa lỗi UI** | Tiến hành thử nghiệm 10 phút với 1 người dùng ngoài nhóm theo 2 nhiệm vụ (điều kiện khóa luận 118 tín chỉ và nơi đổi thẻ sinh viên bị mất). Quan sát độc lập, ghi nhận 3 sự hiểu lầm/trở ngại vào `worksheets/user_test_observations.md`. Chọn 1 vấn đề để sửa trực tiếp trong mã nguồn UI, commit kèm ảnh chụp so sánh trước/sau khi sửa (before/after screenshot). | `worksheets/user_test_observations.md`<br>`ui/app.py` hoặc `ui/logic.py` | **Hưng** (`@pghung2516-netizen`) |
| **[#70](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/70)** | **Homework H2 & Bonus: Phản tư Google PAIR & Điểm thưởng Giao diện Nâng cao** | Đọc tài liệu Google PAIR Guidebook (*Feedback + Control*, *Errors + Graceful Failure*), viết đoạn văn phản tư H2 gồm đúng 2 câu lưu vào `docs/lab7/reflection.md`. Triển khai tính năng thưởng Bonus (+1.0 đ) trong `ui/app.py`: hiệu ứng gõ chữ (Streaming animation) bằng `st.write_stream` HOẶC nâng cấp trích dẫn nguồn bằng thẻ collapsible card (`st.expander`). | `docs/lab7/reflection.md`<br>`ui/app.py` | **Đạt** (`@EddieOuttaHere`) |

---

## 👥 Phân chia công việc Lab 6: Adding AI to the Assistant, Safely (Nhóm 7 thành viên)

> [!IMPORTANT]
> Trọng tâm Lab 6 là xây dựng cơ chế **RAG an toàn (Safe RAG)**, kiểm tra tính có căn cứ (**Grounding Check**), cơ chế từ chối khi không có dữ liệu (**Abstain**), khởi động Mini Search Engine, đo lường Benchmark 3 đường dẫn và giải quyết bài toán xử lý ngôn ngữ thực tế. Mỗi thành viên checkout nhánh riêng theo mã task, hoàn thành công việc, mở PR và pass 100% CI để Tech Lead review và merge.

| Issue | Đầu việc (Task) | Mô tả chi tiết phần việc cần làm | File liên quan | Người phụ trách (Assignee) |
| :---: | :--- | :--- | :--- | :---: |
| **[#49](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/49)** | **Part E — Task A1: Cơ chế Từ chối Trả lời ("I Don't Know")** | Triển khai TODO A1 trong `RagAnswerer.answer`: kiểm tra nếu không tìm thấy đoạn văn (`not hits`) hoặc điểm BM25 cao nhất nhỏ hơn ngưỡng tin cậy `self.min_score`, lập tức trả về `Response(answer=ESCALATE_MSG, intent=Intent.UNKNOWN, path="abstain", escalate=True, confidence=0.0)` trước khi gọi LLM; gỡ bỏ marker `xfail` trên test `test_abstain_when_nothing_relevant`. Phụ trách review PR, tích hợp nhóm và gắn tag phát hành `v0.6-ai`. | `src/assistant_core/rag/answerer.py`<br>`tests/test_rag.py` | **Danh (Leader)** (`@25127029-DBDANH`) |
| **[#51](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/51)** | **Part D — Task A2: Cơ chế Kiểm tra Trích dẫn Nguồn (Grounding Check)** | Triển khai TODO A2 trong hàm `parse_draft`: kiểm tra nếu mô hình không từ chối (`not draft.abstain`) thì bắt buộc phải có ít nhất 1 nguồn trích dẫn và toàn bộ nguồn đó phải là tập con của các đoạn tài liệu tìm thấy (`set(draft.source_ids) <= allowed_ids`), nếu vi phạm thì raise `ProviderError("answer cites sources that were not retrieved")`; gỡ bỏ marker `xfail` trên test `test_citation_of_unretrieved_source_is_rejected`. | `src/assistant_core/llm.py`<br>`tests/test_rag.py` | **Khang** (`@ankhang-maker`) |
| **[#52](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/52)** | **Part B — Task S1: Xây dựng Inverted Index (Mini Search)** | Hoàn thiện hàm `build_index(docs: dict[str, str])` trong `practice/mini_search.py`: tách từ qua `tokenize()`, loại bỏ stop words, xây dựng cấu trúc chỉ mục đảo ánh xạ từ từng từ vựng sang tập hợp ID các tài liệu chứa từ khóa đó (`dict[str, set[str]]`). Viết bổ sung test case kiểm tra tính toàn vẹn của chỉ mục với các từ khóa lặp và từ dừng trong `practice/test_mini_search.py`. | `practice/mini_search.py`<br>`practice/test_mini_search.py` | **Đăng** (`@dhdang2523-coder`) |
| **[#53](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/53)** | **Part B — Task S2 & S3: Thuật toán Score & Rank (Mini Search)** | Hoàn thiện hàm `search(index, query, k=2)` trong `practice/mini_search.py`: tính điểm tương đồng văn bản dựa trên tần số xuất hiện của các từ khóa câu hỏi trong tài liệu (S2), sau đó sắp xếp các tài liệu theo thứ tự điểm giảm dần và lấy top-$k$ kết quả cao nhất (S3). Chạy và pass 100% bộ test `practice/test_mini_search.py` (4/4 tests). | `practice/mini_search.py`<br>`practice/test_mini_search.py` | **Hạo** (`@DMH554`) |
| **[#54](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/54)** | **Part F: Đo lường Benchmark So sánh Ba Đường Dẫn & Báo cáo** | Thực thi kịch bản đo lường `python eval/compare_paths.py` trên 20 test cases mẫu trong `eval/cases.jsonl`, trích xuất bảng số liệu đo lường 3 cơ chế (`deterministic`, `retrieval`, `llm (stub)`). Cập nhật bảng kết quả vào `docs/lab6/path_comparison.md` và viết 3 câu nhận xét phân tích chuyên sâu (lựa chọn luồng cho handbook, lý do kỹ thuật, và đề xuất xử lý trường hợp lỗi E14/E15). | `eval/compare_paths.py`<br>`eval/cases.jsonl`<br>`docs/lab6/path_comparison.md` | **Lam** (`@LamNotNam1607`) |
| **[#55](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/55)** | **Homework H1: Thiết kế 5 Test Cases Mới & Tái đo lường Benchmark** | Thiết kế và bổ sung 5 câu hỏi kiểm thử mới (E21–E25) vào `eval/cases.jsonl`: gồm 3 câu hỏi thông thường kèm nguồn đối chiếu chính xác từ kho tài liệu `data/kb/` (`expect_source`), và 2 câu hỏi ngoài phạm vi hoặc xâm phạm quyền riêng tư yêu cầu từ chối (`expect_abstain: true`). Chạy lại benchmark trên tập 25 câu hỏi, cập nhật bảng so sánh mới và phân tích kết quả vào `docs/lab6/path_comparison.md`. | `eval/cases.jsonl`<br>`eval/compare_paths.py`<br>`docs/lab6/path_comparison.md` | **Hưng** (`@pghung2516-netizen`) |
| **[#56](https://github.com/25127029-DBDANH/assistant-core-lab-team07/issues/56)** | **Homework H2 Reflection & Bonus H3: Xử lý Từ vựng Số nhiều (Stemming)** | Soạn thảo đoạn văn Reflection H2 (5 dòng) giải thích nguyên lý hoạt động của RAG theo ẩn dụ "kỳ thi mở sách" và phân tích chốt chặn an toàn của code mà LLM không tự làm được. Đồng thời triển khai Bonus H3: trong `src/assistant_core/rag/index.py`, cải tiến hàm `tokenize` để tự động loại bỏ chữ `"s"` ở cuối các từ dài hơn 4 ký tự (xử lý số nhiều), chạy lại benchmark xác nhận case E14 chuyển sang pass và ghi nhận kết quả vào `docs/lab6/path_comparison.md`. | `docs/lab6/path_comparison.md`<br>`src/assistant_core/rag/index.py`<br>`eval/compare_paths.py` | **Đạt** (`@EddieOuttaHere`) |

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
