from rl_pipeline.health import health_check


def test_health() -> None:
    assert health_check() == {"status": "ok"}
