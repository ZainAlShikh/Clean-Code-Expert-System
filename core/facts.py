import collections
import collections.abc
collections.Mapping = collections.abc.Mapping
collections.Sequence = collections.abc.Sequence

from experta import Fact, Field


class JSFunctionFact(Fact):
    name = Field(str, mandatory=True)
    file_path = Field(str, mandatory=True)
    line_count = Field(int, mandatory=True)
    param_count = Field(int, mandatory=True)
    params_list = Field(tuple, default=tuple())
    start_line = Field(int, mandatory=True)
    complexity = Field(int, default=1)
    nesting_depth = Field(int, default=0)


class JSConcernFact(Fact):
    func_name = Field(str, mandatory=True)
    file_path = Field(str, mandatory=True)
    concern = Field(str, mandatory=True)


class JSFunctionCallFact(Fact):
    target_name = Field(str, mandatory=True)
    file_path = Field(str, mandatory=True)
    start_line = Field(int, mandatory=True)


class JSVariableFact(Fact):
    name = Field(str, mandatory=True)
    file_path = Field(str, mandatory=True)
    scope = Field(str, default="local")
    is_constant = Field(bool, default=False)
    start_line = Field(int, mandatory=True)


class JSMagicNumberFact(Fact):
    value = Field(float, mandatory=True)
    file_path = Field(str, mandatory=True)
    start_line = Field(int, mandatory=True)


class JSIfStatementFact(Fact):
    logical_operators_count = Field(int, mandatory=True)
    file_path = Field(str, mandatory=True)
    start_line = Field(int, mandatory=True)
