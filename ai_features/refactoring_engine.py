import json
import urllib.request
import urllib.error


class RefactoringEngine:

    GEMINI_API_KEY = "AIzaSyDB9OYS45Cd4Vs_WXrB6k_kqihAKg-qiCw"
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-robotics-er-1.6-preview:generateContent?key={GEMINI_API_KEY}"

    @staticmethod
    def generate_refactored_preview(source_code, recommendations):
        if not recommendations:
            return {
                "refactored_code": source_code,
                "applied_strategies": [],
                "structure_preview": None
            }

        applied_strategies = list(set([rec.strategy for rec in recommendations]))

        primary_func = "main_process"
        for rec in recommendations:
            if rec.rule_name in ["Long Method", "Too Many Parameters", "Dead Code (Project-Wide)",
                                 "High Cyclomatic Complexity", "Deep Nesting (Arrow Anti-Pattern)",
                                 "Multiple Responsibilities", "Data Clumps"]:
                if rec.target_name and rec.target_name != "unknown":
                    primary_func = rec.target_name
                    break

        refactored_code = RefactoringEngine._call_gemini_api(source_code, recommendations)

        if not refactored_code:
            refactored_code = RefactoringEngine._generate_template(primary_func)

        structure_preview = {
            "root": f"{primary_func}()",
            "extracted": []
        }

        try:
            import re
            functions = []
            func_matches = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', refactored_code)
            functions.extend(func_matches)
            arrow_matches = re.findall(r'(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s+)?\(.*?\)\s*=>', refactored_code)
            functions.extend(arrow_matches)

            seen = set()
            functions = [x for x in functions if not (x in seen or seen.add(x))]

            if functions:
                structure_preview["root"] = f"{functions[0]}()"
                structure_preview["extracted"] = [f"{f}()" for f in functions[1:4]]
        except Exception as e:
            print(f"[RefactoringEngine] Could not parse AI code for structure: {e}")
            structure_preview = {
                "root": f"{primary_func}()",
                "extracted": [
                    f"validate_{primary_func}()",
                    f"execute_{primary_func}()",
                    f"finalize_{primary_func}()"
                ]
            }

        return {
            "refactored_code": refactored_code,
            "applied_strategies": applied_strategies,
            "structure_preview": structure_preview
        }

    @staticmethod
    def _call_gemini_api(source_code, recommendations):
        try:
            violations = []
            for rec in recommendations:
                violations.append(f"- {rec.rule_name}: {rec.description} (Strategy: {rec.strategy})")
            violations_text = "\n".join(violations)

            prompt = f"""You are a Clean Code refactoring expert. Analyze the following JavaScript code and rewrite it applying Clean Code principles.

The following violations were detected by our expert system:
{violations_text}

Original Code:
```javascript
{source_code}
```

Instructions:
1. Apply Guard Clauses to reduce nesting
2. Extract methods to follow Single Responsibility Principle
3. Use Parameter Objects if there are too many parameters
4. Replace magic numbers with named constants
5. Use meaningful variable names

CRITICAL: Return ONLY the refactored JavaScript code, no explanations.
CRITICAL: DO NOT TRUNCATE the output. Ensure all functions are fully implemented and ALL brackets are properly closed. Output the full file!
CRITICAL: Generate STRICTLY ECMA 5.1 compliant JavaScript. DO NOT use object destructuring, DO NOT use arrow functions, DO NOT use let/const (use var), and DO NOT use template literals. This is required for our legacy AST parser to work."""

            payload = json.dumps({
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 8192
                }
            })

            req = urllib.request.Request(
                RefactoringEngine.GEMINI_API_URL,
                data=payload.encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                content = result["candidates"][0]["content"]["parts"][0]["text"]

                content = content.strip()
                if content.startswith("```javascript"):
                    content = content[len("```javascript"):].strip()
                if content.startswith("```js"):
                    content = content[len("```js"):].strip()
                if content.startswith("```"):
                    content = content[3:].strip()
                if content.endswith("```"):
                    content = content[:-3].strip()
                return content

        except Exception as e:
            print(f"[RefactoringEngine] Gemini API call failed: {e}")
            if hasattr(e, 'read'):
                print(f"[RefactoringEngine] Error details: {e.read().decode()}")
            return None

    @staticmethod
    def _generate_template(primary_func):
        return f"""function {primary_func}(requestObj) {{
    if (!requestObj || !requestObj.isValid) return;

    validate_{primary_func}(requestObj);
    execute_{primary_func}(requestObj);
    finalize_{primary_func}(requestObj);
}}

function validate_{primary_func}(data) {{
}}

function execute_{primary_func}(data) {{
}}

function finalize_{primary_func}(data) {{
}}"""
