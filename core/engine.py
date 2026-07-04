from experta import KnowledgeEngine
from core.rules import CleanCodeRules


class CleanCodeExpertSystem(KnowledgeEngine, CleanCodeRules):

    def __init__(self):
        super().__init__()
        self.recommendations = []

    def reset_engine(self):
        self.reset()
        self.recommendations = []

    def analyze(self, facts: list) -> list:
        self.reset_engine()
        for fact in facts:
            self.declare(fact)
        self.run()
        return self.recommendations
