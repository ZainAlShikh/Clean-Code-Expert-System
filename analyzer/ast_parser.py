import esprima


class JavaScriptParser:

    @staticmethod
    def parse(source_code: str):
        try:
            ast = esprima.parseModule(source_code, {"loc": True})
            return ast.toDict()
        except Exception as e:
            raise ValueError(f"Failed to parse JavaScript code. Error: {e}")
