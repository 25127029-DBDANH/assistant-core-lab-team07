# Lab 7 — H2 Reflection: Google PAIR Guidebook

**Người thực hiện:** Đạt (`@EddieOuttaHere`) — Issue #70

---

> **Câu 1 — Ý tưởng đã áp dụng vào Lab 7 hôm nay:**
> Từ chương *Errors + Graceful Failure*, tôi đã áp dụng nguyên tắc "fail gracefully with a human in the loop" vào `ui/app.py` và `ui/logic.py`: khi backend không phản hồi, giao diện hiển thị thông báo lỗi thân thiện bằng `st.error` thay vì crash; khi trợ lý không tìm được câu trả lời (`escalate=True`), hệ thống chủ động chuyển tiếp người dùng đến Phòng Đào tạo phòng I.101 — đảm bảo người dùng luôn có lối thoát an toàn thay vì bị bỏ lại với màn hình trống.

> **Câu 2 — Ý tưởng đề xuất bổ sung thêm cho hệ thống:**
> Từ chương *Feedback + Control*, tôi đề xuất bổ sung tính năng cho phép người dùng **chỉnh sửa và gửi lại câu hỏi ngay trong chat bubble** (edit-and-retry): khi nhấn nút ✏️ trên tin nhắn vừa gửi, ô nhập liệu sẽ được tự động điền lại với nội dung cũ để người dùng có thể tinh chỉnh cách đặt câu hỏi — thực hiện quyền kiểm soát (*Control*) của người dùng và thu thập tín hiệu ngầm (*implicit feedback*) giúp cải thiện chất lượng truy xuất BM25 về lâu dài.
