# Báo cáo kiểm tra trạng thái giao diện — Lab 7 (Issue #68)

**Ngày kiểm tra ban đầu:** 17/11/2026  
**Ngày cập nhật xác minh sau tích hợp toàn bộ PR (#64–#70):** 22/11/2026  
**Phạm vi:** Kiểm thử tự động toàn bộ test suite (`pytest -q`), kiểm thử end-to-end 6 trạng thái D.4 qua FastAPI backend thật (`create_app`) + `AssistantClient` + Streamlit UI (`ui/app.py`), và đối chiếu trực quan qua ảnh chụp màn hình (`docs/lab7/screenshots/after_fix.png`).

## Kết quả đối chiếu sáu trạng thái (Bảng D.4)

| # | Trạng thái cần kiểm tra | Kết quả trên nhánh `main` | Chi tiết xác minh |
|---|---|---|---|
| 1 | Chọn câu hỏi mẫu ở sidebar | **Đạt (PASS)** | Nút ví dụ ở sidebar (`EXAMPLES`) gán câu hỏi vào `st.session_state.pending` và tự động gửi qua luồng chat; kèm nút `🔄 New conversation` để reset phiên. |
| 2 | Hỏi quy chế và thấy nguồn `H26#5.3` | **Đạt (PASS)** | Hỏi `"Can I register my thesis with 118 credits?"` trả về nguồn `H26#5.3 — 5.3 Thesis registration` qua `format_sources` (L1) và thẻ gập mở `st.expander` (Bonus). |
| 3 | Hỏi ngoài phạm vi và thấy escalation tới I.101 | **Đạt (PASS)** | Hỏi `"what is the capital of France"` trả về `escalate=True`; `status_note` (L2) hiển thị hộp `st.info` hướng dẫn liên hệ `Training Office, room I.101`. |
| 4 | Gửi ô chat rỗng | **Đạt (PASS)** | `st.chat_input` chặn gửi chuỗi rỗng trên trình duyệt; `validate_input` trả về `"Please type a question."` trước khi gọi API. |
| 5 | Bấm 👍 / 👎, thấy cảm ơn và ẩn nút | **Đạt (PASS)** | Cả nút 👍 (`rating=+1`) và 👎 (`rating=-1`) gửi thành công HTTP `201 Created` tới `/v1/feedback`, hiển thị `st.toast`, lưu `request_id` vào `st.session_state.rated` và ẩn cặp nút. |
| 6 | Backend ngừng hoạt động | **Đạt (PASS)** | Khi backend không chạy, `client.healthy()` hiển thị `st.error` ở đầu trang; gửi câu hỏi trả về `"Cannot reach the assistant. Is the backend running?"` thay vì crash. |

## Kết quả kiểm thử tự động sau tích hợp

- `pytest -q`: **82 passed, 0 failed** (gồm 13/13 tests trong `tests/test_ui.py`).
- `pytest -q practice/test_hello_streamlit.py`: **6 passed, 0 failed** (U1–U4 + 2 edge cases).
- `ruff check .` & `ruff format --check .`: **100% clean**.
- `worksheets/usability_checklist.md`: **10/10 mục đã hoàn thành `[x]`**.

## Tệp đã đối chiếu

- `ui/app.py`
- `ui/api_client.py`
- `ui/logic.py`
- `tests/test_ui.py`
- `worksheets/usability_checklist.md`
- `docs/lab7/screenshots/after_fix.png`
