import esprima

class JavaScriptParser:
    """
    Parser wrapper for JavaScript code using esprima.
    Converts raw JavaScript source code into an Abstract Syntax Tree (AST).
    Supports modern JavaScript including ES6 (imports, arrow functions, etc).
    """

    @staticmethod
    def parse(source_code: str):
        """
        Parses the JavaScript source code into an AST.
        
        :param source_code: Raw JavaScript string.
        :return: AST dictionary.
        """
        try:
            ast = esprima.parseModule(source_code, {"loc": True})
            return ast.toDict()
        except Exception as e:
            raise ValueError(f"Failed to parse JavaScript code. Error: {e}")
