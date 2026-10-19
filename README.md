# assistant-core-team07

Lab 3 (CSC10014): tách script `assistant_monolith.py` thành package `assistant_core` dễ đọc, dễ cấu hình, dễ kiểm thử và dễ mở rộng.
Hành vi giữ nguyên (chào hỏi, tra văn phòng, tính học phí, tra sổ tay có nguồn); chỉ đổi cấu trúc. Phần AI vẫn là stub, tuần 4 mới thêm AI thật.

## Cài đặt (Windows, Git Bash)

```bash
git clone git@github.com:<owner>/assistant-core-team07.git
cd assistant-core-team07
py -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
cp .env.example .env        # .env KHÔNG được commit
pytest -q
ruff check .
```

Nếu `pip install` báo lỗi build `pydantic-core`: kiểm tra `requirements.txt` đang ghim `pydantic==2.12.5` (bản 2.9.2 không có gói dựng sẵn cho Python 3.14).

## Cấu trúc và người phụ trách

| Phần | File | Người phụ trách |
|---|---|---|
| Khung dự án, `errors.py`, `models.py`, `service.py`, `__main__.py`, tích hợp, tag | nhiều file | Member 1 |
| Cấu hình và log | `config.py`, `.env.example`, `logging_setup.py` | Member 2 |
| Nguồn tri thức | `knowledge.py` (văn phòng, sổ tay) | Member 3 |
| Tính học phí | `tools.py`, `tests/test_tools.py` | Member 4 |
| Bộ trả lời | `responder.py` (Protocol, Template, StubLLM) | Member 5 |
| Bộ định tuyến | `router.py`, `tests/test_router.py` | Member 6 |
| Tài liệu và test dịch vụ | `docs/architecture.md`, `tests/test_service.py`, `tests/conftest.py`, CI | Member 7 |

## Quy trình làm việc

1. Không push thẳng vào `main`. Mỗi người một nhánh `feat/<module>`, ví dụ `feat/tools`.
2. Chỉ sửa file thuộc phần mình. Cần đổi `errors.py` hoặc `models.py` thì báo Member 1.
3. Mỗi PR: `pytest -q` pass, `ruff check .` sạch, có người khác Approve, ghi mục AI use.
4. Commit dạng `loại(module): mô tả`, ví dụ `feat(tools): add tuition calculation`.
5. Không đưa bí mật hay `.env` lên Git, không log nội dung đầy đủ tin nhắn của người dùng.

## Nguồn tham chiếu

Script gốc nằm ở `lab03/monolith/assistant_monolith.py` trong repo của giảng viên (`public_materials`).
