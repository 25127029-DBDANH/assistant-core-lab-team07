# H2 Reflection — Gọi hàm trực tiếp vs. Web API

**Tên:** Đạt (EddieOuttaHere) — Issue #21

---

## So sánh: Gọi hàm trực tiếp và gọi qua Web API

Khi gọi hàm trực tiếp trong cùng một chương trình, kết quả trả về tức thì vì lời gọi diễn ra trong cùng tiến trình, không tốn chi phí mạng hay tuần tự hoá dữ liệu.
Ngược lại, khi gọi một Web API, yêu cầu phải được đóng gói thành HTTP, truyền qua mạng, xử lý ở server từ xa rồi phản hồi trở lại, nên độ trễ cao hơn và có nguy cơ thất bại do timeout hoặc lỗi kết nối.
Gọi hàm trực tiếp không cần quan tâm đến bảo mật hay định dạng dữ liệu, nhưng Web API buộc cả hai phía phải tuân thủ một hợp đồng (contract) rõ ràng — schema JSON, mã HTTP — giúp các ngôn ngữ và dịch vụ khác nhau có thể giao tiếp.
Vì Web API là dịch vụ bên ngoài, chúng ta phải xử lý ba tình huống mà gọi hàm nội bộ không bao giờ gặp: timeout (đặt giới hạn thời gian chờ), retry (thử lại khi thất bại tạm thời), và cache fallback (phục vụ dữ liệu cũ khi nguồn bị sập).
Tóm lại, gọi hàm trực tiếp phù hợp cho logic nội bộ vì đơn giản và nhanh, còn Web API phù hợp để tích hợp dịch vụ bên ngoài hoặc chia sẻ tính năng qua ranh giới hệ thống, nhưng đòi hỏi thiết kế phòng thủ hơn.

---

## H3 Bonus — Holiday API Integration

**API sử dụng:** [Nager.Date Public Holidays API](https://date.nager.at/api/v3)
**Base URL:** `https://date.nager.at/api/v3/PublicHolidays/{year}/{countryCode}`
**Lý do chọn:** API công khai, miễn phí, không cần key, dữ liệu ngày lễ quốc gia rõ ràng và ổn định.

### Các điểm kỹ thuật đã áp dụng

| Habit | Cài đặt | Lý do |
|---|---|---|
| **Timeout** | 5 giây (`timeout_s=5.0`) | Nager.Date thường phản hồi < 1 s; 5 s đủ rộng cho mạng chậm nhưng không block server lâu |
| **Retry** | 1 lần (tổng 2 lần thử) | Bao phủ lỗi mạng tạm thời; tránh DDoS vô tình |
| **Cache TTL** | 24 giờ (`cache_ttl_s=86_400`) | Danh sách ngày lễ không đổi trong ngày; giảm số lần gọi API |
| **Stale fallback** | Trả về cache cũ (đánh dấu `stale=True`) | Người dùng vẫn nhận được dữ liệu dù upstream sập |
| **HTTP 503** | Khi không có cache và upstream lỗi | Báo hiệu rõ ràng cho client biết dịch vụ ngoài không khả dụng |

### Endpoints mới

- `GET /v1/holidays?country=VN&year=2026` — Danh sách ngày lễ
- `GET /v1/holidays/next?country=VN` — Ngày lễ tiếp theo

### Tests đã thêm (trong `tests/test_api.py`)

- `test_holidays_ok` — Status 200, đúng country code và số lượng ngày lễ
- `test_holidays_contains_national_day` — Kiểm tra 2/9 có trong danh sách VN
- `test_holidays_503_when_upstream_down` — Trả 503 khi Nager.Date không phản hồi
- `test_holidays_stale_cache_on_failure` — Cache cũ được phục vụ khi upstream fail
- `test_next_holiday_returns_future_date` — Endpoint `/next` không crash
