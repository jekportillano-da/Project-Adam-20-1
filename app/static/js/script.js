document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('budget-form');
    const suggestionBox = document.getElementById('suggestion');
    const submitButton = form.querySelector('button[type="submit"]');

    // Format currency with commas
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'PHP'
        }).format(amount);
    }

    // Format response sections
    function formatResponse(response) {
        const sections = {
            summary: '',
            breakdown: '',
            tips: ''
        };

        const lines = response.trim().split('\n').filter(line => line.trim());
        let currentSection = '';

        lines.forEach(line => {
            if (line.startsWith('Daily Budget Summary:')) {
                currentSection = 'summary';
                // Extract the daily amount
                const amount = line.match(/PHP\s*[\d,]+(\.\d{2})?/);
                if (amount) {
                    sections.summary = `
                        <div class="budget-summary">
                            <h2>Daily Budget</h2>
                            <div class="amount">${amount[0]}</div>
                        </div>
                    `;
                }
            } else if (line.startsWith('Budget Breakdown:')) {
                currentSection = 'breakdown';
                sections.breakdown = '<div class="budget-breakdown"><h3>Budget Breakdown</h3><ul>';
            } else if (line.startsWith('Money-Saving Tips:')) {
                currentSection = 'tips';
                sections.tips = '<div class="money-tips"><h3>Money-Saving Tips</h3><ol>';
            } else if (line.trim()) {
                switch (currentSection) {
                    case 'breakdown':
                        if (line.startsWith('Savings and Discretionary:')) {
                            sections.breakdown += '<li class="section-header">Savings and Discretionary</li>';
                        } else if (line.includes(':')) {
                            const [category, amount] = line.split(':').map(s => s.trim());
                            sections.breakdown += `
                                <li class="${category === 'Total Essential Expenses' ? 'total-row' : ''}">
                                    <span class="category">${category}</span>
                                    <span class="amount">${amount}</span>
                                </li>
                            `;
                        }
                        break;
                    case 'tips':
                        if (line.startsWith('•')) {
                            // Handle bullet points - remove the bullet from content
                            const cleanLine = line.replace(/^[•]\s*/, '');
                            sections.tips += `<li class="tip-detail">${cleanLine}</li>`;
                        } else if (line.match(/^\d+\./)) {
                            // Handle numbered tips (1., 2., etc.)
                            sections.tips += `<li class="tip-title">${line}</li>`;
                        } else if (!line.toLowerCase().includes('here are')) {
                            sections.tips += `<li>${line}</li>`;
                        }
                        break;
                }
            }
        });

        sections.breakdown += '</ul></div>';
        sections.tips += '</ol></div>';

        return `
            ${sections.summary}
            <div class="result-card">
                ${sections.breakdown}
                ${sections.tips}
            </div>
        `;
    }

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const budget = document.getElementById('budget').value;
        const duration = document.getElementById('duration').value;
        
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner"></span> Generating...';
        suggestionBox.innerHTML = '<div class="loading">Analyzing your budget...</div>';
        
        try {
            const response = await fetch('/api/tip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ budget, duration })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.tip || 'Failed to generate budget tips');
            }

            suggestionBox.innerHTML = formatResponse(data.tip);
            
        } catch (error) {
            console.error('Error:', error);
            suggestionBox.innerHTML = `
                <div class="error-message">
                    <span class="error-icon">⚠️</span>
                    <p>${error.message || 'Something went wrong. Please try again.'}</p>
                </div>
            `;
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = 'Get Budget Tips';
        }
    });

    // Enhanced input validation with real-time formatting
    const budgetInput = document.getElementById('budget');
    
    budgetInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/[^0-9.]/g, '');
        
        if (value) {
            const num = parseFloat(value);
            if (num <= 0) {
                e.target.setCustomValidity('Please enter a positive amount');
            } else if (num > 1000000) {
                e.target.setCustomValidity('Amount cannot exceed 1,000,000');
            } else {
                e.target.setCustomValidity('');
            }

            // Format the number with commas while typing
            const parts = value.split('.');
            parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            e.target.value = parts.join('.');
        }
    });

    // Format initial values
    if (budgetInput.value) {
        const num = parseFloat(budgetInput.value.replace(/,/g, ''));
        if (!isNaN(num)) {
            budgetInput.value = num.toLocaleString('en-US');
        }
    }
});
