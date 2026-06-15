import sys
import os

from analyzer.ast_parser import JavaScriptParser
from analyzer.fact_extractor import FactExtractor
from core.engine import CleanCodeExpertSystem
from utils.report_generator import ReportGenerator

IGNORED_DIRS = {"node_modules", "dist", "build", ".git"}

def find_js_files(target_path: str) -> list:
    """
    Finds all .js files in the given target path recursively.
    Ignores common output/dependency directories.
    """
    js_files = []
    if os.path.isfile(target_path):
        if target_path.endswith(".js"):
            js_files.append(target_path)
    elif os.path.isdir(target_path):
        for root, dirs, files in os.walk(target_path):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            
            for file in files:
                if file.endswith(".js"):
                    js_files.append(os.path.join(root, file))
    return js_files

def main():
    """
    Main entry point for the Clean Code Expert System.
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_js_file_or_directory>")
        sys.exit(1)

    target_path = sys.argv[1]
    if not os.path.exists(target_path):
        print(f"Error: Path '{target_path}' not found.")
        sys.exit(1)

    js_files = find_js_files(target_path)
    if not js_files:
        print(f"No JavaScript (.js) files found in '{target_path}'.")
        sys.exit(0)

    print(f"Found {len(js_files)} JavaScript file(s). Analyzing...\n")

    extractor = FactExtractor()
    all_facts = []

    # 1 & 2. Parse and Extract Facts for all files
    for file_path in js_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
            ast = JavaScriptParser.parse(source_code)
            facts = extractor.extract(ast, file_path)
            all_facts.extend(facts)
        except Exception as e:
            print(f"Warning: Failed to process '{file_path}'. Error: {e}")

    # 3. Run Expert System on all collected facts
    engine = CleanCodeExpertSystem()
    recommendations = engine.analyze(all_facts)

    # 4. Generate Report
    report = ReportGenerator.to_text(recommendations)
    print(report)

if __name__ == "__main__":
    main()
