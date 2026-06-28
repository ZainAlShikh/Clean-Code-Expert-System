class CleanCodeScorer:
    """
    Calculates a Clean Code Score from 0 to 100 based on detected issues.
    Starts at 100 and deducts points based on the severity of each recommendation.
    """

    SEVERITY_WEIGHTS = {
        "CRITICAL": 25,
        "HIGH": 15,
        "MEDIUM": 8,
        "LOW": 3,
    }

    @staticmethod
    def calculate_score(recommendations):
        """
        Calculates the Clean Code Score using an Exponential Decay algorithm.
        This prevents the score from hitting 0 instantly and is fairer for larger files.
        
        :param recommendations: List of RefactoringRecommendation objects.
        :return: An integer score between 0 and 100.
        """
        total_penalty = 0
        for rec in recommendations:
            severity_value = rec.severity.value if hasattr(rec.severity, 'value') else str(rec.severity)
            deduction = CleanCodeScorer.SEVERITY_WEIGHTS.get(severity_value, 5)
            total_penalty += deduction
            
        # Exponential Decay: 100 * (0.95 ^ total_penalty)
        # Every penalty point reduces the CURRENT score by 5%.
        score = 100 * (0.95 ** total_penalty)
        
        return max(0, min(100, int(score)))
