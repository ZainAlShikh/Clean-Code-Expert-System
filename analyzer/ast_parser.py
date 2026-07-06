import subprocess
import json
import os

_PARSER_SCRIPT = os.path.join(os.path.dirname(__file__), 'parse_js.js')
_NODE_MODULES = os.path.join(os.path.dirname(__file__), '..', 'node_modules')

class JavaScriptParser:

    @staticmethod
    def parse(source_code: str) -> dict:
        try:
            result = subprocess.run(
                ['node', _PARSER_SCRIPT],
                input=source_code,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=15
            )
            if result.returncode == 0 and result.stdout:
                ast = json.loads(result.stdout)
                if '__parse_error__' in ast:
                    raise ValueError(f"Failed to parse JavaScript: {ast['__parse_error__']}")
                return ast
        except FileNotFoundError:
            pass
        except subprocess.TimeoutExpired:
            raise ValueError("JavaScript parsing timed out (file may be too large).")

        try:
            import esprima
            ast = esprima.parseModule(source_code, {"loc": True})
            return ast.toDict()
        except Exception as e:
            raise ValueError(f"Failed to parse JavaScript code. Error: {e}")
