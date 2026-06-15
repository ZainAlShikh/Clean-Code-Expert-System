from experta import KnowledgeEngine
from core.rules import CleanCodeRules

class CleanCodeExpertSystem(KnowledgeEngine, CleanCodeRules):
    """
    The Expert System Engine.
    Inherits from KnowledgeEngine (Experta) and CleanCodeRules.
    """

    def __init__(self):
        super().__init__()
        self.recommendations = []

    def reset_engine(self):
        """
        Resets the engine state and clears old recommendations.
        """
        self.reset()
        self.recommendations = []

    def analyze(self, facts: list) -> list:
        """
        Loads facts into the engine, runs it, and returns recommendations.
        """
        self.reset_engine()

        # Declare facts to the engine
        for fact in facts:
            self.declare(fact)

        # Run the inference engine
        self.run()

        return self.recommendations
