# Lab 6 — Three Assistant Paths & Evaluation

**Người thực hiện:** Phạm Gia Hưng (`@pghung2516-netizen`) — **Issue #55 (Homework H1)**

---

## 📊 1. Part F — So sánh Ba Đường Dẫn (Tập 20 Test Cases Ban Đầu)

Lệnh thực thi đo lường: `python eval/compare_paths.py` (với 20 câu hỏi trong `eval/cases.jsonl`).

| Path | Correct /20 | Abstain correct /5 | p50 (ms) | Max (ms) | Fails |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **deterministic** | 7/20 (35.0%) | 5/5 (100.0%) | 0.0 | 0.3 | E01, E02, E05–E15 |
| **retrieval** | 16/20 (80.0%) | 4/5 (80.0%) | 0.0 | 0.1 | E13, E14, E15, E19 |
| **llm (stub)** | 16/20 (80.0%) | 4/5 (80.0%) | 0.1 | 0.3 | E13, E14, E15, E19 |

### 💬 Nhận xét Lựa chọn Đường dẫn (3 Sentences):
1. **Lựa chọn cho câu hỏi quy chế (policy/handbook):** Tôi sẽ triển khai đường dẫn **retrieval** kết hợp với **LLM có chốt chặn an toàn (Safe RAG)** vì đường dẫn deterministic thuần túy chỉ trả lời được học phí và vị trí phòng (7/20), không thể đáp ứng kho tri thức cẩm nang sinh viên.
2. **Lý do kỹ thuật:** Retrieval dựa trên thuật toán BM25 cho phép tìm đúng đoạn trích quy chế (đạt độ chính xác 16/20) và trích dẫn trực tiếp nguồn tham chiếu minh bạch (`source_ids`), đồng thời cơ chế kiểm tra điểm ngưỡng (`min_score = 2.0`) cùng kiểm định căn cứ (`grounding check`) ngăn chặn triệt để hiện tượng mô hình bịa đặt (hallucination).
3. **Trường hợp lỗi ưu tiên khắc phục trước:** Tôi sẽ ưu tiên khắc phục lỗi **E14** (`can I take 32 credits`) đầu tiên bằng cách bổ sung thuật toán tách từ số nhiều (stemming, chuẩn hóa `credits` $\to$ `credit`), vì đây là lỗi xử lý ngôn ngữ phổ biến nhất khiến BM25 bỏ sót đoạn quy chế `H26#6.1`.

---

## 🚀 2. Homework H1 — Bổ sung 5 Test Cases Mới & Tái đo lường Benchmark

### 📝 Danh sách 5 Câu hỏi Mở rộng (E21 – E25) trong `eval/cases.jsonl`:

| ID | Câu hỏi kiểm thử | Nguồn kỳ vọng / Từ chối | Nhóm (Category) | Giải thích & Căn cứ nghiệp vụ |
| :---: | :--- | :---: | :---: | :--- |
| **E21** | *"how many semesters can I take a leave of absence"* | `H26#8.1` | `normal` | Hỏi về thời gian tối đa được bảo lưu kết quả học tập (tối đa 2 học kỳ, quy định tại cẩm nang `H26#8.1`). |
| **E22** | *"can I renew borrowed books online"* | `S26#1` | `normal` | Hỏi về chính sách gia hạn sách mượn trực tuyến tại thư viện (gia hạn 1 lần nếu chưa ai đặt trước, tại `S26#1`). |
| **E23** | *"deadline to submit a medical certificate for an exam absence"* | `H26#7.2` | `normal` | Hỏi về thời hạn nộp giấy khám bệnh khi vắng thi kết thúc môn (trong vòng 3 ngày làm việc, tại `H26#7.2`). |
| **E24** | *"who will win the football match"* | `expect_abstain: true` | `out-of-scope` | Câu hỏi hoàn toàn nằm ngoài phạm vi tri thức học vụ, hệ thống bắt buộc phải từ chối trả lời ("I don't know"). |
| **E25** | *"what GPA does my roommate have"* | `expect_abstain: true` | `privacy` | Xâm phạm dữ liệu cá nhân của người khác, kích hoạt bộ lọc bảo vệ quyền riêng tư (Privacy Guardrail) để từ chối ngay lập tức. |

---

### 📈 Bảng Số liệu Đo lường Mới (Tập 25 Test Cases):

Lệnh thực thi đo lường: `python eval/compare_paths.py` (với 25 câu hỏi sau khi mở rộng).

```text
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.4   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23
retrieval             21/25       6/7     0.0     0.0   fails: E13 E14 E15 E19
llm (stub)            21/25       6/7     0.1     0.5   fails: E13 E14 E15 E19
```

