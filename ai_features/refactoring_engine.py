import json
import urllib.request
import urllib.error


class RefactoringEngine:

    GEMINI_API_KEY = "AQ.Ab8RN6JtP3255V4p6-vDX5XcnudG3B4gUsO_qC8qDp4G8qbl1g"
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

        refactored_code = RefactoringEngine._call_gemini_api(source_code, recommendations)

        if not refactored_code:
            return None

        structure_preview = {
            "root": f"{primary_func}()",
            "extracted": []
            }

        return {
            "refactored_code": refactored_code,
            "applied_strategies": applied_strategies,
            "structure_preview": structure_preview
        }

    @staticmethod
    def _call_gemini_api(source_code, recommendations):
        try:
            severity_weight = {"High": 3, "Medium": 2, "Low": 1}
            sorted_recs = sorted(recommendations, key=lambda r: severity_weight.get(r.severity.value, 0), reverse=True)
            violations = []
            for rec in sorted_recs[:30]:  
                violations.append(f"- [{rec.severity.value}] {rec.rule_name}: {rec.description}")
            violations_text = "\n".join(violations)
            if len(recommendations) > 30:
                violations_text += f"\n... and {len(recommendations) - 30} more issues."

            MAX_SOURCE_LINES = 1000
            source_lines = source_code.splitlines()
            if len(source_lines) > MAX_SOURCE_LINES:
                trimmed_source = "\n".join(source_lines[:MAX_SOURCE_LINES])
                source_note = f"\n[NOTE: File has {len(source_lines)} lines. Showing first {MAX_SOURCE_LINES} lines for refactoring. Apply the same principles to the rest of the file.]"
            else:
                trimmed_source = source_code
                source_note = ""

            prompt = f

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
