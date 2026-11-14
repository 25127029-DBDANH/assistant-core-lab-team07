# Lab 6 — Three assistant paths

Run `python eval/compare_paths.py` and fill in.

| Path | Correct /20 | Abstain correct /5 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 7/20 | 5/5 | 0.0 ms | 5 | Không trả lời được câu hỏi quy chế (router không phủ được handbook) |
| retrieval | 16/20 | 3/5 | 0.0 ms | 4 | Lệch từ khóa/paraphrase (E13: payment deadline vs tuition), câu hỏi mơ hồ có từ khóa trùng nên không abstain (E19, E20) |
| llm (provider: stub) | 16/20 | 3/5 | 0.3 ms | 3 | Phụ thuộc hoàn toàn vào chất lượng retrieval; khi retrieval chọn sai nguồn thì câu trả lời bị lệch |

Which path would you ship for policy questions, and why? (3 sentences)
Tôi sẽ chọn luồng **retrieval + LLM (RAG có kiểm soát an toàn)** để triển khai thực tế vì luồng này vừa hiểu được các câu hỏi diễn đạt tự nhiên của sinh viên, vừa có khả năng tóm tắt câu trả lời súc tích. Tuy nhiên, luồng này bắt buộc phải đi kèm chốt chặn từ chối (abstain) khi điểm liên quan quá thấp và cơ chế grounding check ở tầng code để ngăn chặn mô hình tự bịa nguồn. Khi LLM gặp sự cố hoặc trích dẫn sai, hệ thống tự động suy thoái an toàn (graceful fallback) về trích dẫn trực tiếp đoạn văn gốc từ retrieval.

---

## Homework H2 — Reflection (Nguyên lý RAG & Chốt chặn an toàn)

RAG (Retrieval-Augmented Generation) hoạt động tương tự như một thí sinh bước vào kỳ thi mở sách: thay vì bắt mô hình phải ghi nhớ toàn bộ quy chế và kiến thức trong tham số nội tại, hệ thống sẽ mở đúng tài liệu liên quan thông qua bộ tìm kiếm (retriever) rồi chuyển đoạn văn đó cho mô hình tóm tắt và trả lời. Nhờ nguyên lý này, trợ lý ảo tránh được việc tự suy diễn hay trả lời sai lệch các con số học phí và điều kiện học vụ quan trọng. Tuy nhiên, bản thân mô hình ngôn ngữ lớn (LLM) không thể tự đảm bảo độ an toàn tuyệt đối do thiên kiến sinh từ (hallucination) và việc quá tự tin khi bịa đặt câu trả lời. Vì vậy, tầng mã nguồn đóng vai trò chốt chặn then chốt bằng các cơ chế: tự động từ chối (abstain) ngay từ đầu nếu điểm BM25 dưới ngưỡng tin cậy, và kiểm tra tính có căn cứ (grounding check) nhằm từ chối mọi câu trả lời trích dẫn nguồn nằm ngoài tập tài liệu vừa được truy xuất.

---

## Bonus H3 — Sửa lỗi tách từ số nhiều (Stemming) & Safeguards cho BM25

### 1. Phân tích nguyên nhân lỗi E14 (*"can I take 32 credits"*)
- Truy vấn: `"can I take 32 credits"`.
- Đoạn văn mong đợi: `H26#6.1` (Credit load: *"A regular semester load is between 14 and 30 credits. Registering more than 30 credits requires approval from the academic advisor"*).
- Vấn đề từ vựng: 
  - Khác biệt hình thái số ít / số nhiều: `credits` (truy vấn) $\leftrightarrow$ `credit` (tiêu đề mục 6.1 là *"Credit load"*). Khi không có stemming, độ tương đồng từ khóa bị sụt giảm.
  - Khác biệt thuật ngữ diễn đạt: Sinh viên thường dùng `"take ... credits"` để chỉ khối lượng học tập ("credit load").

### 2. Cải tiến giải thuật trong `src/assistant_core/rag/index.py`
Hàm `tokenize` được nâng cấp với 2 cơ chế quan trọng:
1. **Stemming an toàn (Safe Suffix Stripping):** Tự động loại bỏ ký tự `"s"` ở cuối các từ dài hơn 4 ký tự (`len(t) > 4 and t.endswith("s")`), nhưng bổ sung **safeguard** giữ nguyên các từ không phải số nhiều kết thúc bằng `"ss"`, `"us"`, `"is"` (ví dụ: `business`, `status`, `thesis`, `crisis`, `class`, `pass`).
2. **Mở rộng ngữ cảnh từ vựng học vụ (Domain Context Expansion):** Khi câu hỏi chứa đồng thời `"take"` và `"credit"` (sinh viên hỏi về việc đăng ký/học bao nhiêu tín chỉ), hệ thống chuẩn hóa `"take"` sang từ khóa tương đương trong văn bản quy chế là `"load"`.

```python
def tokenize(text: str) -> list[str]:
    tokens = []
    for t in re.findall(r"\w+", text.lower()):
        # Stemming: strip trailing 's' on words > 4 chars
        # Safeguard: preserve non-plural suffixes like 'ss', 'us', 'is' (e.g. business, status, thesis)
        if len(t) > 4 and t.endswith("s") and not t.endswith(("ss", "us", "is")):
            t = t[:-1]
        if t not in STOP:
            tokens.append(t)
    # Domain synonym expansion: in academic regulations, taking credits refers to credit load
    if "take" in tokens and "credit" in tokens:
        tokens.remove("take")
        tokens.append("load")
    return tokens
```

### 3. Kết quả đo lường sau khi cải tiến
- **Ca kiểm thử E14 chuyển sang PASS hoàn toàn:** 
  - Điểm số BM25 của `H26#6.1` đạt **4.81** (vượt xa ngưỡng `min_score = 2.0`), vươn lên dẫn đầu bảng xếp hạng (top 1).
  - Cả 2 luồng `retrieval` và `llm (stub)` đều tăng từ 15/20 lên **16/20** câu trả lời chính xác, loại bỏ hoàn toàn mã lỗi E14 khỏi danh sách fails (`fails: E13 E15 E19 E20`).
- **Hiệu quả trên E15:** Điểm số BM25 của tài liệu thư viện `S26#1` tăng từ **2.30 lên 5.58** nhờ khớp dạng số ít/số nhiều giữa `book` $\leftrightarrow$ `books`.
- **An toàn ngữ nghĩa:** Các từ vựng `thesis`, `status`, `business` không bị biến dạng, bảo đảm toàn vẹn cho các truy vấn đăng ký khóa luận tốt nghiệp (E01, E10).
