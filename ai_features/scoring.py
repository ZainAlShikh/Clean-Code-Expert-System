import math


class CleanCodeScorer:

    RULE_WEIGHTS = {
        "Multiple Responsibilities": 10,
        "High Cyclomatic Complexity": 8,
        "Long Method": 7,
        "Deep Nesting (Arrow Anti-Pattern)": 6,
        "Too Many Parameters": 5,
        "Data Clumps": 5,
        "Dead Code (Project-Wide)": 4,
        "Magic Number": 1,
        "Short Variable Name": 1,
    }

    MINOR_REPETITIVE_RULES = {"Magic Number", "Short Variable Name"}

    @staticmethod
    def calculate_score(recommendations, total_lines=1):
        rule_counts = {}
        for rec in recommendations:
            rule_name = rec.rule_name
            rule_counts[rule_name] = rule_counts.get(rule_name, 0) + 1

        total_penalty = 0
        for rule_name, count in rule_counts.items():
            weight = CleanCodeScorer.RULE_WEIGHTS.get(rule_name, 5)
            if rule_name in CleanCodeScorer.MINOR_REPETITIVE_RULES:
                effective_penalty = weight * math.sqrt(count)
            else:
                effective_penalty = weight * count
            total_penalty += effective_penalty

        normalized_penalty = (total_penalty * 100) / max(total_lines, 1)
        score = 100 * (0.99 ** normalized_penalty)
        return max(0, min(100, round(score)))
