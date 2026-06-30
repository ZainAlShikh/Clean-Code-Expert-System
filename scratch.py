import urllib.request
import json
import urllib.error

GEMINI_API_KEY = "AIzaSyDB9OYS45Cd4Vs_WXrB6k_kqihAKg-qiCw"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-robotics-er-1.6-preview:generateContent?key={GEMINI_API_KEY}"

try:
    prompt = "Hello"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    })

    req = urllib.request.Request(
        GEMINI_API_URL,
        data=payload.encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=15) as response:
        print("Success!")
        print(response.read().decode("utf-8"))

except Exception as e:
    print(f"API call failed: {e}")
    if hasattr(e, 'read'):
        print(f"Error details: {e.read().decode()}")
