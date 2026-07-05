document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const targetPathInput = document.getElementById('targetPath');
    const mainContent = document.getElementById('mainContent');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    const errorToast = document.getElementById('errorToast');
    const sidebarStats = document.getElementById('sidebarStats');
    const sidebarActions = document.getElementById('sidebarActions');
    const reAnalyzeBtn = document.getElementById('reAnalyzeBtn');
    
    // AI Modal Elements
    const openAiModalBtn = document.getElementById('openAiModalBtn');
    const aiModal = document.getElementById('aiModal');
    const closeAiModalBtn = document.getElementById('closeAiModalBtn');

    // Store last analysis data globally
    let lastData = null;
    let afterScore = null;

    analyzeBtn.addEventListener('click', runAnalysis);

    async function runAnalysis() {
        const path = targetPathInput.value.trim();
        if (!path) { showError("Please enter a valid path."); return; }

        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="btn-icon"></span> Analyzing...';
        loadingText.textContent = 'Analyzing code & generating AI refactoring...';
        loadingOverlay.classList.remove('hidden');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || "Analysis failed.");

            lastData = data;
            afterScore = null;
            applyDataToUI(data);
        } catch (err) {
            showError(err.message);
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span class="btn-icon"></span> Run Analysis';
            loadingOverlay.classList.add('hidden');
        }
    }

    function applyDataToUI(data) {
        renderAll(data);
        mainContent.classList.remove('hidden');
        sidebarStats.classList.remove('hidden');
        document.getElementById('improvementCard').classList.add('hidden');
        
        if (data.refactored_preview) {
            openAiModalBtn.classList.remove('hidden');
        }
    }

    // Auto-load from sessionStorage
    const savedData = sessionStorage.getItem('lastAnalysisData');
    const savedPath = sessionStorage.getItem('lastAnalysisPath');
    
    if (savedData && savedPath) {
        targetPathInput.value = savedPath;
        try {
            const data = JSON.parse(savedData);
            lastData = data;
            applyDataToUI(data);
        } catch (e) {
            console.error("Failed to parse saved data", e);
        }
    }

    // Re-Analyze button
    reAnalyzeBtn.addEventListener('click', async () => {
        if (!lastData || !lastData.refactored_preview) return;
        const code = lastData.refactored_preview.refactored_code;
        if (!code) { showError("No refactored code to re-analyze."); return; }

        loadingText.textContent = 'Re-analyzing the refactored code...';
        loadingOverlay.classList.remove('hidden');

        try {
            const response = await fetch('/api/re-analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || "Re-analysis failed.");

            afterScore = result.clean_code_score;
            renderImprovement(lastData.clean_code_score, afterScore, lastData.radar_data, result.radar_data);
        } catch (err) {
            showError(err.message);
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    });
    
    // AI Modal handlers
    if (openAiModalBtn && aiModal && closeAiModalBtn) {
        openAiModalBtn.addEventListener('click', () => {
            aiModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        });
        
        closeAiModalBtn.addEventListener('click', () => {
            aiModal.classList.add('hidden');
            document.body.style.overflow = '';
        });
        
        // Close on click outside
        aiModal.addEventListener('click', (e) => {
            if (e.target === aiModal) {
                aiModal.classList.add('hidden');
                document.body.style.overflow = '';
            }
        });
    }


    function showError(msg) {
        errorToast.textContent = msg;
        errorToast.classList.remove('hidden');
        setTimeout(() => errorToast.classList.add('hidden'), 4000);
    }

    function renderAll(data) {
        // Sidebar stats
        document.getElementById('filesScanned').textContent = data.files_scanned || 0;
        document.getElementById('issuesFound').textContent = data.recommendations ? data.recommendations.length : 0;
        renderScore(data.clean_code_score);

        // Sections
        renderSourceCode(data.source_code);
        renderAST(data.ast_tree);
        renderFacts(data.extracted_facts);
        renderProblems(data.recommendations);
        renderRuleTable(data.recommendations);
        renderRadar(data.radar_data, 'radarCanvas');
        renderRefactoring(data.refactored_preview, data.source_code);
    }

    function renderScore(score) {
        const scoreValue = document.getElementById('scoreValue');
        const scoreRing = document.getElementById('scoreRing');

        // Animated counter
        let current = 0;
        const step = Math.max(1, Math.ceil(score / 30));
        const timer = setInterval(() => {
            current = Math.min(current + step, score);
            scoreValue.textContent = current;
            scoreRing.setAttribute('stroke-dasharray', `${current}, 100`);
            if (current >= score) clearInterval(timer);
        }, 30);

        scoreRing.classList.remove('high', 'medium', 'low');
        if (score >= 80) scoreRing.classList.add('high');
        else if (score >= 50) scoreRing.classList.add('medium');
        else scoreRing.classList.add('low');
    }

    function renderSourceCode(code) {
        const el = document.getElementById('sourceCodeBlock');
        el.textContent = code || "// No source code";
        Prism.highlightElement(el);
    }

    function renderAST(tree) {
        const astVisual = document.getElementById('astVisual');
        astVisual.innerHTML = '';
        if (!tree) { astVisual.innerHTML = '<div style="color:var(--text-muted)">No AST</div>'; return; }

        function build(nodeData, container) {
            if (!nodeData) return;
            const el = document.createElement('div');
            el.className = 'ast-node';
            if (nodeData.name === 'Module') el.classList.add('n-module');
            else if (nodeData.name.includes('FunctionDef')) el.classList.add('n-func');
            else if (nodeData.name.includes('arguments')) el.classList.add('n-args');
            else if (nodeData.name === 'body') el.classList.add('n-body');
            el.textContent = nodeData.name;
            container.appendChild(el);

            if (nodeData.children && nodeData.children.length > 0) {
                const kids = document.createElement('div');
                kids.className = 'ast-children';
                const limit = Math.min(nodeData.children.length, 5);
                for (let i = 0; i < limit; i++) build(nodeData.children[i], kids);
                if (nodeData.children.length > 5) {
                    const more = document.createElement('div');
                    more.className = 'ast-node';
                    more.style.opacity = '0.4';
                    more.textContent = `... +${nodeData.children.length - 5} more`;
                    kids.appendChild(more);
                }
                container.appendChild(kids);
            }
        }
        build(tree, astVisual);
    }

    function renderFacts(facts) {
        const factsList = document.getElementById('factsList');
        factsList.innerHTML = '';
        if (!facts) return;
        const items = [
            `Parameter Count: ${facts.parameter_count}`,
            `Nesting Depth: ${facts.nesting_depth}`,
            `Function Calls: ${facts.function_calls}`,
        ];
        items.forEach(text => {
            const li = document.createElement('li');
            li.textContent = text;
            factsList.appendChild(li);
        });
        if (facts.concerns_detected && facts.concerns_detected.length > 0) {
            const li = document.createElement('li');
            li.innerHTML = `Concerns Detected:<div class="concern-list">${facts.concerns_detected.map(c => `<div> ${c}</div>`).join('')}</div>`;
            factsList.appendChild(li);
        }
    }

    function renderProblems(recs) {
        const container = document.getElementById('problemsContainer');
        container.innerHTML = '';
        if (!recs || recs.length === 0) {
            container.innerHTML = '<div style="color:var(--success);padding:1rem;"> No violations detected!</div>';
            return;
        }
        recs.forEach((rec, i) => {
            const card = document.createElement('div');
            card.className = `violation-card ${rec.severity}`;
            card.style.animationDelay = `${i * 0.05}s`;
            card.innerHTML = `
                <div class="violation-head">
                    <span class="violation-title">${rec.rule_name || rec.violation_type}</span>
                    <span class="sev-tag sev-${rec.severity}">${rec.severity}</span>
                </div>
                <div class="violation-body">
                    <p>${rec.description}</p>
                    <p>Strategy: <strong>${rec.strategy || ''}</strong></p>
                </div>`;
            container.appendChild(card);
        });
    }

    function renderRuleTable(recs) {
        const tbody = document.getElementById('ruleTableBody');
        tbody.innerHTML = '';
        if (!recs) return;
        const seen = new Set();
        recs.forEach((rec, idx) => {
            const rId = rec.rule_id || `R${idx + 1}`;
            if (seen.has(rId)) return;
            seen.add(rId);
            
            const condition = rec.condition || `Rule matched for: ${rec.target_name || 'Code Block'}`;
            const vType = rec.violation_type || rec.rule_name || "Unknown Violation";
            const strategy = rec.strategy || rec.suggestion || "Manual Refactoring";
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${rId}</strong></td>
                <td>${condition}</td>
                <td><span class="fired-badge">FIRED</span></td>
                <td>${vType}</td>
                <td>${strategy}</td>`;
            tbody.appendChild(tr);
        });
    }

    // ===== RADAR CHART (Pure Canvas) =====
    function renderRadar(radarData, canvasId, overlayData) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !radarData) return;
        const ctx = canvas.getContext('2d');
        const W = canvas.width, H = canvas.height;
        const cx = W / 2, cy = H / 2;
        const R = Math.min(cx, cy) - 40;
        const labels = radarData.labels;
        const values = radarData.values;
        const n = labels.length;
        const angleStep = (2 * Math.PI) / n;

        ctx.clearRect(0, 0, W, H);

        // Draw grid rings
        for (let ring = 1; ring <= 4; ring++) {
            const r = (R / 4) * ring;
            ctx.beginPath();
            for (let i = 0; i <= n; i++) {
                const angle = (angleStep * i) - Math.PI / 2;
                const x = cx + r * Math.cos(angle);
                const y = cy + r * Math.sin(angle);
                i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
            }
            ctx.strokeStyle = 'rgba(255,255,255,0.08)';
            ctx.stroke();
        }

        // Draw axes
        for (let i = 0; i < n; i++) {
            const angle = (angleStep * i) - Math.PI / 2;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(cx + R * Math.cos(angle), cy + R * Math.sin(angle));
            ctx.strokeStyle = 'rgba(255,255,255,0.1)';
            ctx.stroke();
        }

        // Draw data polygon
        function drawPoly(vals, fillColor, strokeColor) {
            ctx.beginPath();
            for (let i = 0; i <= n; i++) {
                const idx = i % n;
                const angle = (angleStep * idx) - Math.PI / 2;
                const r = (vals[idx] / 100) * R;
                const x = cx + r * Math.cos(angle);
                const y = cy + r * Math.sin(angle);
                i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
            }
            ctx.closePath();
            ctx.fillStyle = fillColor;
            ctx.fill();
            ctx.strokeStyle = strokeColor;
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        if (overlayData) {
            drawPoly(overlayData.values, 'rgba(244, 63, 94, 0.15)', '#f43f5e');
        }
        drawPoly(values, 'rgba(6, 182, 212, 0.25)', '#06b6d4');

        // Draw labels
        ctx.fillStyle = '#8888a0';
        ctx.font = '11px Outfit';
        ctx.textAlign = 'center';
        for (let i = 0; i < n; i++) {
            const angle = (angleStep * i) - Math.PI / 2;
            const lx = cx + (R + 22) * Math.cos(angle);
            const ly = cy + (R + 22) * Math.sin(angle);
            ctx.fillText(labels[i], lx, ly + 4);
        }

        // Draw dots
        for (let i = 0; i < n; i++) {
            const angle = (angleStep * i) - Math.PI / 2;
            const r = (values[i] / 100) * R;
            ctx.beginPath();
            ctx.arc(cx + r * Math.cos(angle), cy + r * Math.sin(angle), 3, 0, Math.PI * 2);
            ctx.fillStyle = '#06b6d4';
            ctx.fill();
        }
    }

    // ===== REFACTORING + DIFF =====
    function renderRefactoring(preview, originalCode) {
        if (!preview) return;

        // Structure diagram
        const diagram = document.getElementById('structureDiagram');
        diagram.innerHTML = '';
        if (preview.structure_preview) {
            const root = document.createElement('div');
            root.className = 'sd-box sd-root';
            root.textContent = preview.structure_preview.root;

            const kids = document.createElement('div');
            kids.className = 'sd-kids';
            preview.structure_preview.extracted.forEach(name => {
                const kid = document.createElement('div');
                kid.className = 'sd-kid';
                const box = document.createElement('div');
                box.className = 'sd-box';
                box.textContent = name;
                kid.appendChild(box);
                kids.appendChild(kid);
            });

            diagram.appendChild(root);
            diagram.appendChild(kids);
        }

        // Checklist
        const checklist = document.getElementById('refactoringChecklist');
        checklist.innerHTML = '';
        if (preview.applied_strategies) {
            preview.applied_strategies.forEach(s => {
                const div = document.createElement('div');
                div.innerHTML = `<span></span> ${s}`;
                checklist.appendChild(div);
            });
        }

        // Refactored Code
        const codeEl = document.getElementById('refactoredCodeBlock');
        codeEl.textContent = preview.refactored_code || "// No preview";
        Prism.highlightElement(codeEl);

        // Diff View
        renderDiff(originalCode || '', preview.refactored_code || '');

        // Tab switching
        document.querySelectorAll('.diff-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.diff-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                const view = tab.dataset.view;
                document.getElementById('codeAfterView').classList.toggle('hidden', view !== 'after');
                document.getElementById('codeDiffView').classList.toggle('hidden', view !== 'diff');
            });
        });
    }

    function renderDiff(before, after) {
        const output = document.getElementById('diffOutput');
        let html = '';

        if (typeof Diff !== 'undefined') {
            const diff = Diff.diffLines(before, after);
            diff.forEach(part => {
                const color = part.added ? 'diff-add' : part.removed ? 'diff-del' : 'diff-normal';
                const prefix = part.added ? '+ ' : part.removed ? '- ' : '  ';
                const lines = part.value.replace(/\n$/, '').split('\n');
                lines.forEach(line => {
                    html += `<span class="${color}">${prefix}${escapeHtml(line)}</span>\n`;
                });
            });
        } else {
            html = '<span style="color:red">Diff library failed to load.</span>';
        }

        output.innerHTML = html;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ===== IMPROVEMENT SECTION =====
    function renderImprovement(beforeScore, afterScoreVal, beforeRadar, afterRadar) {
        const card = document.getElementById('improvementCard');
        card.classList.remove('hidden');

        // Animate scores
        animateNumber('impBefore', beforeScore);
        animateNumber('impAfter', afterScoreVal);
        const delta = afterScoreVal - beforeScore;
        document.getElementById('impDelta').textContent = `+${delta}`;

        // Render comparison radar
        if (afterRadar) {
            renderRadar(afterRadar, 'radarCompareCanvas', beforeRadar);
        }

        // Scroll to it
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function animateNumber(elementId, target) {
        const el = document.getElementById(elementId);
        let current = 0;
        const step = Math.max(1, Math.ceil(target / 25));
        const timer = setInterval(() => {
            current = Math.min(current + step, target);
            el.textContent = current;
            if (current >= target) clearInterval(timer);
        }, 30);
    }
});

