document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('budget-form');
    const suggestionBox = document.getElementById('suggestion');
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Initialize Charts
    const ctx = document.getElementById('savingsChart').getContext('2d');
    const savingsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['1mo', '2mo', '3mo', '6mo', '1yr'],
            datasets: [{
                label: 'Potential Savings',
                data: [0, 0, 0, 0, 0],
                borderColor: '#62B6CB',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(98, 182, 203, 0.1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => '₱' + value.toLocaleString()
                    }
                }
            }
        }
    });

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
            
            // Update insights based on budget data
            updateInsights(budget, duration, data.tip);
            
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

    function updateInsights(budget, duration, tipResponse) {
        const budgetNum = parseFloat(budget.replace(/,/g, ''));
        
        // Parse the breakdown to get discretionary and emergency fund amounts
        let discretionary = 0;
        let emergency = 0;
        
        tipResponse.split('\n').forEach(line => {
            if (line.includes('Discretionary:')) {
                discretionary = parseFloat(line.split(':')[1].trim().replace('PHP', '').replace(',', ''));
            }
            if (line.includes('Emergency Fund:')) {
                emergency = parseFloat(line.split(':')[1].trim().replace('PHP', '').replace(',', ''));
            }
        });

        // Calculate potential savings
        const monthlySavings = (discretionary + emergency) * (duration === 'daily' ? 30 : duration === 'weekly' ? 4 : 1);
        const projectedSavings = [1, 2, 3, 6, 12].map(months => monthlySavings * months);
        
        // Update savings chart
        savingsChart.data.datasets[0].data = projectedSavings;
        savingsChart.update();

        // Update emergency fund progress
        const emergencyGoal = 50000;
        const currentEmergency = emergency * (duration === 'daily' ? 30 : duration === 'weekly' ? 4 : 1);
        const progressPercent = Math.min((currentEmergency / emergencyGoal) * 100, 100);
        document.getElementById('emergencyProgress').style.width = progressPercent + '%';
        document.querySelector('.emergency-fund .current').textContent = 'Current: ₱' + currentEmergency.toLocaleString();

        // Update what-if scenarios with fixed decimal places
        const tenPercentMore = monthlySavings * 0.1;
        document.getElementById('tenPercentMore').textContent = '+₱' + tenPercentMore.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '/month';
        document.getElementById('yearlyPotential').textContent = '₱' + (monthlySavings * 12).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');

        // Update mood indicator with detailed insights
        const moodEl = document.getElementById('budgetMood');
        const moodLabel = document.querySelector('.mood-label');
        const moodInsight = document.querySelector('.mood-insight');
        
        // Calculate key metrics
        const savingsRate = ((emergency + discretionary) / budgetNum) * 100;
        const hasEmergencyFund = progressPercent >= 25;
        const goodSavingsRate = savingsRate >= 20;
        
        if (progressPercent > 50) {
            moodEl.textContent = '🤑';
            moodLabel.textContent = 'Excellent progress!';
            moodInsight.innerHTML = `
                <div class="insight-item success">
                    <span>✓ Strong emergency fund: ${progressPercent.toFixed(1)}% of goal</span>
                </div>
                <div class="insight-item">
                    <span>💡 Savings rate: ${savingsRate.toFixed(1)}% of income</span>
                </div>
                <div class="insight-item">
                    <span>💪 Keep it up! Consider investing excess savings</span>
                </div>
            `;
        } else if (progressPercent > 25) {
            moodEl.textContent = '😊';
            moodLabel.textContent = 'On track!';
            moodInsight.innerHTML = `
                <div class="insight-item success">
                    <span>✓ Building emergency fund: ${progressPercent.toFixed(1)}% of goal</span>
                </div>
                <div class="insight-item">
                    <span>💡 Savings rate: ${savingsRate.toFixed(1)}% of income</span>
                </div>
                <div class="insight-item">
                    <span>📈 Good progress! Stay consistent with savings</span>
                </div>
            `;
        } else {
            moodEl.textContent = '🤔';
            moodLabel.textContent = 'Room for improvement';
            moodInsight.innerHTML = `
                <div class="insight-item warning">
                    <span>⚠️ Low emergency fund: ${progressPercent.toFixed(1)}% of goal</span>
                </div>
                <div class="insight-item">
                    <span>💡 Savings rate: ${savingsRate.toFixed(1)}% of income</span>
                </div>
                <div class="insight-item">
                    <span>💪 Try to increase emergency savings first</span>
                </div>
            `;
        }
    }
});
