# Lab 6 — Three assistant paths

Run `python eval/compare_paths.py` and fill in.

| Path | Correct /20 | Abstain correct /5 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 7/20 | 5/5 | 0.02 ms | 5 | Không trả lời được câu hỏi quy chế (router không phủ được handbook) |
| retrieval | 15/20 | 3/5 | 0.04 ms | 4 | Lệch từ khóa/paraphrase (E13), câu hỏi mơ hồ có từ khóa trùng nên không abstain (E19, E20) |
| llm (provider: stub) | 15/20 | 3/5 | 0.26 ms | 3 | Phụ thuộc hoàn toàn vào chất lượng retrieval; khi retrieval chọn sai nguồn thì câu trả lời bị lệch |

Which path would you ship for policy questions, and why? (3 sentences)
Tôi sẽ chọn luồng **retrieval + LLM (RAG có kiểm soát an toàn)** để triển khai thực tế vì luồng này vừa hiểu được các câu hỏi diễn đạt tự nhiên của sinh viên, vừa có khả năng tóm tắt câu trả lời súc tích. Tuy nhiên, luồng này bắt buộc phải đi kèm chốt chặn từ chối (abstain) khi điểm liên quan quá thấp và cơ chế grounding check ở tầng code để ngăn chặn mô hình tự bịa nguồn. Khi LLM gặp sự cố hoặc trích dẫn sai, hệ thống tự động suy thoái an toàn (graceful fallback) về trích dẫn trực tiếp đoạn văn gốc từ retrieval.

---

## Homework H2 — Reflection (Nguyên lý RAG & Chốt chặn an toàn)

RAG (Retrieval-Augmented Generation) hoạt động tương tự như một thí sinh bước vào kỳ thi mở sách: thay vì bắt mô hình phải ghi nhớ toàn bộ quy chế và kiến thức trong tham số nội tại, hệ thống sẽ mở đúng tài liệu liên quan thông qua bộ tìm kiếm (retriever) rồi chuyển đoạn văn đó cho mô hình tóm tắt và trả lời. Nhờ nguyên lý này, trợ lý ảo tránh được việc tự suy diễn hay trả lời sai lệch các con số học phí và điều kiện học vụ quan trọng. Tuy nhiên, bản thân mô hình ngôn ngữ lớn (LLM) không thể tự đảm bảo độ an toàn tuyệt đối do thiên kiến sinh từ (hallucination) và việc quá tự tin khi bịa đặt câu trả lời. Vì vậy, tầng mã nguồn đóng vai trò chốt chặn then chốt bằng các cơ chế: tự động từ chối (abstain) ngay từ đầu nếu điểm BM25 dưới ngưỡng tin cậy, và kiểm tra tính có căn cứ (grounding check) nhằm từ chối mọi câu trả lời trích dẫn nguồn nằm ngoài tập tài liệu vừa được truy xuất.

---

## Bonus H3 — Sửa lỗi tách từ số nhiều (Stemming) cho BM25

### 1. Phân tích nguyên nhân lỗi E14 (*"can I take 32 credits"*)
- Truy vấn: `"can I take 32 credits"`.
- Tokenizer gốc: tách thành `['take', '32', 'credits']` (loại bỏ từ dừng `can`, `i`).
- Đoạn văn mong đợi: `H26#6.1` (Credit load: *"A regular semester load is between 14 and 30 credits. Registering more than 30 credits requires approval from the academic advisor"*).
- Vấn đề từ vựng: Trong tiếng Anh và tài liệu học vụ, từ khóa xuất hiện dưới cả hai dạng số ít (`credit`) và số nhiều (`credits`), ví dụ tiêu đề mục 6.1 là *"Credit load"*. Khi tìm kiếm chính xác, sự sai biệt hình thái này làm giảm độ khớp từ vựng giữa câu hỏi và tài liệu. Tương tự, ở ca kiểm thử E15 (*"how long can I keep a library book"*), từ khóa câu hỏi là số ít `book` trong khi tài liệu `S26#1` dùng số nhiều `books`.

### 2. Giải pháp cài đặt trong `src/assistant_core/rag/index.py`
Cải tiến hàm `tokenize` để tự động loại bỏ hậu tố `"s"` ở cuối các từ có độ dài lớn hơn 4 ký tự:
```python
def tokenize(text: str) -> list[str]:
    tokens = []
    for t in re.findall(r"\w+", text.lower()):
        if len(t) > 4 and t.endswith("s"):
            t = t[:-1]
        if t not in STOP:
            tokens.append(t)
    return tokens
```

### 3. Kết quả đo lường sau khi áp dụng Stemming
- **Độ tương đồng tài liệu:** Từ khóa `credits` được chuẩn hóa thành `credit`, giúp tăng tần số từ vựng khớp với các đoạn văn quy chế tín chỉ (`H26#6.1`, `F26#1`).
- **Hiệu quả rõ rệt trên E15:** Điểm số BM25 của tài liệu mượn sách thư viện `S26#1` tăng vọt từ **2.30 lên 5.58** nhờ khớp dạng từ `book` $\leftrightarrow$ `books`.
- **Hạn chế của mô hình từ khóa thuần túy:** Với câu E14, từ `"take"` có IDF rất cao (xuất hiện ở ít tài liệu) khiến đoạn `H26#7.2` (Exam absence có cụm *"take the exam"*) vẫn giữ điểm cao. Điều này chứng minh rằng bên cạnh stemming, hệ thống thực tế cần kết hợp Hybrid Index hoặc Semantic Embeddings để hiểu đúng ngữ nghĩa của toàn bộ câu hỏi.
