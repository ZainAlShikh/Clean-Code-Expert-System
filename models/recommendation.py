from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RefactoringRecommendation:
    rule_name: str
    description: str
    target_name: str
    file_path: str
    line_number: Optional[int] = None
    severity: Severity = Severity.MEDIUM
    suggestion: str = ""
    rule_id: str = ""
    condition: str = ""
    violation_type: str = ""
    strategy: str = ""
    status: str = "FIRED"

    def to_dict(self):
        return {
            "rule_name": self.rule_name,
            "description": self.description,
            "target_name": self.target_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "severity": self.severity.value,
            "suggestion": self.suggestion,
            "rule_id": self.rule_id,
            "condition": self.condition,
            "violation_type": self.violation_type,
            "strategy": self.strategy,
            "status": self.status
        }
