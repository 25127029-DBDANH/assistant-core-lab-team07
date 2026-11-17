# Báo cáo kiểm tra trạng thái giao diện — Lab 7 (Issue #68)

**Ngày kiểm tra:** 17/11/2026  
**Phạm vi:** Đọc mã nguồn hiện có trên nhánh `main` và đối chiếu sáu trạng thái trong D.4. Đây chưa phải kiểm thử end-to-end trên trình duyệt.

## Kết quả đối chiếu sáu trạng thái

| # | Trạng thái cần kiểm tra | Kết quả trên mã nguồn `main` | Nhận xét |
|---|---|---|---|
| 1 | Chọn câu hỏi mẫu ở sidebar | Có xử lý | Nút mẫu lưu câu hỏi vào session state; phần gửi câu hỏi chạy qua luồng chat chung. Chưa chạy tương tác trên trình duyệt. |
| 2 | Hỏi quy chế và thấy nguồn `H26#5.3` | Chưa đạt | `format_sources` trong `ui/logic.py` vẫn là TODO và ném `NotImplementedError`; test tương ứng đang được đánh dấu `xfail`. Logic này thuộc issue #67. |
| 3 | Hỏi ngoài phạm vi và thấy escalation tới I.101 | Chưa đạt | `status_note` vẫn là TODO và ném `NotImplementedError`; test tương ứng đang được đánh dấu `xfail`. Logic này thuộc issue #67. |
| 4 | Gửi ô chat rỗng | Có xử lý | `validate_input` trả thông báo thân thiện; luồng UI chỉ gọi API khi nội dung hợp lệ. Chưa xác nhận request bằng runtime. |
| 5 | Bấm 👍 / 👎, thấy cảm ơn và ẩn nút | Có xử lý trong mã | UI gửi mức đánh giá, ghi request vào trạng thái đã vote và gọi toast. Chưa xác nhận phản hồi API/runtime. |
| 6 | Backend ngừng hoạt động | Có xử lý trong mã | Client bắt lỗi kết nối và trả thông báo `Cannot reach the assistant...`; UI hiển thị lỗi thay cho việc dừng trang. Chưa tắt backend để kiểm thử runtime. |

## Giới hạn kiểm thử

- Đã chạy `pytest -q tests/test_ui.py` bằng môi trường Python có sẵn: **6 passed, 2 xfailed, 1 failed**. Test nút 👎 không khởi chạy được vì môi trường thiếu `streamlit`; hai ca xfail là kiểm thử nguồn trích dẫn và escalation đang chờ TODO của issue #67.
- Chưa thể xác nhận kết quả trực quan, tương phản hoặc bố cục ở `phone-width` từ việc đọc mã nguồn.
- Nhánh `main` hiện còn hai TODO của issue #67, nên không thể đánh dấu checklist hoàn tất hoặc xác nhận trạng thái 2 và 3 đạt.
- Cần bổ sung `streamlit` vào môi trường kiểm thử, chạy lại sáu kịch bản trên ứng dụng sau khi issue #67 được tích hợp, đồng thời kiểm tra giao diện ở kích thước điện thoại. Các mục chưa được kiểm chứng được giữ trống trong checklist.

## Tệp đã đối chiếu

- `ui/app.py`
- `ui/api_client.py`
- `ui/logic.py`
- `tests/test_ui.py`
- `worksheets/usability_checklist.md`