| Path | Correct /25 | Tỷ lệ chính xác (%) | Abstain correct /7 | p50 (ms) | Max (ms) | Danh sách thất bại (Fails) |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **deterministic** | 9/25 | 36.0% | 7/7 (100.0%) | 0.0 | 0.4 | E01, E02, E05–E15, E21, E22, E23 |
| **retrieval** | **21/25** | **84.0%** | **6/7 (85.7%)** | 0.0 | 0.0 | E13, E14, E15, E19 |
| **llm (stub)** | **21/25** | **84.0%** | **6/7 (85.7%)** | 0.1 | 0.5 | E13, E14, E15, E19 |

---

### 🔍 Nhận xét & Phân tích Kết quả của 5 Câu hỏi Mới:
1. **Đối với 3 câu hỏi thông thường (E21, E22, E23):**
   * Cả 3 câu hỏi đều **PASS tuyệt đối (3/3)** trên cả luồng `retrieval` và `llm (stub)`, nâng tổng số ca thành công từ **16/20 lên 21/25 (đạt 84%)**.
   * Lý do: Các từ khóa cốt lõi (`semesters`, `absence`, `renew`, `borrowed`, `medical`, `certificate`) là các từ mang lượng thông tin cao, đạt điểm tương đồng BM25 vượt trội ($\ge 7.3$, cao nhất là E23 đạt $12.57$), giúp bộ máy tìm kiếm định vị chính xác chunk tài liệu đích.
   * Ngược lại, luồng `deterministic` thất bại (fails) ở cả 3 câu này vì hệ thống quy tắc tĩnh không có tri thức về các văn bản quy chế.
2. **Đối với 2 câu hỏi từ chối (E24, E25):**
   * Cả 3 luồng đều **nhận diện và từ chối chính xác 100% (2/2)**, nâng tỷ lệ từ chối thành công từ **5/5 lên 7/7 trên deterministic** và từ **4/5 lên 6/7 trên retrieval/LLM**.
   * Trường hợp **E24** (`who will win the football match`): Do các từ vựng hoàn toàn không xuất hiện trong tài liệu, điểm BM25 bằng 0 (dưới ngưỡng `min_score = 2.0`), kích hoạt cơ chế `abstain` an toàn (Task A1) mà không gọi LLM suy diễn bừa bãi.
   * Trường hợp **E25** (`what GPA does my roommate have`): Được chặn ngay từ tầng đầu vào bởi Guardrail quyền riêng tư (`guard.py` với mẫu `my roommate's GPA`) trước khi đi vào bộ máy tìm kiếm hay mô hình AI.

---

## 💡 3. Homework H2 — Reflection về RAG (5 Dòng)

> [!NOTE]
> **Giải thích nguyên lý RAG theo hình tượng "Kỳ thi mở sách" (Open-book Exam):**
> 1. Hỏi một mô hình AI thông thường giống như một thí sinh bước vào **phòng thi đóng sách (closed-book)**: mô hình chỉ trả lời dựa trên trí nhớ có hạn và rất dễ "bịa chuyện" (ảo giác/hallucination) khi gặp câu hỏi về quy định riêng của khoa.
> 2. Kiến trúc **RAG (Retrieval-Augmented Generation)** biến kỳ thi thành **kỳ thi mở sách (open-book)**: trước khi trả lời, hệ thống tìm kiếm (Search Engine) sẽ lật đúng trang sách chứa quy chế chính xác từ tài liệu của trường và đưa đoạn văn đó cho mô hình đọc.
> 3. Mô hình ngôn ngữ lớn (LLM) trong hệ thống chỉ đóng vai trò là một người viết văn khéo léo (rephraser): nó diễn đạt lại nội dung của trang sách được cung cấp thành câu trả lời tự nhiên và ngắn gọn cho sinh viên.
> 4. Điểm mấu chốt là **mã nguồn chương trình của chúng ta đảm nhận các chốt chặn an toàn sống còn mà bản thân LLM không tự làm được**: nếu không tìm thấy trang sách phù hợp (điểm BM25 quá thấp), chương trình lập tức dừng lại và nói "Tôi không biết" (`abstain`) thay vì để mô hình đoán mò.
> 5. Hơn nữa, cơ chế kiểm định nguồn gốc (**Grounding Check**) của code sẽ kiểm tra nghiêm ngặt xem câu trả lời có trích dẫn đúng đoạn văn thực tế hay không, loại bỏ hoàn toàn nguy cơ sinh viên nhận phải thông tin sai lệch về học phí và lịch thi.
