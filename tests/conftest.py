"""Shared pytest fixtures.

Owner: Member 7
Tests use the stub responder and the sample data in data/, so they run offline and give the same result every time.
"""

from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def settings() -> Settings:
    return Settings(data_dir=DATA_DIR)


@pytest.fixture
def service(settings: Settings) -> AssistantService:
    offices = OfficeDirectory.from_csv(DATA_DIR / "offices.csv")
    handbook = Handbook.from_json(DATA_DIR / "handbook.json")
    return AssistantService(settings, offices, handbook, StubLLMResponder())
