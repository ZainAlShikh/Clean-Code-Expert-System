from core.facts import JSFunctionFact, JSVariableFact, JSIfStatementFact

class FactExtractor:
    """
    Traverses the pyjsparser AST and extracts facts for the Expert System.
    """

    def __init__(self):
        self.facts = []
        self.current_file_path = ""

    def extract(self, ast, file_path: str) -> list:
        """
        Extracts facts from the AST for a specific file.
        """
        self.current_file_path = file_path
        self._traverse(ast)
        return self.facts

    def _traverse(self, node):
        if not node or not isinstance(node, dict):
            return

        node_type = node.get("type")
        if not node_type:
            return

        if node_type in ("FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"):
            self._handle_function(node)

        elif node_type == "VariableDeclaration":
            self._handle_variable(node)

        elif node_type == "IfStatement":
            self._handle_if_statement(node)

        # Traverse children recursively
        for key, value in node.items():
            if key in ("loc", "type", "range"):
                continue
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._traverse(item)
            elif isinstance(value, dict):
                self._traverse(value)

    def _handle_function(self, node):
        name = "anonymous"
        if node.get("id"):
            name = node["id"].get("name", "anonymous")
            
        start_line = 0
        line_count = 0
        if "loc" in node:
            start_line = node["loc"]["start"]["line"]
            end_line = node["loc"]["end"]["line"]
            line_count = end_line - start_line + 1

        params = node.get("params", [])
        param_count = len(params)

        self.facts.append(JSFunctionFact(
            name=name,
            file_path=self.current_file_path,
            line_count=line_count,
            param_count=param_count,
            start_line=start_line
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
            logical_ops_count=logical_ops_count,
            logical_operators_count=logical_ops_count,
            file_path=self.current_file_path,
            start_line=start_line
        ))

    def _count_logical_operators(self, test_node):
        count = 0
        def _count(n):
            nonlocal count
            if not n or not isinstance(n, dict): return
            if n.get("type") == "LogicalExpression":
                count += 1
                
            for k, v in n.items():
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict): _count(item)
                elif isinstance(v, dict):
                    _count(v)
        _count(test_node)
        return count
