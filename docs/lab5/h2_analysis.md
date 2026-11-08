# Lab 5 — Homework H2: Phân tích Dữ liệu Trợ lý Mở rộng (Assistant Data Analysis)
**Người thực hiện:** Phạm Gia Hưng (`@pghung2516-netizen`) — **Issue #39 (H2 Analysis)**

---

## 🎯 1. Bối cảnh & Mục tiêu Phân tích

Trong quá trình vận hành Study Assistant, bên cạnh các chỉ số cơ bản như số lượng yêu cầu theo từng ý định (F1) hay độ trễ trung bình (F2), đội ngũ quản trị hệ thống cần hiểu sâu hơn về **chất lượng câu trả lời** và **mức độ hài lòng của sinh viên**.

Hệ thống ghi nhận trạng thái của mỗi phản hồi qua hai cờ boolean quan trọng:
* `resolved`: Liệu trợ lý có nhận diện và giải quyết được yêu cầu hay không (`0` = unknown / bot không biết trả lời).
* `degraded`: Liệu câu trả lời có phải sử dụng cơ chế dự phòng (fallback / backup answer) do thiếu dữ liệu hoặc dịch vụ ngoài phản hồi chậm/lỗi hay không.

### Câu hỏi Quản trị Đặt ra:
1. **Câu hỏi trọng tâm:** *Tỷ lệ câu trả lời phải sử dụng phương án dự phòng (`degraded` / fallback) là bao nhiêu theo từng nhóm Intent, và mức độ tin cậy (`resolved`) của từng Intent ra sao?*
2. **Câu hỏi mở rộng (Tác động người dùng):** *Khi câu trả lời bị rơi vào trạng thái degraded, tỷ lệ đánh giá tiêu cực (thumbs-down `rating = -1`) từ sinh viên tăng lên như thế nào so với các câu trả lời bình thường?*
3. **Phân tích hành vi phiên (Session behavior):** *Số lượng phiên trò chuyện (`chat_session`) và số lượt tương tác trung bình trên mỗi phiên là bao nhiêu?*

---

## 🔍 2. Phân tích Chi tiết & Câu lệnh SQL

### 2.1. Phân tích Tỷ lệ Degraded & Độ tin cậy theo từng Intent

#### Câu lệnh SQL thực thi:
```sql
SELECT 
    intent,
    COUNT(*) AS total_requests,
    SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) AS resolved_count,
    ROUND(100.0 * SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS resolved_rate_pct,
    SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) AS degraded_count,
    ROUND(100.0 * SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS degraded_rate_pct,
    ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY total_requests DESC;
```

