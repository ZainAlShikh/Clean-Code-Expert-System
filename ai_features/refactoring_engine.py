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
            for rec in recommendations[:30]:  # Cap at 30 most important violations
                violations.append(f"- [{rec.severity.value}] {rec.rule_name}: {rec.description}")
            violations_text = "\n".join(violations)
            if len(recommendations) > 30:
                violations_text += f"\n... and {len(recommendations) - 30} more issues."

            # For large files, send only the first 300 lines to avoid truncation
            MAX_SOURCE_LINES = 300
            source_lines = source_code.splitlines()
            if len(source_lines) > MAX_SOURCE_LINES:
                trimmed_source = "\n".join(source_lines[:MAX_SOURCE_LINES])
                source_note = f"\n[NOTE: File has {len(source_lines)} lines. Showing first {MAX_SOURCE_LINES} lines for refactoring. Apply the same principles to the rest of the file.]"
            else:
                trimmed_source = source_code
                source_note = ""

            prompt = f"""You are a Clean Code refactoring expert. Rewrite the following JavaScript code applying Clean Code principles.

Detected violations:
{violations_text}

Original Code:{source_note}
```javascript
{trimmed_source}
```

Instructions:
1. Apply Guard Clauses to reduce deep nesting
2. Extract long methods into smaller focused helper functions
3. Replace ALL magic numbers with named constants at the top of the file
4. Use meaningful variable names (no single-letter names like x, y, z)
5. Remove duplicate code

CRITICAL: Return ONLY the refactored JavaScript code with no explanations or markdown.
CRITICAL: DO NOT truncate. Every function must be fully implemented with properly closed brackets."""

            payload = json.dumps({
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 65536
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
