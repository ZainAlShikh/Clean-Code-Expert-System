import os
from flask import Flask, render_template, request, jsonify

from analyzer.ast_parser import JavaScriptParser
from analyzer.fact_extractor import FactExtractor
from core.engine import CleanCodeExpertSystem
from ai_features.scoring import CleanCodeScorer
from ai_features.refactoring_engine import RefactoringEngine
from ai_features.ast_visualizer import ASTVisualizer
from main import find_js_files

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ai-dashboard')
def ai_dashboard():
    return render_template('ai/ai_dashboard.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    target_path = data.get('path', 'unknown.js').strip()
    source_code = data.get('code', None)
    js_files = []

    if not source_code:
        if not target_path or not os.path.exists(target_path):
            return jsonify({"error": "Invalid or missing path, and no source code provided."}), 400

        js_files = find_js_files(target_path)
        if not js_files:
            return jsonify({"error": "No JavaScript files found in the specified path."}), 404

        try:
            with open(js_files[0], "r", encoding="utf-8") as f:
                source_code = f.read()
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    extractor = FactExtractor()
    all_facts = []

    primary_source_code = source_code
    primary_ast = None
    total_project_lines = len(source_code.splitlines())

    try:
        ast = JavaScriptParser.parse(source_code)
        primary_ast = ast
        facts = extractor.extract(ast, target_path)
        all_facts.extend(facts)
    except ValueError as parse_err:
        return jsonify({
            "error": f"JavaScript parse error: {str(parse_err)}. Note: The analyzer uses esprima which may not support modern JS syntax (e.g. class static fields, optional chaining). Try simplifying the code or using a supported ES2018 syntax."
        }), 422

    engine = CleanCodeExpertSystem()
    recommendations = engine.analyze(all_facts)

    score = CleanCodeScorer.calculate_score(recommendations, total_project_lines)
    extracted_facts = extractor.get_extracted_facts_summary()
    ast_tree = ASTVisualizer.simplify_ast(primary_ast) if primary_ast else None
    refactored_preview = RefactoringEngine.generate_refactored_preview(primary_source_code, recommendations)
    radar_data = _build_radar_data(extracted_facts, recommendations)

    result = {
        "files_scanned": len(js_files),
        "source_code": primary_source_code,
        "clean_code_score": score,
        "extracted_facts": extracted_facts,
        "ast_tree": ast_tree,
        "refactored_preview": refactored_preview,
        "recommendations": [rec.to_dict() for rec in recommendations],
        "radar_data": radar_data
    }
    return jsonify(result)


@app.route('/api/re-analyze', methods=['POST'])
def re_analyze():
    data = request.json
    refactored_code = data.get('code', '').strip()

    if not refactored_code:
        return jsonify({"error": "No refactored code provided."}), 400

    try:
        total_lines = len(refactored_code.splitlines())
        ast = JavaScriptParser.parse(refactored_code)
        extractor = FactExtractor()
        facts = extractor.extract(ast, "refactored_code.js")

        engine = CleanCodeExpertSystem()
        recommendations = engine.analyze(facts)
        score = CleanCodeScorer.calculate_score(recommendations, total_lines)
        extracted_facts = extractor.get_extracted_facts_summary()
        radar_data = _build_radar_data(extracted_facts, recommendations)

    except Exception as e:
        print(f"[Re-Analyze] Analysis failed: {e}")
        return jsonify({"error": f"Re-analysis failed to parse the AI generated code: {str(e)}"}), 500

    return jsonify({
        "clean_code_score": score,
        "recommendations": [rec.to_dict() for rec in recommendations],
        "extracted_facts": extracted_facts,
        "radar_data": radar_data
    })



def _build_radar_data(extracted_facts, recommendations):
    if not extracted_facts:
        return None

    param_count = extracted_facts.get('parameter_count', 0)
    nesting_depth = extracted_facts.get('nesting_depth', 0)
    concerns = len(extracted_facts.get('concerns_detected', []))
    issue_count = len(recommendations) if recommendations else 0

    naming = max(0, 100 - (sum(1 for r in recommendations if r.rule_name == "Short Variable Name") * 25)) if recommendations else 100
    params = max(0, 100 - max(0, (param_count - 3) * 20))
    nesting = max(0, 100 - max(0, (nesting_depth - 2) * 20))
    srp = max(0, 100 - (concerns * 25))
    complexity = max(0, 100 - (issue_count * 10))

    return {
        "labels": ["Naming", "Parameters", "Nesting", "SRP", "Complexity"],
        "values": [naming, params, nesting, srp, complexity]
    }


if __name__ == '__main__':
    app.run(debug=True, port=5000)
