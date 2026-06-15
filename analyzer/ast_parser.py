import pyjsparser

class JavaScriptParser:
    """
    Parser wrapper for JavaScript code using pyjsparser (pure python).
    Converts raw JavaScript source code into an Abstract Syntax Tree (AST).
    """

    @staticmethod
    def parse(source_code: str):
        """
        Parses the JavaScript source code into an AST.
        
        :param source_code: Raw JavaScript string.
        :return: AST dictionary.
        """
        try:
            parser = pyjsparser.PyJsParser()
            ast = parser.parse(source_code)
            return ast
        except Exception as e:
            raise ValueError(f"Failed to parse JavaScript code. Error: {e}")
