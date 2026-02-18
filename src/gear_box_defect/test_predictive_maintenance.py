import pytest

from .predictive_maintenance import (
    remaining_useful_life,
    health_score,
    maintenance_scheduler,
    failure_trend,
)
from .maintenance_utils import (
    predict_failure_cost,
    spare_parts_recommendation,
    root_cause_analysis,
    chatbot_response,
    digital_twin_simulation,
)
from .predict import predict_fault_and_severity


def test_rul_and_health():
    prob = 0.25
    assert remaining_useful_life(prob) == pytest.approx(375)
    assert health_score(prob) == pytest.approx(75)


def test_scheduler_messages():
    assert "routine" in maintenance_scheduler(100).lower()
    assert "immediate" in maintenance_scheduler(10).lower()


def test_trend_length():
    t = failure_trend([0.1, 0.2], periods=4)
    assert len(t) == 4
    assert all(0 <= v <= 1 for v in t)


def test_new_utilities():
    cost = predict_failure_cost(0.5)
    assert cost > 0
    parts = spare_parts_recommendation("gear_wear")
    assert "gear" in parts[0].lower()
    rc = root_cause_analysis("teeth_break", "SEVERE")
    assert "overload" in rc.lower()
    chat = chatbot_response("High Risk")
    assert "high" in chat.lower()
    sim = digital_twin_simulation(0.8)
    assert "imminent" in sim.lower()


def test_predict_integration(tmp_path):
    # create synthetic CSV file with required vibration columns
    import pandas as pd
    import numpy as np
    file = tmp_path / "dummy.csv"
    df = pd.DataFrame({
        "gearbox_vibration_x": np.random.randn(100),
        "gearbox_vibration_y": np.random.randn(100),
        "gearbox_vibration_z": np.random.randn(100),
    })
    df.to_csv(file, index=False)

    result = predict_fault_and_severity(str(file))
    # expect dataclass with fields
    assert hasattr(result, "fault")
    assert hasattr(result, "risk_label")
    assert hasattr(result, "failure_cost")

    # compatibility: if function returned a tuple we should be able to rebuild
    from .result import GearboxAnalysis
    tup = (
        result.fault,
        result.severity,
        result.rms,
        result.energy,
        result.recommendation,
        result.risk_label,
        result.risk_probability,
        result.remaining_life,
        result.schedule,
        result.health_score,
        result.trend,
        result.failure_cost,
        result.spare_parts,
        result.root_cause,
        result.chatbot_intro,
        result.digital_twin_summary,
    )
    converted = GearboxAnalysis(*tup)
    assert converted.fault == result.fault
    assert converted.health_score == result.health_score
