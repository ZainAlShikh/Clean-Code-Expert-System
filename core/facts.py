import collections
import collections.abc
collections.Mapping = collections.abc.Mapping
collections.Sequence = collections.abc.Sequence

from experta import Fact, Field

class JSFunctionFact(Fact):
    """
    Fact representing a JavaScript function or method.
    """
    name = Field(str, mandatory=True)
    file_path = Field(str, mandatory=True)
    line_count = Field(int, mandatory=True)
    param_count = Field(int, mandatory=True)
    start_line = Field(int, mandatory=True)
    complexity = Field(int, default=1)  # Optional metric for Cyclomatic Complexity


class JSVariableFact(Fact):
    """
    Fact representing a JavaScript variable declaration.
    """
    name = Field(str, mandatory=True)
    file_path = Field(str, mandatory=True)
    scope = Field(str, default="local") # e.g., "global", "local", "block"
    is_constant = Field(bool, default=False)
    start_line = Field(int, mandatory=True)


class JSIfStatementFact(Fact):
    """
    Fact representing an If statement condition.
    Useful for detecting overly complex conditionals.
    """
    logical_operators_count = Field(int, mandatory=True)
    file_path = Field(str, mandatory=True)
    start_line = Field(int, mandatory=True)
