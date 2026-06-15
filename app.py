import os
from flask import Flask, render_template, request, jsonify

# Import the core engine and parsers
from analyzer.ast_parser import JavaScriptParser
from analyzer.fact_extractor import FactExtractor
from core.engine import CleanCodeExpertSystem
from main import find_js_files

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    target_path = data.get('path', '').strip()

    if not target_path or not os.path.exists(target_path):
        return jsonify({"error": "Invalid or missing path."}), 400

    js_files = find_js_files(target_path)
    if not js_files:
        return jsonify({"error": "No JavaScript files found in the specified path."}), 404

    extractor = FactExtractor()
    all_facts = []

    for file_path in js_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
            ast = JavaScriptParser.parse(source_code)
            facts = extractor.extract(ast, file_path)
            all_facts.extend(facts)
        except Exception as e:
            # We can log this internally
            pass

    engine = CleanCodeExpertSystem()
    recommendations = engine.analyze(all_facts)

    return jsonify({
        "files_scanned": len(js_files),
        "recommendations": [rec.to_dict() for rec in recommendations]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
