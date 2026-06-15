import json
from collections import defaultdict

class ReportGenerator:
    """
    Utility class to format the list of RefactoringRecommendations 
    into different report formats.
    """

    @staticmethod
    def to_json(recommendations: list) -> str:
        """
        Returns a JSON string representation of recommendations.
        """
        return json.dumps([rec.to_dict() for rec in recommendations], indent=4)

    @staticmethod
    def to_text(recommendations: list) -> str:
        """
        Returns a human-readable text report grouped by file.
        """
        if not recommendations:
            return "No refactoring recommendations found. Your code looks clean!"

        report = ["Clean Code Refactoring Report", "=" * 50]
        
        # Group by file path
        grouped_recs = defaultdict(list)
        for rec in recommendations:
            grouped_recs[rec.file_path].append(rec)

        for file_path, recs in grouped_recs.items():
            report.append(f"\nFile: {file_path}")
            report.append("-" * 50)
            
            # Sort recommendations by line number if available
            sorted_recs = sorted(
                recs, 
                key=lambda r: r.line_number if r.line_number is not None else 999999
            )

            for i, rec in enumerate(sorted_recs, 1):
                line_str = f"Line {rec.line_number}" if rec.line_number else "Global"
                report.append(f"{i}. [{rec.severity.value}] {rec.rule_name} ({line_str})")
                report.append(f"   Target: {rec.target_name}")
                report.append(f"   Issue: {rec.description}")
                report.append(f"   Suggestion: {rec.suggestion}\n")

        return "\n".join(report)
