import subprocess
import json
import os

# Path to the acorn-based Node.js parser script
_PARSER_SCRIPT = os.path.join(os.path.dirname(__file__), 'parse_js.js')
# Path to node_modules (installed at project root)
_NODE_MODULES = os.path.join(os.path.dirname(__file__), '..', 'node_modules')


class JavaScriptParser:

    @staticmethod
    def parse(source_code: str) -> dict:
        """
        Parse JavaScript source code into an AST dict.

        Uses acorn (via Node.js) which supports ES2025 syntax including:
        - Class static fields (static x = 1)
        - Optional chaining (a?.b)
        - Nullish coalescing (a ?? b)
        - Private class fields (#field)
        - Logical assignment operators (&&=, ||=, ??=)
        - Top-level await
        - Import/export statements
        Falls back to esprima for environments without Node.js.
        """
        # Try acorn via Node.js first (full modern JS support)
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
            # Node.js not available — fall back to esprima
            pass
        except subprocess.TimeoutExpired:
            raise ValueError("JavaScript parsing timed out (file may be too large).")

        # Fallback: esprima (supports up to ES2018)
        try:
            import esprima
            ast = esprima.parseModule(source_code, {"loc": True})
            return ast.toDict()
        except Exception as e:
            raise ValueError(f"Failed to parse JavaScript code. Error: {e}")
