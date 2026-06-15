# Knowledge-Based Expert System for Automated Clean Code Refactoring

An intelligent, rule-based expert system that automatically analyzes JavaScript projects and provides context-aware Clean Code and Refactoring recommendations.

## 🚀 Features
- **Abstract Syntax Tree (AST) Parsing:** Converts raw JavaScript into a structured format using `pyjsparser` (Pure Python).
- **Rule-Based Inference Engine:** Powered by `experta` to evaluate code against standard Clean Code principles.
- **Recursive Project Scanning:** Pass an entire project directory, and it will intelligently find and scan all `.js` files while ignoring dependency folders like `node_modules` and `dist`.
- **Beautiful Web Interface:** Comes with a modern, glassmorphism-themed GUI for a seamless user experience.
- **CLI Support:** Can also be run directly from the terminal for CI/CD or fast checks.

## 🧠 Supported Rules
Currently, the knowledge base supports the following Clean Code heuristics:
1. **Long Method Rule:** Detects functions exceeding 20 lines and suggests extracting methods.
2. **Too Many Parameters Rule:** Detects functions taking more than 3 parameters and suggests introducing Parameter Objects.
3. **Short Variable Name Rule:** Flags meaningless variable names (like `n` or `c`) while safely ignoring common loop counters like `i` and `j`.
4. **Complex Condition Rule:** Analyzes `if` statements with more than 2 logical operators (`&&`, `||`) and suggests condition simplification.

## 🛠️ Installation

1. Clone or download this project.
2. Set up a Python Virtual Environment (recommended).
3. Install the dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage (طريقة التشغيل)

### 1. تشغيل واجهة الويب (Web UI - Recommended)
الواجهة الرسومية توفر تجربة مستخدم ممتازة وتفاعلية. لتشغيل الخادم المحلي:

```powershell
# 1. تفعيل البيئة الوهمية (إذا كنت تستخدم Windows)
.\.venv\Scripts\activate

# 2. تشغيل تطبيق الـ Web
python app.py
```
بعد تشغيل الأمر، افتح المتصفح الخاص بك وانتقل إلى الرابط:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

في حقل النص، قم بلصق **المسار المطلق (Absolute Path)** للمجلد أو الملف الخاص بك (مثلاً: `C:\Users\Name\Desktop\Project`) ثم اضغط على زر التحليل.

---

### 2. التشغيل عبر سطر الأوامر (CLI)
إذا كنت تفضل السرعة أو استخدام النظام ضمن أدوات أخرى، يمكنك تشغيله مباشرة:

```powershell
# تفعيل البيئة الوهمية أولاً
.\.venv\Scripts\activate

# تشغيل الفحص على مجلد أو ملف محدد
python main.py "C:\path\to\your\javascript\project"
```

## 🏗️ Architecture
- `analyzer/`: Responsible for parsing the JavaScript into AST and extracting Expert System "Facts".
- `core/`: The heart of the system. Contains the `experta` KnowledgeEngine, Facts schemas, and the rules definition.
- `models/`: Domain classes for formatting the refactoring recommendations.
- `utils/`: Generators for JSON and Text reports.
- `app.py` / `main.py`: The application entry points (Web and CLI).

## 🔮 Future Work
- Add Auto-fix capabilities.
- Support more complex architectural smells (e.g., God Class).
- Add support for TypeScript via Tree-sitter.
