from typing import Protocol
from assistant_core.errors import ProviderError
# Lưu ý: import Rule từ models hoặc knowledge tuỳ cách nhóm bạn đặt
# từ models import Rule hoặc dataclass Rule

class Responder(Protocol):
    """Giao diện chung (Protocol) cho tất cả các bộ sinh phản hồi."""
    def explain(self, question: str, rule) -> str:
        ...

class TemplateResponder:
    """Trả lời thuần template dựa vào quy chế (dùng làm Fallback khi AI lỗi)."""
    def explain(self, question: str, rule) -> str:
        return f"{rule.title}: {rule.text}"

class StubLLMResponder:
    """Giả lập LLM: có thể bật cờ fail=True để chủ động test kịch bản LLM sập."""
    def __init__(self, fail: bool = False):
        self.fail = fail

    def explain(self, question: str, rule) -> str:
        if self.fail:
            raise ProviderError("stub provider unavailable")
        return f"Based on '{rule.title}': {rule.text}"