#### Kết quả trích xuất từ `assistant.db` (300 tương tác mẫu):
| Intent | Tổng yêu cầu (`total_requests`) | Đã giải quyết (`resolved`) | Tỷ lệ giải quyết (%) | Số lượt dự phòng (`degraded`) | Tỷ lệ dự phòng (`%`) | Độ trễ TB (`latency_ms`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **rule** (quy chế) | 140 | 140 | 100.00% | 34 | **24.29%** | **76.2 ms** |
| **fee** (học phí) | 61 | 61 | 100.00% | 1 | 1.64% | 5.1 ms |
| **office** (văn phòng) | 48 | 48 | 100.00% | 1 | 2.08% | 3.4 ms |
| **greeting** (chào hỏi) | 26 | 26 | 100.00% | 2 | 7.69% | 2.4 ms |
| **unknown** (chưa rõ) | 26 | 0 | **0.00%** | 0 | 0.00% | 8.1 ms |

#### 💡 Nhận xét & Ý nghĩa Quản trị:
* **Nhóm Quy chế (`rule`) chiếm lưu lượng cao nhất (140/301 ~ 46.5%)** nhưng đồng thời có **tỷ lệ degraded cao vượt trội (24.29%)** và độ trễ phản hồi cao nhất (76.2 ms). Điều này phản ánh các câu hỏi quy chế thường phức tạp, phải tra cứu nhiều điều khoản hoặc gọi fallback khi không match chính xác điều luật.
* **Các nhóm Nghiệp vụ cố định (`fee`, `office`)** hoạt động cực kỳ ổn định với tỷ lệ degraded rất thấp (< 2.1%) và độ trễ phản hồi chỉ từ 3 - 5 ms.
* **Nhóm `unknown` chiếm 8.6% tổng lượt hỏi**, toàn bộ không được giải quyết (`resolved = 0`). Đây là nhóm câu hỏi nằm ngoài phạm vi tri thức hiện tại của trợ lý.

---

### 2.2. Tác động của Degraded Response đến Mức độ Hài lòng (Feedback)

Để kiểm chứng giả thuyết *"Câu trả lời dự phòng (degraded) làm giảm nghiêm trọng sự hài lòng của sinh viên"*, chúng ta thực hiện phép `JOIN` giữa bảng `interaction` và `feedback`.

#### Câu lệnh SQL thực thi:
```sql
SELECT 
    CASE WHEN i.degraded = 1 THEN 'Degraded (Fallback)' ELSE 'Normal' END AS answer_quality,
    COUNT(f.id) AS total_feedback,
    SUM(CASE WHEN f.rating = 1 THEN 1 ELSE 0 END) AS positive_count,
    SUM(CASE WHEN f.rating = -1 THEN 1 ELSE 0 END) AS negative_count,
    ROUND(100.0 * SUM(CASE WHEN f.rating = -1 THEN 1 ELSE 0 END) / COUNT(f.id), 2) AS negative_rate_pct
FROM interaction i
JOIN feedback f ON i.request_id = f.request_id
GROUP BY i.degraded;
```

#### Kết quả trích xuất từ `assistant.db`:
| Chất lượng câu trả lời | Tổng lượt feedback | Đánh giá tích cực (+1) | Đánh giá tiêu cực (-1) | Tỷ lệ tiêu cực (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Normal** (Phản hồi chuẩn xác) | 78 | 61 | 17 | **21.79%** |
| **Degraded** (Phương án dự phòng) | 18 | 0 | 18 | **100.00%** |

#### 💡 Phát hiện Quản trị Quan trọng (Key Finding):
* **100% người dùng nhận câu trả lời degraded đều đánh giá tiêu cực (-1)!** Không có bất kỳ đánh giá tích cực nào dành cho các phản hồi dự phòng.
* Trong khi đó, đối với câu trả lời chuẩn xác (Normal), tỷ lệ hài lòng đạt **78.21%** (61/78).
* **Kết luận:** Trải nghiệm người dùng tỷ lệ nghịch trực tiếp với cờ `degraded`. Việc giảm thiểu tỷ lệ fallback chính là đòn bẩy lớn nhất để nâng cao chất lượng phục vụ của trợ lý ảo.

---

### 2.3. Phân tích Hành vi Phiên hội thoại (Session Engagement)

Xem xét sinh viên thường tương tác bao nhiêu câu hỏi trong mỗi phiên trò chuyện ẩn danh.

#### Câu lệnh SQL thực thi:
```sql
SELECT 
    COUNT(DISTINCT s.id) AS total_sessions,
    COUNT(i.id) AS total_interactions,
    ROUND(1.0 * COUNT(i.id) / COUNT(DISTINCT s.id), 2) AS avg_interactions_per_session
FROM chat_session s
LEFT JOIN interaction i ON s.id = i.session_id;
```

#### Kết quả trích xuất:
| Tổng số phiên (`total_sessions`) | Tổng lượt tương tác (`total_interactions`) | Trung bình tương tác / phiên |
| :---: | :---: | :---: |
| **59** | **301** | **5.10** |

#### 💡 Nhận xét:
* Mỗi phiên hội thoại kéo dài trung bình **~5.1 lượt trao đổi**. Điều này chứng minh sinh viên không chỉ hỏi một câu đơn lẻ rồi rời đi mà có xu hướng đặt nhiều câu hỏi tiếp nối (follow-up questions).
* Kiến trúc lưu trữ với khóa ngoại `interaction.session_id REFERENCES chat_session(id)` cho phép nhóm phát triển theo dõi toàn bộ luồng hội thoại của phiên một cách an toàn (thông qua mã băm ẩn danh SHA-256 có muối) mà không xâm phạm quyền riêng tư.

---

## 📋 3. Đề xuất Hành động cho Đội ngũ Phát triển (Actionable Recommendations)

1. **Ưu tiên làm giàu dữ liệu Quy chế Đào tạo (`rule`):**
   * Tập trung bổ sung tri thức và mở rộng từ khóa cho 2 topic đang có nhiều phản hồi tiêu cực nhất trong nhóm rule (đặc biệt là `H26-5.3` và `H26-4.2`).
2. **Cải tiến thông điệp khi Fallback (Graceful Degradation):**
   * Thay vì chỉ trả lời chung chung khi rơi vào trạng thái degraded, trợ lý nên cung cấp kèm liên kết đến cẩm nang sinh viên chính thức hoặc số điện thoại phòng Đào tạo để người dùng vẫn nhận được giá trị thay vì chỉ nhận sự thất vọng.
3. **Giám sát Dashboard định kỳ:**
   * Tích hợp chỉ số `Degraded Rate %` và `Negative Feedback Rate %` vào hệ thống giám sát thời gian thực để phát hiện sớm các đợt sụt giảm chất lượng dịch vụ.
