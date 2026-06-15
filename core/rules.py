from experta import Rule, MATCH, TEST
from core.facts import JSFunctionFact, JSVariableFact, JSIfStatementFact
from models.recommendation import RefactoringRecommendation, Severity

class CleanCodeRules:
    """
    Mixin class containing all the Experta rules for Clean Code.
    Must be mixed into a KnowledgeEngine subclass.
    """

    @Rule(JSFunctionFact(line_count=MATCH.line_count, name=MATCH.name, start_line=MATCH.start_line, file_path=MATCH.file_path),
          TEST(lambda line_count: line_count > 20))
    def long_method_rule(self, name, start_line, line_count, file_path):
        self.recommendations.append(RefactoringRecommendation(
            rule_name="Long Method",
            description=f"Function '{name}' is too long ({line_count} lines). It should ideally be under 20 lines.",
            target_name=name,
            file_path=file_path,
            line_number=start_line,
            severity=Severity.HIGH,
            suggestion="Extract Method: Identify smaller logical blocks within the function and extract them into separate helper functions."
        ))

    @Rule(JSFunctionFact(param_count=MATCH.param_count, name=MATCH.name, start_line=MATCH.start_line, file_path=MATCH.file_path),
          TEST(lambda param_count: param_count > 3))
    def too_many_parameters_rule(self, name, start_line, param_count, file_path):
        self.recommendations.append(RefactoringRecommendation(
            rule_name="Too Many Parameters",
            description=f"Function '{name}' takes {param_count} parameters. More than 3 parameters make the function hard to understand and test.",
            target_name=name,
            file_path=file_path,
            line_number=start_line,
            severity=Severity.MEDIUM,
            suggestion="Introduce Parameter Object: Group related parameters into a single object or class."
        ))

    @Rule(JSVariableFact(name=MATCH.name, start_line=MATCH.start_line, file_path=MATCH.file_path),
          TEST(lambda name: len(name) < 3 and name not in ['i', 'j', 'k', 'e', '_']))
    def short_variable_name_rule(self, name, start_line, file_path):
        self.recommendations.append(RefactoringRecommendation(
            rule_name="Short Variable Name",
            description=f"Variable '{name}' has a poorly descriptive, short name.",
            target_name=name,
            file_path=file_path,
            line_number=start_line,
            severity=Severity.LOW,
            suggestion="Rename Variable: Give the variable a meaningful and descriptive name that explains its intent."
        ))

    @Rule(JSIfStatementFact(logical_operators_count=MATCH.logical_operators_count, start_line=MATCH.start_line, file_path=MATCH.file_path),
          TEST(lambda logical_operators_count: logical_operators_count >= 3))
    def complex_condition_rule(self, start_line, logical_operators_count, file_path):
        self.recommendations.append(RefactoringRecommendation(
            rule_name="Complex Condition",
            description=f"If statement contains {logical_operators_count} logical operators, making it hard to read.",
            target_name="If Statement",
            file_path=file_path,
            line_number=start_line,
            severity=Severity.MEDIUM,
            suggestion="Extract Variable / Extract Method: Break down the condition into well-named boolean variables or a separate method."
        ))
