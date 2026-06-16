# نظام Clean Code الخبير (Clean Code Expert System)

## نظرة عامة (Overview)
هذا المشروع عبارة عن نظام خبير (Expert System) ذكي يعتمد على القواعد (Rule-Based)، تم تصميمه لأتمتة عملية تحليل الشيفرة المصدرية (Source Code) المكتوبة بلغة JavaScript. يقوم النظام بتقييم الكود بناءً على مبادئ Clean Code و Refactoring المعتمدة (استناداً إلى أعمال Robert C. Martin و Martin Fowler) لاكتشاف العيوب التصميمية (Design Flaws)، الروائح البرمجية (Code Smells)، وعدم الكفاءة الهيكلية.

## القدرات الأساسية (Key Capabilities)
- **تحليل شجرة البنية المجردة (AST Parsing):** يقوم بتحويل كود الـ JavaScript الخام إلى شجرة AST مهيكلة باستخدام مكتبة `pyjsparser`.
- **تحليل شامل للمشروع (Project-Wide Analysis):** يقوم بتقييم ملفات متعددة ومترابطة في نفس الوقت، مما يسمح باكتشاف المشاكل عبر الملفات (Cross-File Issues) مثل الكود الميت (Dead Code) والبيانات المتكررة (Data Clumps).
- **محرك الاستدلال (Inference Engine):** يستخدم مكتبة `experta` لتنفيذ قواعد التسلسل الأمامي (Forward-Chaining Rules) على الحقائق (Facts) المستخرجة من الكود.
- **طرق التشغيل (Execution Modes):** يدعم كلاً من واجهة المستخدم الرسومية (Web UI) وواجهة سطر الأوامر (CLI) للتكامل الآلي (Automated Integration).

## القواعد المدعومة (Supported Rules)
تُطبق قاعدة المعرفة (Knowledge Base) حالياً قواعد التحليل التالية:
1. **التعقيد (Cyclomatic Complexity):** يكتشف الدوال التي تحتوي على تفرعات كثيرة وتعقيد في مسار التحكم (Control Flow) (الحد الأقصى > 10).
2. **التشعب العميق (Control Flow Nesting):** يكتشف الـ Arrow Anti-Pattern حيث تكون الجمل الشرطية (Conditions) أو الحلقات (Loops) متداخلة بشكل مبالغ فيه (الحد الأقصى > 3).
3. **التخلص من الكود الميت (Dead Code Elimination):** يحدد الدوال التي تم التصريح عنها (Declared) ولكن لم يتم استدعاؤها (Invoked) في أي مكان ضمن كامل المشروع الذي يتم تحليله.
4. **البيانات المتكررة (Data Clumps):** يكتشف الدوال في ملفات مختلفة التي تتشارك نفس قوائم المعاملات (Parameters) الطويلة والمطابقة، مما يشير إلى وجود مفهوم برمجي مفقود (Missing Domain Concept).
5. **الأرقام السحرية (Magic Numbers):** ينبه على وجود أرقام صلبة (Hardcoded Numeric Literals) في الشيفرة المصدرية غير مفهومة المعنى.
6. **طول الدالة (Method Length):** يكتشف الدوال التي تتجاوز قيود الطول المثالي (الحد الأقصى > 20 سطر).
7. **عدد المعاملات (Parameter Count):** ينبه على الدوال التي تحتوي على عدد كبير جداً من المعاملات (الحد الأقصى > 3).
8. **تسمية المتغيرات (Variable Naming):** يحدد المتغيرات ذات الأسماء غير المعبرة أو المختصرة بشكل مبالغ فيه.

## التثبيت (Installation)

1. قم باستنساخ (Clone) المستودع.
2. قم بإنشاء وتفعيل بيئة بايثون وهمية (Python Virtual Environment).
3. قم بتثبيت الاعتماديات المطلوبة (Dependencies):
```bash
pip install -r requirements.txt
```

## تعليمات الاستخدام (Usage Instructions)

### واجهة الويب (Web Interface)
لتشغيل واجهة المستخدم الرسومية:

```powershell
# 1. تجاوز سياسة التنفيذ إذا كانت مقيدة (Windows فقط)
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 2. تفعيل البيئة الوهمية (Virtual Environment)
.\.venv\Scripts\activate

# 3. تشغيل خادم التطبيق (Application Server)
python app.py
```
انتقل إلى `http://127.0.0.1:5000` في متصفح الويب الخاص بك. أدخل المسار المطلق (Absolute Path) لمجلد مشروع JavaScript الخاص بك لبدء التحليل.

### واجهة سطر الأوامر (CLI)
لتشغيل التحليل مباشرة من سطر الأوامر (Terminal) بدون واجهة الويب:

```powershell
.\.venv\Scripts\python.exe main.py "C:\absolute\path\to\javascript\project"
```

## بنية النظام (System Architecture)
- `analyzer/`: مسؤول عن تحليل كود الـ JavaScript إلى AST واستخراج الحقائق المنطقية الرسمية (`FactExtractor`).
- `core/`: يحتوي على محرك المعرفة (`experta` KnowledgeEngine)، تعريفات الحقائق (Facts)، وإعدادات القواعد (Rules).
- `models/`: يُعرّف هياكل البيانات (Data Structures) لتوصيات إعادة الهيكلة (Refactoring Recommendations).
- `utils/`: يتعامل مع تنسيق وإنشاء تقارير التحليل النهائية.
- `app.py` / `main.py`: نقاط الإدخال (Entry Points) لتطبيقات الويب و الـ CLI على التوالي.
