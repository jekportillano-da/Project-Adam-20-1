document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('budget-form');
    const suggestionBox = document.getElementById('suggestion');
    const submitButton = form.querySelector('button[type="submit"]');
    const exportButton = document.getElementById('export-budget');
    
    // Store budget data for export
    let currentBudgetData = null;

    function showLoading(isLoading) {
        submitButton.disabled = isLoading;
        submitButton.innerHTML = isLoading ? 
            '<span class="spinner"></span> Calculating...' : 
            'Calculate Budget';
        
        if (isLoading) {
            suggestionBox.innerHTML = '<div class="loading">Analyzing your budget...</div>';
        }
    }
    
    function showError(message) {
        suggestionBox.innerHTML = `
            <div class="error-message">
                <span class="error-icon">⚠️</span>
                <p>${message}</p>
            </div>
        `;
    }
    
    // Initialize Chart with proper currency formatting
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
                },
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            // Convert label to more readable format
                            const label = tooltipItems[0].label;
                            if (label === '1mo') return '1 month from now';
                            if (label === '2mo') return '2 months from now';
                            if (label === '3mo') return '3 months from now';
                            if (label === '6mo') return '6 months from now';
                            if (label === '1yr') return '1 year from now';
                            return label;
                        },
                        label: function(context) {
                            // Format the tooltip value with currency
                            const value = context.raw;
                            const formatted = formatCurrency(value);
                            
                            // Calculate growth if previous data point exists
                            let growthText = '';
                            if (context.dataIndex > 0) {
                                const previousValue = context.dataset.data[context.dataIndex - 1];
                                const growth = value - previousValue;
                                const growthPercent = previousValue > 0 ? (growth / previousValue * 100).toFixed(1) : 0;
                                growthText = `\nGrowth: ${formatCurrency(growth)} (${growthPercent}%)`;
                            }
                            
                            return `Projected savings: ${formatted}${growthText}`;
                        }
                    },
                    padding: 10,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    bodyFont: {
                        size: 14
                    },
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => formatCurrency(value)
                    }
                }
            }
        }
    });

    // Format currency with commas and decimals
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-PH', {
            style: 'currency',
            currency: 'PHP',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }


    async function fetchFromAPI(url, data) {
        try {
            console.log('Fetching from:', url);
            console.log('With data:', data);
            
            const response = await fetch(url, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(data)
            });

            console.log('Response status:', response.status);
            const responseData = await response.json();
            console.log('Response data:', responseData);
            
            if (!response.ok) {
                throw new Error(responseData.detail || `API request failed: ${response.status}`);
            }

            return responseData;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const budget = document.getElementById('budget').value;
        const duration = document.getElementById('duration').value;
        
        try {
            showLoading(true);

            // Clean budget input
            const cleanBudget = parseFloat(budget.replace(/[^0-9.]/g, ''));
            if (isNaN(cleanBudget) || cleanBudget <= 0) {
                throw new Error('Please enter a valid budget amount');
            }

            // Get budget breakdown
            const breakdownData = await fetchFromAPI('http://localhost:8001/calculate', {
                amount: cleanBudget,
                duration
            });

            // Calculate savings forecast
            const savingsData = await fetchFromAPI('http://localhost:8002/forecast', {
                monthly_savings: breakdownData.total_savings,
                emergency_fund: breakdownData.categories.emergency_fund,
                current_goal: 50000
            });

            // Get financial insights
            const insightsData = await fetchFromAPI('http://localhost:8003/analyze', {
                budget_breakdown: breakdownData,
                savings_data: savingsData
            });

            // Update UI with all data
            updateUIWithData(breakdownData, savingsData, insightsData);
            
            // Store data for export
            currentBudgetData = {
                budget: cleanBudget,
                duration: duration,
                breakdown: breakdownData,
                savings: savingsData,
                insights: insightsData,
                timestamp: new Date().toISOString()
            };
            
            // Enable export button
            exportButton.disabled = false;
            
        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'Something went wrong. Please try again.');
        } finally {
            showLoading(false);
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
    
    // Export button functionality
    exportButton.addEventListener('click', function() {
        if (!currentBudgetData) return;
        
        exportBudgetPlan(currentBudgetData);
    });
    
    // Function for formatting numbers for CSV export (without currency symbols)
    function formatNumberForCSV(amount) {
        // Parse the value if it's a string
        if (typeof amount === 'string') {
            amount = parseFloat(amount);
        }
        
        // Return a simple number formatted with 2 decimal places
        return amount.toFixed(2);
    }
    
    // Function to export budget plan
    function exportBudgetPlan(data) {
        // Create CSV content
        let csvContent = "data:text/csv;charset=utf-8,";
        
        // Add header
        csvContent += "Budget Buddy - Smart Financial Planning\n";
        csvContent += `Generated on: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}\n\n`;
        
        // Add budget details
        csvContent += "BUDGET OVERVIEW\n";
        csvContent += `Amount,${formatNumberForCSV(data.budget)}\n`;
        csvContent += `Time Period,${data.duration.charAt(0).toUpperCase() + data.duration.slice(1)}\n\n`;
        
        // Add budget breakdown
        csvContent += "BUDGET BREAKDOWN\n";
        csvContent += "Category,Amount\n";
        
        for (let category in data.breakdown.categories) {
            const formattedCategory = category.split('_')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
            csvContent += `${formattedCategory},${formatNumberForCSV(data.breakdown.categories[category])}\n`;
        }
        
        csvContent += `Total Essential Expenses,${formatNumberForCSV(data.breakdown.total_essential)}\n`;
        csvContent += `Total Savings,${formatNumberForCSV(data.breakdown.total_savings)}\n\n`;
        
        // Add savings forecast
        csvContent += "SAVINGS FORECAST\n";
        csvContent += "Time Period,Projected Amount\n";
        
        const timeLabels = ['1 Month', '2 Months', '3 Months', '6 Months', '1 Year'];
        data.savings.monthly_projections.forEach((amount, index) => {
            if (index < timeLabels.length) {
                csvContent += `${timeLabels[index]},${formatNumberForCSV(amount)}\n`;
            }
        });
        
        csvContent += `\nEmergency Fund Progress,${data.savings.emergency_fund_progress}%\n\n`;
        
        // Add what-if calculations
        csvContent += "WHAT IF CALCULATIONS\n";
        csvContent += `If you save 10% more each month,${formatNumberForCSV(data.savings.what_if_scenarios.monthly_10pct_more || data.savings.what_if_scenarios.ten_percent_increase || 0)}/month\n`;
        csvContent += `Yearly potential,${formatNumberForCSV(data.savings.what_if_scenarios.yearly_10pct_more || data.savings.what_if_scenarios.yearly_potential || 0)}/year\n\n`;
        
        // Add insights
        csvContent += "FINANCIAL INSIGHTS\n";
        csvContent += `Overall Health Score,${data.insights.health_score}%\n`;
        csvContent += `Status,${data.insights.status.replace(/_/g, ' ').toUpperCase()}\n\n`;
        
        // Add recommendations
        csvContent += "RECOMMENDATIONS\n";
        data.insights.recommendations.forEach(rec => {
            csvContent += `• ${rec}\n`;
        });
        
        // Encode and create download link
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `budget_plan_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(link);
        
        // Trigger download
        link.click();
        
        // Clean up
        document.body.removeChild(link);
    }

    function updateUIWithData(breakdown, savings, insights) {
        // Format and display budget breakdown
        const breakdownHTML = formatBreakdown(breakdown);
        suggestionBox.innerHTML = breakdownHTML;
        
        // Update savings chart
        savingsChart.data.datasets[0].data = savings.monthly_projections;
        savingsChart.update();

        // Update emergency fund progress
        document.getElementById('emergencyProgress').style.width = savings.emergency_fund_progress + '%';
        document.querySelector('.emergency-fund .current').textContent = 
            'Current: ' + formatCurrency(breakdown.categories.emergency_fund);

        // Update what-if scenarios - handle both old and new field names for compatibility
        const monthlyIncrease = savings.what_if_scenarios.monthly_10pct_more || 
                                savings.what_if_scenarios.ten_percent_increase || 0;
        const yearlyIncrease = savings.what_if_scenarios.yearly_10pct_more || 
                               savings.what_if_scenarios.yearly_potential || 0;
        
        document.getElementById('tenPercentMore').textContent = '+' + formatCurrency(monthlyIncrease) + '/month';
        document.getElementById('yearlyPotential').textContent = '+' + formatCurrency(yearlyIncrease) + '/year';
            
        // Add new what-if information
        const whatIfSection = document.querySelector('.what-if-scenarios');
        
        // Remove old explanation if it exists
        const oldExplanation = document.querySelector('.what-if-explanation');
        if (oldExplanation) {
            oldExplanation.remove();
        }
        
        // Add explanation text
        const explanationDiv = document.createElement('div');
        explanationDiv.className = 'what-if-explanation';
        explanationDiv.innerHTML = `
            <p class="explanation-text">What would happen if you saved 10% more each month?</p>
        `;
        
        // Check if explanation already exists
        const existingExplanation = whatIfSection.querySelector('.what-if-explanation');
        if (!existingExplanation) {
            whatIfSection.insertBefore(explanationDiv, whatIfSection.querySelector('.scenario-container'))
        } else {
            existingExplanation.replaceWith(explanationDiv);
        }
        
        // Add detailed what-if information
        const additionalInfo = document.createElement('div');
        additionalInfo.className = 'additional-what-if';
        
        const monthlyInterest = savings.what_if_scenarios.monthly_interest_gain || 0;
        const monthsToGoal = parseInt(savings.what_if_scenarios.months_to_goal || 0);
        const monthsSaved = parseInt(savings.what_if_scenarios.months_saved || 0);
        
        additionalInfo.innerHTML = `
            <div class="what-if-row">
                <div class="what-if-title">Time to reach goal:</div>
                <div class="what-if-value-container">
                    <div class="what-if-value">${monthsToGoal} months</div>
                    <div class="what-if-info" title="Estimated time to reach your emergency fund goal at current saving rate">ⓘ</div>
                </div>
            </div>
            <div class="what-if-row">
                <div class="what-if-title">With 10% more savings:</div>
                <div class="what-if-value-container">
                    <div class="what-if-value">${monthsToGoal - monthsSaved} months (save ${monthsSaved} months)</div>
                    <div class="what-if-info" title="You could reach your goal faster by increasing your monthly savings by just 10%">ⓘ</div>
                </div>
            </div>
            <div class="what-if-row">
                <div class="what-if-title">Monthly interest earned:</div>
                <div class="what-if-value-container">
                    <div class="what-if-value">${formatCurrency(monthlyInterest)}</div>
                    <div class="what-if-info" title="Potential interest earned monthly with a 4% annual interest rate">ⓘ</div>
                </div>
            </div>
        `;
        
        // Check if the additional info is already there
        if (!document.querySelector('.additional-what-if')) {
            whatIfSection.appendChild(additionalInfo);
        } else {
            // Replace existing additional info
            document.querySelector('.additional-what-if').replaceWith(additionalInfo);
        }
        
        // Add bottom explanation
        const bottomExplanation = document.createElement('div');
        bottomExplanation.className = 'what-if-bottom-note';
        bottomExplanation.innerHTML = `
            <p>Small changes in your saving habits can have a significant impact over time. 
               Increasing your monthly contribution by just 10% could help you reach your goals faster.</p>
        `;
        
        // Check if the bottom explanation is already there
        if (!document.querySelector('.what-if-bottom-note')) {
            whatIfSection.appendChild(bottomExplanation);
        } else {
            // Replace existing bottom explanation
            document.querySelector('.what-if-bottom-note').replaceWith(bottomExplanation);
        }

        // Update mood and insights
        const moodEl = document.getElementById('budgetMood');
        const moodLabel = document.querySelector('.mood-label');
        const moodInsight = document.querySelector('.mood-insight');
        
        // Enhanced emoji selection based on health score
        let emoji, label;
        if (insights.status === 'excellent') {
            // For excellent financial standing
            const greatEmojis = ['🤑', '💰', '💎', '🚀', '🏆'];
            emoji = greatEmojis[Math.floor(Math.random() * greatEmojis.length)];
            label = 'Excellent progress!';
        } else if (insights.status === 'on_track') {
            // For moderate/on track financial standing
            const moderateEmojis = ['😊', '👍', '💪', '📈', '✅'];
            emoji = moderateEmojis[Math.floor(Math.random() * moderateEmojis.length)];
            label = 'On track!';
        } else {
            // For underperforming financial standing
            const improvementEmojis = ['😬', '🤔', '📊', '⚠️', '🔍'];
            emoji = improvementEmojis[Math.floor(Math.random() * improvementEmojis.length)];
            label = 'Room for improvement';
        }
        
        moodEl.textContent = emoji;
        moodLabel.textContent = label;

        // Display insights
        moodInsight.innerHTML = insights.insights.map(insight => `
            <div class="insight-item ${insight.type}">
                <span>${insight.message}</span>
            </div>
        `).join('');
    }

    function formatBreakdown(breakdown) {
        const essentials = ['food', 'transportation', 'utilities'].map(category => `
            <li>
                <span class="category">${category.charAt(0).toUpperCase() + category.slice(1)}</span>
                <span class="amount">${formatCurrency(breakdown.categories[category])}</span>
            </li>
        `).join('');

        const savings = ['emergency_fund', 'discretionary'].map(category => `
            <li>
                <span class="category">${category.split('_').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                ).join(' ')}</span>
                <span class="amount">${formatCurrency(breakdown.categories[category])}</span>
            </li>
        `).join('');

        return `
            <div class="budget-breakdown">
                <h3>Budget Breakdown</h3>
                <ul class="breakdown-list">
                    ${essentials}
                    <li class="total-row">
                        <span class="category">Total Essential Expenses</span>
                        <span class="amount">${formatCurrency(breakdown.total_essential)}</span>
                    </li>
                    <li class="section-header">Savings and Discretionary</li>
                    ${savings}
                    <li class="total-row">
                        <span class="category">Total Savings</span>
                        <span class="amount">${formatCurrency(breakdown.total_savings)}</span>
                    </li>
                </ul>
            </div>
        `;
    }
});
