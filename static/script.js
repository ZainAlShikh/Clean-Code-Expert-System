document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const targetPathInput = document.getElementById('targetPath');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    const errorMessage = document.getElementById('errorMessage');
    const resultsSection = document.getElementById('resultsSection');
    const scanSummary = document.getElementById('scanSummary');
    const cardsContainer = document.getElementById('cardsContainer');

    analyzeBtn.addEventListener('click', async () => {
        const path = targetPathInput.value.trim();
        
        if (!path) {
            showError("Please enter a valid path.");
            return;
        }

        // Reset UI
        hideError();
        resultsSection.classList.add('hidden');
        cardsContainer.innerHTML = '';
        
        // Show Loader
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ path: path })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Something went wrong during analysis.");
            }

            displayResults(data);
        } catch (error) {
            showError(error.message);
        } finally {
            // Hide Loader
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }

    function displayResults(data) {
        scanSummary.innerHTML = `Scanned <strong>${data.files_scanned}</strong> JavaScript files. Found <strong>${data.recommendations.length}</strong> issues.`;
        
        if (data.recommendations.length === 0) {
            cardsContainer.innerHTML = `
                <div class="rec-card" style="text-align: center; color: #10b981;">
                    <h3>🎉 Your code looks perfectly clean! No refactoring needed.</h3>
                </div>
            `;
            resultsSection.classList.remove('hidden');
            return;
        }

        // Group by file path
        const grouped = data.recommendations.reduce((acc, rec) => {
            if (!acc[rec.file_path]) acc[rec.file_path] = [];
            acc[rec.file_path].push(rec);
            return acc;
        }, {});

        let delay = 0;

        for (const [filePath, recs] of Object.entries(grouped)) {
            const fileGroup = document.createElement('div');
            fileGroup.className = 'file-group';
            
            const fileTitle = document.createElement('h3');
            fileTitle.innerHTML = `📄 ${filePath}`;
            fileGroup.appendChild(fileTitle);

            recs.forEach(rec => {
                const card = document.createElement('div');
                card.className = 'rec-card';
                card.style.animationDelay = `${delay}s`;
                delay += 0.1;

                const lineStr = rec.line_number ? `Line ${rec.line_number}` : 'Global Scope';

                card.innerHTML = `
                    <div class="card-header">
                        <span class="rule-name">${rec.rule_name}</span>
                        <span class="severity-badge severity-${rec.severity}">${rec.severity}</span>
                    </div>
                    <div class="card-body">
                        <p><strong>Target:</strong> ${rec.target_name} (${lineStr})</p>
                        <p><strong>Issue:</strong> ${rec.description}</p>
                        <div class="suggestion">
                            💡 <strong>Suggestion:</strong> ${rec.suggestion}
                        </div>
                    </div>
                `;
                
                fileGroup.appendChild(card);
            });

            cardsContainer.appendChild(fileGroup);
        }

        resultsSection.classList.remove('hidden');
    }
});
