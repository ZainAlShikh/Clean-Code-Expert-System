from core.facts import JSFunctionFact, JSVariableFact, JSIfStatementFact, JSFunctionCallFact, JSMagicNumberFact, JSConcernFact


class FactExtractor:

    def __init__(self):
        self.facts = []
        self.current_file_path = ""
        self.function_stack = []

    def extract(self, ast, file_path: str) -> list:
        self.current_file_path = file_path
        self._traverse(ast, current_depth=0)
        return self.facts

    def _traverse(self, node, current_depth=0):
        if not node or not isinstance(node, dict):
            return

        node_type = node.get("type")
        if not node_type:
            return

        child_depth = current_depth
        if node_type in ("BlockStatement", "IfStatement", "ForStatement", "WhileStatement", "DoWhileStatement", "SwitchStatement"):
            child_depth += 1

        is_func = node_type in ("FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression")
        if is_func:
            name = "anonymous"
            if node.get("id"):
                name = node["id"].get("name", "anonymous")
            self.function_stack.append(name)
            self._handle_function(node, name)
            child_depth = 0

        elif node_type == "VariableDeclaration":
            self._handle_variable(node)

        elif node_type == "IfStatement":
            self._handle_if_statement(node)

        elif node_type == "CallExpression":
            self._handle_call_expression(node)

        elif node_type == "Literal":
            self._handle_literal(node)

        for key, value in node.items():
            if key in ("loc", "type", "range"):
                continue
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._traverse(item, current_depth=child_depth)
            elif isinstance(value, dict):
                self._traverse(value, current_depth=child_depth)

        if is_func:
            self.function_stack.pop()

    def _handle_function(self, node, name):
        start_line = 0
        line_count = 0
        if "loc" in node:
            start_line = node["loc"]["start"]["line"]
            end_line = node["loc"]["end"]["line"]
            line_count = end_line - start_line + 1

        params = node.get("params", [])
        param_count = len(params)
        params_list = []
        for p in params:
            if p.get("type") == "Identifier":
                params_list.append(p.get("name", ""))

        complexity, max_nesting = self._calculate_complexity_and_nesting(node.get("body", {}))

        self.facts.append(JSFunctionFact(
            name=name,
            file_path=self.current_file_path,
            line_count=line_count,
            param_count=param_count,
            params_list=tuple(params_list),
            start_line=start_line,
            complexity=complexity,
            nesting_depth=max_nesting
        ))

    def _handle_variable(self, node):
        kind = node.get("kind", "var")
        scope = "block" if kind in ("let", "const") else "function/global"
        is_constant = (kind == "const")

        declarations = node.get("declarations", [])
        for decl in declarations:
            decl_id = decl.get("id")
            if decl_id and "name" in decl_id:
                name = decl_id["name"]
                start_line = decl.get("loc", {}).get("start", {}).get("line", 0)
                self.facts.append(JSVariableFact(
                    name=name,
                    file_path=self.current_file_path,
                    scope=scope,
                    is_constant=is_constant,
                    start_line=start_line
                ))

    def _handle_if_statement(self, node):
        start_line = node.get("loc", {}).get("start", {}).get("line", 0)
        test_node = node.get("test")
        logical_ops_count = self._count_logical_operators(test_node)
        self.facts.append(JSIfStatementFact(
            logical_operators_count=logical_ops_count,
            file_path=self.current_file_path,
            start_line=start_line
        ))

    def _handle_call_expression(self, node):
        callee = node.get("callee", {})
        target_name = "unknown"

        if callee.get("type") == "Identifier":
            target_name = callee.get("name", "unknown")
        elif callee.get("type") == "MemberExpression":
            prop = callee.get("property", {})
            if prop.get("type") == "Identifier":
                target_name = prop.get("name", "unknown")

        start_line = node.get("loc", {}).get("start", {}).get("line", 0)

        if target_name != "unknown":
            self.facts.append(JSFunctionCallFact(
                target_name=target_name,
                file_path=self.current_file_path,
                start_line=start_line
            ))

            if self.function_stack:
                current_func = self.function_stack[-1]
                concern = None
                tn_lower = target_name.lower()

                if "validat" in tn_lower:
                    concern = "Validation"
                elif "save" in tn_lower or "db" in tn_lower or "query" in tn_lower or "persist" in tn_lower:
                    concern = "Database"
                elif "email" in tn_lower or "send" in tn_lower or "notify" in tn_lower:
                    concern = "Email"
                elif "report" in tn_lower or "export" in tn_lower:
                    concern = "Reporting"
                elif "dash" in tn_lower or "update_dash" in tn_lower:
                    concern = "Dashboard"
                elif "archiv" in tn_lower:
                    concern = "Archiving"
                elif "audit" in tn_lower or "log" in tn_lower:
                    concern = "Audit"

                if concern:
                    self.facts.append(JSConcernFact(
                        func_name=current_func,
                        file_path=self.current_file_path,
                        concern=concern
                    ))

    def _handle_literal(self, node):
        val = node.get("value")
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            if val not in (0, 1, -1):
                start_line = node.get("loc", {}).get("start", {}).get("line", 0)
                self.facts.append(JSMagicNumberFact(
                    value=float(val),
                    file_path=self.current_file_path,
                    start_line=start_line
                ))

    def _calculate_complexity_and_nesting(self, body_node):
        complexity = 1
        max_nesting = 0

        def _walk(n, current_depth):
            nonlocal complexity, max_nesting
            if not n or not isinstance(n, dict):
                return

            ntype = n.get("type")
            child_depth = current_depth

            if ntype in ("BlockStatement", "IfStatement", "ForStatement", "WhileStatement", "DoWhileStatement", "SwitchStatement"):
                child_depth += 1
                max_nesting = max(max_nesting, child_depth)

            if ntype in ("IfStatement", "ForStatement", "WhileStatement", "DoWhileStatement", "SwitchCase"):
                complexity += 1
            elif ntype == "LogicalExpression" and n.get("operator") in ("&&", "||"):
                complexity += 1

            for k, v in n.items():
                if k in ("loc", "type", "range"):
                    continue
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict):
                            _walk(item, child_depth)
                elif isinstance(v, dict):
                    _walk(v, child_depth)

        _walk(body_node, 0)
        return complexity, max_nesting

    def _count_logical_operators(self, test_node):
        count = 0

        def _count(n):
            nonlocal count
            if not n or not isinstance(n, dict):
                return
            if n.get("type") == "LogicalExpression":
                count += 1
            for k, v in n.items():
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict):
                            _count(item)
                elif isinstance(v, dict):
                    _count(v)

        _count(test_node)
        return count

    def get_extracted_facts_summary(self):
        summary = {
            "functions": [],
            "variables": [],
            "magic_numbers": [],
            "concerns": []
        }
        for f in self.facts:
            if "complexity" in f:
                summary["functions"].append({"name": f["name"], "complexity": f["complexity"], "param_count": f["param_count"], "line_count": f["line_count"], "nesting_depth": f["nesting_depth"]})
            elif "is_constant" in f:
                summary["variables"].append({"name": f["name"], "scope": f["scope"]})
            elif "value" in f:
                summary["magic_numbers"].append({"value": f["value"]})
            elif "concern" in f:
                summary["concerns"].append({"func_name": f["func_name"], "concern": f["concern"]})
        return summary
