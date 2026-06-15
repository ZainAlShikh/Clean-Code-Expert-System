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
    """
    Data class representing a suggested refactoring or clean code issue.
    """
    rule_name: str
    description: str
    target_name: str  # Name of the function, variable, or class
    file_path: str    # Path to the file containing the issue
    line_number: Optional[int] = None
    severity: Severity = Severity.MEDIUM
    suggestion: str = ""

    def to_dict(self):
        return {
            "rule_name": self.rule_name,
            "description": self.description,
            "target_name": self.target_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "severity": self.severity.value,
            "suggestion": self.suggestion
        }
