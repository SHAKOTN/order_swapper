import time

import pytest


@pytest.fixture
def patch_time(monkeypatch):
    def mock_time():
        return 123456.789

    monkeypatch.setattr(time, "time", mock_time)
    yield
