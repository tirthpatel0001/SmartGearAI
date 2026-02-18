from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GearboxAnalysis:
    # diagnosis outputs
    fault: str
    severity: str
    rms: float
    energy: float
    recommendation: str

    # predictive maintenance
    risk_label: str
    risk_probability: float
    remaining_life: float
    schedule: str
    health_score: float
    trend: List[float]

    # additional features
    failure_cost: float
    spare_parts: List[str]
    root_cause: str
    chatbot_intro: str
    digital_twin_summary: str

    # You can extend with more fields later
