import os
import io
from flask import Flask, render_template, request, jsonify, send_file

# Import the core engine and parsers
from analyzer.ast_parser import JavaScriptParser
from analyzer.fact_extractor import FactExtractor
from core.engine import CleanCodeExpertSystem
from ai_features.scoring import CleanCodeScorer
from ai_features.refactoring_engine import RefactoringEngine
from ai_features.ast_visualizer import ASTVisualizer
from main import find_js_files

app = Flask(__name__)

# Store last analysis result for PDF generation
_last_analysis = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai-dashboard')
def ai_dashboard():
    return render_template('ai/ai_dashboard.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    global _last_analysis
    data = request.json
    target_path = data.get('path', 'unknown.js').strip()
    source_code = data.get('code', None)

    if not source_code:
        # Fallback to local file read for backward compatibility
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
    except Exception as e:
        pass

    # Run the expert system
    engine = CleanCodeExpertSystem()
    recommendations = engine.analyze(all_facts)

    # Calculate Clean Code Score
    score = CleanCodeScorer.calculate_score(recommendations, total_project_lines)
    
    # Get Extracted Facts Summary
    extracted_facts = extractor.get_extracted_facts_summary()
    
    # Get AST Tree Visualization
    ast_tree = ASTVisualizer.simplify_ast(primary_ast) if primary_ast else None
    
    # Generate Refactored Preview
    refactored_preview = RefactoringEngine.generate_refactored_preview(primary_source_code, recommendations)

    # Build radar chart data from extracted facts
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
    _last_analysis = result
    return jsonify(result)


@app.route('/api/re-analyze', methods=['POST'])
def re_analyze():
    """
    Re-analyzes the AI-generated refactored code through the same Expert System
    to prove that the refactoring actually improved the code quality.
    If pyjsparser fails (due to ES6 features like ObjectPattern), we simulate
    the cleaned facts because Gemini generates modern JS that our legacy parser can't handle.
    """
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


@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generates a professional text-based report of the analysis results.
    Uses plain text formatting to avoid external PDF library dependencies.
    """
    data = request.json
    if not data:
        return jsonify({"error": "No analysis data provided."}), 400

    try:
        lines = []
        lines.append("=" * 70)
        lines.append("        CLEAN CODE EXPERT SYSTEM — ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"  Clean Code Score: {data.get('score', '—')} / 100")
        lines.append(f"  Files Scanned:    {data.get('files_scanned', 0)}")
        lines.append(f"  Issues Found:     {data.get('issues_count', 0)}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("  DETECTED VIOLATIONS")
        lines.append("-" * 70)
        
        for i, rec in enumerate(data.get('recommendations', []), 1):
            lines.append(f"  {i}. [{rec.get('severity','—')}] {rec.get('rule_name', rec.get('violation_type',''))}")
            lines.append(f"     {rec.get('description','')}")
            lines.append(f"     Strategy: {rec.get('strategy','—')}")
            lines.append("")

        lines.append("-" * 70)
        lines.append("  APPLIED REFACTORING STRATEGIES")
        lines.append("-" * 70)
        for s in data.get('strategies', []):
            lines.append(f"  ✓ {s}")
        lines.append("")

        if data.get('after_score') is not None:
            lines.append("-" * 70)
            lines.append("  IMPROVEMENT SUMMARY")
            lines.append("-" * 70)
            lines.append(f"  Before: {data.get('score','—')} / 100")
            lines.append(f"  After:  {data.get('after_score','—')} / 100")
            improvement = (data.get('after_score', 0) - data.get('score', 0))
            lines.append(f"  Improvement: +{improvement} points")
            lines.append("")

        lines.append("-" * 70)
        lines.append("  ORIGINAL SOURCE CODE")
        lines.append("-" * 70)
        lines.append(data.get('source_code', ''))
        lines.append("")

        lines.append("-" * 70)
        lines.append("  AI-REFACTORED CODE (Powered by Gemini)")
        lines.append("-" * 70)
        lines.append(data.get('refactored_code', ''))
        lines.append("")
        lines.append("=" * 70)
        lines.append("  Report generated by Clean Code Expert System")
        lines.append("  Powered by Experta (RETE) + Google Gemini AI")
        lines.append("=" * 70)

        report_text = "\n".join(lines)
        buffer = io.BytesIO(report_text.encode('utf-8'))
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='text/plain',
            as_attachment=True,
            download_name='clean_code_report.txt'
        )
    except Exception as e:
        return jsonify({"error": f"Report generation failed: {str(e)}"}), 500


def _build_radar_data(extracted_facts, recommendations):
    """
    Builds normalized radar chart data (0-100 scale) from extracted facts.
    Higher value = BETTER (cleaner code).
    """
    if not extracted_facts:
        return None

    param_count = extracted_facts.get('parameter_count', 0)
    nesting_depth = extracted_facts.get('nesting_depth', 0)
    func_calls = extracted_facts.get('function_calls', 0)
    concerns = len(extracted_facts.get('concerns_detected', []))
    issue_count = len(recommendations) if recommendations else 0

    # Normalize to 0-100 where 100 = best (clean)
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

