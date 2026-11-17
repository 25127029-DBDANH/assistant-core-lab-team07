# Lab 7 — Usability checklist (tick before your user test)

- [x] The first screen says what the assistant can do, with example questions (verified in `ui/logic.py` and `ui/app.py`)
- [x] Empty or too-long input shows a friendly message (verified in `ui/logic.py` and `ui/app.py`)
- [x] While waiting, the user sees "Thinking…" (verified in `ui/app.py`)
- [ ] Every answer from documents shows its sources (blocked: `format_sources` is not implemented on the current `main` branch; see issue #67)
- [ ] "I don't know" answers tell the user who can help (blocked: `status_note` is not implemented on the current `main` branch; see issue #67)
- [x] If the backend is down, the page says so clearly (verified in `ui/api_client.py` and `ui/app.py`)
- [x] Each answer has 👍 / 👎, and clicking gives a "thanks" message (verified in `ui/app.py`)
- [x] The page says it is an AI assistant (verified in `ui/app.py`)
- [ ] Text is readable (size, contrast); buttons have clear labels (requires visual review in a browser)
- [ ] Works on a phone-width window (requires visual review at phone width)

> Các mục đã đánh dấu chỉ được xác nhận bằng đọc mã nguồn. Các mục cần giao diện chạy thật được để trống cho đến khi có kiểm thử trực quan; không xem đây là kết quả user test.
