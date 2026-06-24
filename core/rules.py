from experta import Rule, MATCH, TEST, NOT
from core.facts import JSFunctionFact, JSVariableFact, JSIfStatementFact, JSFunctionCallFact, JSMagicNumberFact
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
            description=f"Function '{name}' is too long ({line_count} lines). Clean Code recommends functions to be small (ideally under 20 lines).",
            target_name=name,
            file_path=file_path,
            line_number=start_line,
            severity=Severity.HIGH,
            suggestion="Extract Method: Identify smaller logical blocks within the function and extract them into separate helper functions.",
            rule_id="R1",
            condition="IF LineCount > 20",
            violation_type="Long Method",
            strategy="Extract Method",
            status="FIRED"
        ))

    @Rule(JSFunctionFact(param_count=MATCH.param_count, name=MATCH.name, start_line=MATCH.start_line, file_path=MATCH.file_path),
          TEST(lambda param_count: param_count > 3))
    def too_many_parameters_rule(self, name, start_line, param_count, file_path):
        self.recommendations.append(RefactoringRecommendation(
            rule_name="Too Many Parameters",
            description=f"Function '{name}' takes {param_count} parameters. Clean Code states that a function should have 0-2 parameters, and >3 requires strong justification.",
            target_name=name,
            file_path=file_path,
            line_number=start_line,
            severity=Severity.HIGH, # Changed to HIGH to match image
            suggestion="Introduce Parameter Object: Group related parameters into a single object or class.",
            rule_id="R2",
            condition="IF ParameterCount > 3",
            violation_type="Too Many Parameters",
            strategy="Introduce Parameter Object",
            status="FIRED"
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
            suggestion="Rename Variable: Give the variable a meaningful and descriptive name that explains its intent.",
            rule_id="R3",
            condition="IF VariableNameLength < 3",
            violation_type="Short Variable Name",
            strategy="Rename Variable",
            status="FIRED"
        ))

    @Rule(JSFunctionFact(name=MATCH.func_name, file_path=MATCH.file_path, start_line=MATCH.start_line),
          TEST(lambda func_name: func_name != "anonymous"),
          NOT(JSFunctionCallFact(target_name=MATCH.func_name)))
    def dead_code_project_wide_rule(self, func_name, file_path, start_line):
        self.recommendations.append(RefactoringRecommendation(
            rule_name="Dead Code (Project-Wide)",
            description=f"Function '{func_name}' is declared but never called anywhere in the analyzed project files.",
            target_name=func_name,
            file_path=file_path,
            line_number=start_line,
            severity=Severity.MEDIUM,
            suggestion="Remove Dead Code: If the function is not part of a public API, it should be removed to keep the codebase clean.",
            rule_id="R4",
            condition="IF FunctionDeclared AND NOT FunctionCalled",
            violation_type="Dead Code",
            strategy="Remove Dead Code",
            status="FIRED"
        ))

    @Rule(
        JSFunctionFact(name=MATCH.f1, params_list=MATCH.p, file_path=MATCH.file_path1, start_line=MATCH.start_line1),
        JSFunctionFact(name=MATCH.f2, params_list=MATCH.p, file_path=MATCH.file_path2),
        TEST(lambda f1, f2, p: f1 < f2 and len(p) >= 3 and f1 != "anonymous" and f2 != "anonymous")
    )
    def data_clumps_rule(self, f1, f2, p, file_path1, start_line1, file_path2):
        param_str = ", ".join(p)
        self.recommendations.append(RefactoringRecommendation(
            rule_name="Data Clumps",
            description=f"Functions '{f1}' and '{f2}' (in {file_path2}) share the exact same long list of parameters ({param_str}).",
            target_name=f1,
            file_path=file_path1,
            line_number=start_line1,
            severity=Severity.MEDIUM,
            suggestion="Extract Class / Introduce Parameter Object: Turn these parameters into an object.",
            rule_id="R5",
            condition="IF SameParameters >= 3 in Multiple Functions",
            violation_type="Data Clumps",
            strategy="Extract Class / Introduce Parameter Object",
            status="FIRED"
        ))

    @Rule(JSFunctionFact(complexity=MATCH.complexity, name=MATCH.name, start_line=MATCH.start_line, file_path=MATCH.file_path),
          TEST(lambda complexity: complexity > 10))
    def high_cyclomatic_complexity_rule(self, name, start_line, complexity, file_path):
        self.recommendations.append(RefactoringRecommendation(
            rule_name="High Cyclomatic Complexity",
            description=f"Function '{name}' has a cyclomatic complexity of {complexity}. Clean Code suggests functions should do one thing and have low complexity (<= 10).",
            target_name=name,
            file_path=file_path,
            line_number=start_line,
            severity=Severity.HIGH,
            suggestion="Extract Method: Break down the complex logic into smaller, single-purpose functions.",
            rule_id="R6",
            condition="IF CyclomaticComplexity > 10",
            violation_type="High Cyclomatic Complexity",
            strategy="Extract Method",
            status="FIRED"
        ))

    @Rule(JSFunctionFact(nesting_depth=MATCH.nesting_depth, name=MATCH.name, start_line=MATCH.start_line, file_path=MATCH.file_path),
          TEST(lambda nesting_depth: nesting_depth > 3))
    def deep_nesting_rule(self, name, start_line, nesting_depth, file_path):
        self.recommendations.append(RefactoringRecommendation(
            rule_name="Deep Nesting (Arrow Anti-Pattern)",
            description=f"Function '{name}' has a control flow nesting depth of {nesting_depth}. Blocks within if/for/while should ideally be one line long (calling another function).",
            target_name=name,
            file_path=file_path,
            line_number=start_line,
            severity=Severity.HIGH, # Changed to HIGH to match image
            suggestion="Extract Method / Guard Clauses: Return early to avoid deep nesting, or extract the nested logic into a separate function.",
            rule_id="R7",
            condition="IF NestingDepth > 3",
            violation_type="Deep Nesting",
            strategy="Guard Clauses",
            status="FIRED"
        ))

    @Rule(JSMagicNumberFact(value=MATCH.value, file_path=MATCH.file_path, start_line=MATCH.start_line))
    def magic_number_rule(self, value, file_path, start_line):
        self.recommendations.append(RefactoringRecommendation(
            rule_name="Magic Number",
            description=f"Found unexplained numeric literal '{value}'.",
            target_name=str(value),
            file_path=file_path,
            line_number=start_line,
            severity=Severity.LOW,
            suggestion="Replace Magic Number with Symbolic Constant: Assign the number to a well-named constant variable.",
            rule_id="R8",
            condition="IF UnexplainedNumericLiteral Found",
            violation_type="Magic Number",
            strategy="Replace Magic Number with Constant",
            status="FIRED"
        ))

    @Rule(JSFunctionFact(name=MATCH.name, concern_count=MATCH.cc, file_path=MATCH.file_path, start_line=MATCH.start_line, concerns_list=MATCH.cl),
          TEST(lambda cc: cc > 2))
    def multiple_responsibilities_rule(self, name, cc, file_path, start_line, cl):
        concerns_str = ", ".join(cl)
        self.recommendations.append(RefactoringRecommendation(
            rule_name="Multiple Responsibilities",
            description=f"Function '{name}' handles {cc} different concerns ({concerns_str}).",
            target_name=name,
            file_path=file_path,
            line_number=start_line,
            severity=Severity.MEDIUM,
            suggestion="Extract Method & Apply Single Responsibility Principle",
            rule_id="R9",
            condition="IF Multiple Concerns (>2 types)",
            violation_type="Multiple Responsibilities",
            strategy="Extract Method",
            status="FIRED"
        ))
