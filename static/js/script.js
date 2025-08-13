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

            // Show AI loading state
            showAILoading();

            // First, get AI-powered budget tips from GROQ
            const aiTipsData = await fetchFromAPI('/api/tip', {
                budget: cleanBudget,
                duration: duration
            });

            // Get budget breakdown through gateway
            const breakdownData = await fetchFromAPI('/api/budget/calculate', {
                amount: cleanBudget,
                duration
            });

            // Calculate savings forecast through gateway
            const savingsData = await fetchFromAPI('/api/savings/forecast', {
                monthly_savings: breakdownData.total_savings,
                emergency_fund: breakdownData.categories.emergency_fund,
                current_goal: 50000
            });

            // Get financial insights through gateway
            const insightsData = await fetchFromAPI('/api/insights/analyze', {
                budget_breakdown: breakdownData,
                savings_data: savingsData
            });

            // Update UI with all data including AI tips
            updateUIWithData(breakdownData, savingsData, insightsData, aiTipsData);
            
            // Store data for export including AI tips
            currentBudgetData = {
                budget: cleanBudget,
                duration: duration,
                breakdown: breakdownData,
                savings: savingsData,
                insights: insightsData,
                aiTips: aiTipsData,
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
        
        // Add budget breakdown with bills integration
        csvContent += "COMPREHENSIVE BUDGET BREAKDOWN\n";
        csvContent += "Category,Amount,Source\n";
        
        const { billsByCategory, totalBills } = getBillsByCategory();
        const allCategories = [
            'housing', 'food', 'transportation', 'utilities',
            'entertainment', 'insurance', 'subscriptions', 'other'
        ];
        
        // Track total essential with bills integration
        let csvTotalEssential = data.breakdown.total_essential || 0;
        
        allCategories.forEach(category => {
            let amount = data.breakdown.categories[category] || 0;
            let source = 'Calculated';
            
            // Use actual bill amount if available
            if (billsByCategory[category]) {
                amount = billsByCategory[category];
                source = 'Actual Bills';
            }
            
            // Only include categories with amounts
            if (amount > 0) {
                const formattedCategory = category.charAt(0).toUpperCase() + category.slice(1);
                csvContent += `${formattedCategory},${formatNumberForCSV(amount)},${source}\n`;
            }
        });
        
        // Adjust total essential if bills are integrated
        if (totalBills > 0) {
            const transportationBills = billsByCategory.transportation || 0;
            const utilitiesBills = billsByCategory.utilities || 0;
            const calculatedTransportation = data.breakdown.categories.transportation || 0;
            const calculatedUtilities = data.breakdown.categories.utilities || 0;
            
            csvTotalEssential = csvTotalEssential - calculatedTransportation - calculatedUtilities + totalBills;
        }
        
        // Add savings categories
        for (let category in data.breakdown.categories) {
            if (['emergency_fund', 'discretionary'].includes(category)) {
                const formattedCategory = category.split('_')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
                csvContent += `${formattedCategory},${formatNumberForCSV(data.breakdown.categories[category])},Calculated\n`;
            }
        }
        
        csvContent += `Total Essential Expenses,${formatNumberForCSV(csvTotalEssential)},${totalBills > 0 ? 'Bills Integrated' : 'Calculated'}\n`;
        csvContent += `Total Savings,${formatNumberForCSV(data.breakdown.total_savings)},Calculated\n`;
        
        if (totalBills > 0) {
            csvContent += `\nACTUAL BILLS INTEGRATION\n`;
            csvContent += `Total Bills Amount,${formatNumberForCSV(totalBills)}\n`;
            csvContent += "Bill Category,Amount\n";
            for (let category in billsByCategory) {
                const formattedCategory = category.charAt(0).toUpperCase() + category.slice(1);
                csvContent += `${formattedCategory},${formatNumberForCSV(billsByCategory[category])}\n`;
            }
        }
        
        csvContent += "\n";
        
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

    function updateUIWithData(breakdown, savings, insights, aiTips) {
        // Format and display budget breakdown (without AI tips - they go in right panel now)
        const breakdownHTML = formatBreakdown(breakdown);
        suggestionBox.innerHTML = breakdownHTML;
        
        // Update AI insights in the right panel
        updateAIInsights(aiTips);
        
        // NEW: Update health score and insights visualization
        updateHealthScoreDisplay(insights);
        
        // NEW: Update insights-based recommendations
        updateInsightsRecommendations(insights);
        
        // Update savings chart
        savingsChart.data.datasets[0].data = savings.monthly_projections;
        savingsChart.update();

        // Update emergency fund progress
        const emergencyProgressEl = document.getElementById('emergencyProgress');
        if (emergencyProgressEl) {
            emergencyProgressEl.style.width = savings.emergency_fund_progress + '%';
        }
        
        const emergencyCurrentEl = document.querySelector('.emergency-fund-compact .current') || 
                                  document.querySelector('.emergency-fund .current');
        if (emergencyCurrentEl) {
            emergencyCurrentEl.textContent = 'Current: ' + formatCurrency(breakdown.categories.emergency_fund);
        }

        // Update what-if scenarios - handle both old and new field names for compatibility
        const monthlyIncrease = savings.what_if_scenarios.monthly_10pct_more || 
                                savings.what_if_scenarios.ten_percent_increase || 0;
        const yearlyIncrease = savings.what_if_scenarios.yearly_10pct_more || 
                               savings.what_if_scenarios.yearly_potential || 0;
        
        const tenPercentMoreEl = document.getElementById('tenPercentMore');
        const yearlyPotentialEl = document.getElementById('yearlyPotential');
        
        if (tenPercentMoreEl) {
            tenPercentMoreEl.textContent = '+' + formatCurrency(monthlyIncrease) + '/month';
        }
        if (yearlyPotentialEl) {
            yearlyPotentialEl.textContent = '+' + formatCurrency(yearlyIncrease) + '/year';
        }
            
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

        // Update mood and insights with AI integration
        updateBudgetHealthWithAI(insights, aiTips, breakdown, savings);
    }

    // Enhanced AI-powered budget health analysis
    function updateBudgetHealthWithAI(insights, aiTips, breakdown, savings) {
        const moodEl = document.getElementById('budgetMood');
        const moodLabel = document.querySelector('.mood-label');
        const moodInsight = document.querySelector('.mood-insight');
        
        // Enhanced emoji selection based on health score with AI context
        let emoji, label, aiHealthInsight;
        
        // Extract AI insights for health analysis
        const aiContext = aiTips && aiTips.tip ? aiTips.tip : '';
        const savingsRate = (breakdown.total_savings / (breakdown.total_essential + breakdown.total_savings)) * 100;
        const emergencyFundProgress = savings.emergency_fund_progress || 0;
        
        if (insights.status === 'excellent') {
            const greatEmojis = ['🤑', '💰', '💎', '🚀', '🏆'];
            emoji = greatEmojis[Math.floor(Math.random() * greatEmojis.length)];
            label = 'Excellent progress!';
            aiHealthInsight = generateAIHealthInsight('excellent', savingsRate, emergencyFundProgress, aiContext);
        } else if (insights.status === 'on_track') {
            const moderateEmojis = ['😊', '👍', '💪', '📈', '✅'];
            emoji = moderateEmojis[Math.floor(Math.random() * moderateEmojis.length)];
            label = 'On track!';
            aiHealthInsight = generateAIHealthInsight('on_track', savingsRate, emergencyFundProgress, aiContext);
        } else {
            const improvementEmojis = ['😬', '🤔', '📊', '⚠️', '🔍'];
            emoji = improvementEmojis[Math.floor(Math.random() * improvementEmojis.length)];
            label = 'Room for improvement';
            aiHealthInsight = generateAIHealthInsight('needs_improvement', savingsRate, emergencyFundProgress, aiContext);
        }
        
        if (moodEl) {
            moodEl.textContent = emoji;
        }
        if (moodLabel) {
            moodLabel.textContent = label;
        }

        // Enhanced insights with AI-powered analysis
        if (moodInsight) {
            const combinedInsights = [
                ...insights.insights.map(insight => ({
                    type: insight.type,
                    message: insight.message,
                    source: 'system'
                })),
                {
                    type: 'ai-powered',
                    message: aiHealthInsight,
                    source: 'ai'
                }
            ];

            moodInsight.innerHTML = `
                <div class="health-score-container">
                    <div class="health-score">
                        <span class="score-label">Health Score</span>
                        <span class="score-value">${insights.health_score}%</span>
                    </div>
                    <div class="ai-health-badge">
                        <span class="ai-icon">🤖</span>
                        <span>AI Analysis</span>
                    </div>
                </div>
                <div class="insights-list">
                    ${combinedInsights.map(insight => `
                        <div class="insight-item ${insight.type} ${insight.source}">
                            ${insight.source === 'ai' ? '<span class="ai-indicator">🧠</span>' : ''}
                            <span class="insight-text">${insight.message}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="ai-recommendations">
                    <h5>🎯 Smart Recommendations</h5>
                    ${generateSmartRecommendations(breakdown, savings, insights, aiContext).map(rec => `
                        <div class="smart-rec">
                            <span class="rec-icon">${rec.icon}</span>
                            <span class="rec-text">${rec.text}</span>
                            <span class="rec-impact">${rec.impact}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }

    // Generate AI-powered health insights
    function generateAIHealthInsight(status, savingsRate, emergencyProgress, aiContext) {
        const insights = {
            excellent: [
                "Your financial discipline is paying off! You're building wealth at an impressive rate.",
                "You've mastered the balance between spending and saving - keep this momentum going!",
                "Your emergency fund is well-funded and your savings strategy is optimized.",
                "You're on track to achieve financial independence faster than average!"
            ],
            on_track: [
                "You're making solid progress! Small adjustments could accelerate your financial growth.",
                "Your budget shows good financial awareness with room for strategic improvements.",
                "You're building a strong foundation - consider increasing your savings rate gradually.",
                "Your financial habits are developing well, focus on consistency for better results."
            ],
            needs_improvement: [
                "There's significant opportunity to optimize your budget for better financial health.",
                "Small changes in your spending patterns could lead to substantial savings growth.",
                "Consider reviewing your essential expenses - some categories might have reduction potential.",
                "Building an emergency fund should be your immediate priority for financial stability."
            ]
        };

        const baseInsight = insights[status][Math.floor(Math.random() * insights[status].length)];
        
        // Add contextual information based on metrics
        let contextualAdd = '';
        if (savingsRate < 10) {
            contextualAdd = " Try to aim for at least 10% savings rate.";
        } else if (savingsRate > 20) {
            contextualAdd = ` Your ${savingsRate.toFixed(1)}% savings rate is excellent!`;
        }
        
        if (emergencyProgress < 25) {
            contextualAdd += " Focus on building your emergency fund first.";
        }

        return baseInsight + contextualAdd;
    }

    // Generate smart recommendations based on AI analysis
    function generateSmartRecommendations(breakdown, savings, insights, aiContext) {
        const recommendations = [];
        const savingsRate = (breakdown.total_savings / (breakdown.total_essential + breakdown.total_savings)) * 100;
        const emergencyProgress = savings.emergency_fund_progress || 0;

        // Emergency fund recommendations
        if (emergencyProgress < 50) {
            recommendations.push({
                icon: '🛡️',
                text: 'Prioritize emergency fund',
                impact: `${50 - emergencyProgress}% to safety net`
            });
        }

        // Savings rate recommendations
        if (savingsRate < 15) {
            recommendations.push({
                icon: '📈',
                text: 'Increase savings rate',
                impact: '+5% could save ₱' + Math.round((breakdown.total_essential + breakdown.total_savings) * 0.05).toLocaleString()
            });
        }

        // Category-specific recommendations
        const highestCategory = Object.entries(breakdown.categories)
            .filter(([key]) => ['housing', 'food', 'transportation', 'utilities', 'entertainment'].includes(key))
            .sort(([,a], [,b]) => b - a)[0];

        if (highestCategory && highestCategory[1] > breakdown.total_savings) {
            recommendations.push({
                icon: '🔍',
                text: `Review ${highestCategory[0]} expenses`,
                impact: '10% reduction = ₱' + Math.round(highestCategory[1] * 0.1).toLocaleString() + ' saved'
            });
        }

        // AI-derived recommendations from context
        if (aiContext.toLowerCase().includes('subscription') || aiContext.toLowerCase().includes('recurring')) {
            recommendations.push({
                icon: '📱',
                text: 'Audit subscriptions',
                impact: 'Cancel unused services'
            });
        }

        if (aiContext.toLowerCase().includes('meal') || aiContext.toLowerCase().includes('food')) {
            recommendations.push({
                icon: '🍽️',
                text: 'Optimize meal planning',
                impact: 'Save 15-25% on food'
            });
        }

        // Default recommendations if none generated
        if (recommendations.length === 0) {
            recommendations.push({
                icon: '💡',
                text: 'Track spending patterns',
                impact: 'Identify saving opportunities'
            });
        }

        return recommendations.slice(0, 3); // Limit to top 3 recommendations
    }

    function getBillsByCategory() {
        let bills = [];
        try {
            bills = JSON.parse(localStorage.getItem('bills') || '[]');
        } catch (e) {
            console.error('Error loading bills:', e);
        }
        
        const billsByCategory = {};
        let totalBills = 0;
        
        bills.forEach(bill => {
            if (!billsByCategory[bill.category]) {
                billsByCategory[bill.category] = 0;
            }
            billsByCategory[bill.category] += bill.amount;
            totalBills += bill.amount;
        });
        
        return { billsByCategory, totalBills };
    }

    function updateAIInsights(aiTips) {
        const aiPanel = document.getElementById('aiInsightsPanel');
        const aiContent = document.getElementById('aiInsightsContent');
        
        if (aiTips && aiTips.tip) {
            // Remove loading class if present
            aiPanel.classList.remove('loading');
            
            // Enhanced markdown-like formatting
            let formattedContent = aiTips.tip
                // Convert **text** to <strong>text</strong>
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                // Convert lines starting with emoji and ** to headers
                .replace(/^(🎯|📊|💡|📰|💰|⚖️|🎯) \*\*(.*?)\*\*/gm, '<h4><span class="emoji">$1</span> $2</h4>')
                // Convert bullet points
                .replace(/^• (.*)/gm, '<li>$1</li>')
                .replace(/^✅ (.*)/gm, '<li class="action-item">✅ $1</li>')
                .replace(/^⚠️ (.*)/gm, '<li class="alert-item">⚠️ $1</li>')
                .replace(/^💎 (.*)/gm, '<li class="investment-item">💎 $1</li>')
                .replace(/^🔥 (.*)/gm, '<li class="priority-high">🔥 $1</li>')
                .replace(/^💡 (.*)/gm, '<li class="priority-medium">💡 $1</li>')
                .replace(/^⚡ (.*)/gm, '<li class="priority-low">⚡ $1</li>')
                // Convert news links [Title](URL) to proper hyperlinks
                .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="news-link">$1 🔗</a>')
                // Convert paragraphs
                .split('\n')
                .map(line => {
                    line = line.trim();
                    if (line === '') return '';
                    if (line.startsWith('<h4>') || line.startsWith('<li')) return line;
                    if (line.includes(':') && !line.startsWith('<')) {
                        return `<p class="insight-detail">${line}</p>`;
                    }
                    return `<p>${line}</p>`;
                })
                .join('');
            
            // Wrap consecutive <li> elements in <ul>
            formattedContent = formattedContent
                .replace(/(<li[^>]*>.*?<\/li>)(?=\s*<li)/g, '$1')
                .replace(/(<li[^>]*>.*?<\/li>)(?!\s*<li)/g, '$1</ul>')
                .replace(/(<li[^>]*>)/g, function(match, p1, offset, string) {
                    const beforeLi = string.substring(0, offset);
                    if (!beforeLi.includes('<ul>') || beforeLi.lastIndexOf('</ul>') > beforeLi.lastIndexOf('<ul>')) {
                        return '<ul>' + p1;
                    }
                    return p1;
                });
            
            aiContent.innerHTML = formattedContent;
        } else {
            // Show placeholder message if no tips
            aiContent.innerHTML = `
                <div class="ai-insights-placeholder">
                    💡 Please enter a budget amount and calculate to generate personalized AI insights and money-saving tips!
                </div>
            `;
        }
    }

    function showAILoading() {
        const aiPanel = document.getElementById('aiInsightsPanel');
        const aiContent = document.getElementById('aiInsightsContent');
        
        // Add loading class and show spinner
        aiPanel.classList.add('loading');
        aiContent.innerHTML = `
            <div class="ai-insights-loading">
                <div class="ai-insights-spinner"></div>
                <span>🤖 Analyzing your budget and generating personalized insights...</span>
            </div>
        `;
    }

    function formatBreakdown(breakdown) {
        const { billsByCategory, totalBills } = getBillsByCategory();
        
        // Enhanced categories that include both calculated and actual bill amounts
        const allCategories = [
            'housing',
            'food', 
            'transportation', 
            'utilities',
            'entertainment',
            'insurance',
            'subscriptions',
            'other'
        ];
        
        const essentials = allCategories.map(category => {
            let amount = breakdown.categories[category] || 0;
            let source = 'calculated';
            let displayName = category.charAt(0).toUpperCase() + category.slice(1);
            
            // Use actual bill amount if available, otherwise use calculated amount
            if (billsByCategory[category]) {
                amount = billsByCategory[category];
                source = 'actual';
            }
            
            // Skip if amount is 0 and no bills for this category
            if (amount === 0 && !billsByCategory[category]) {
                return '';
            }
            
            return `
                <li class="${source === 'actual' ? 'actual-bill' : 'calculated'}">
                    <span class="category">
                        ${displayName}
                        ${source === 'actual' ? '<span class="bill-indicator">📋</span>' : ''}
                    </span>
                    <span class="amount">${formatCurrency(amount)}</span>
                </li>
            `;
        }).filter(item => item !== '').join('');

        // Calculate total essential expenses including actual bills
        let totalEssential = breakdown.total_essential || 0;
        if (totalBills > 0) {
            // Add actual bills to calculated essential amount, but avoid double counting
            // For transportation and utilities that exist in both
            const transportationBills = billsByCategory.transportation || 0;
            const utilitiesBills = billsByCategory.utilities || 0;
            const calculatedTransportation = breakdown.categories.transportation || 0;
            const calculatedUtilities = breakdown.categories.utilities || 0;
            
            // Replace calculated amounts with actual bills for these categories
            totalEssential = totalEssential - calculatedTransportation - calculatedUtilities + totalBills;
        }

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
                <h3>
                    Comprehensive Budget Breakdown
                    ${totalBills > 0 ? `
                    <div class="breakdown-legend">
                        <div class="legend-item">
                            <div class="legend-color legend-actual"></div>
                            <span>From Bills</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color legend-calculated"></div>
                            <span>Calculated</span>
                        </div>
                    </div>
                    ` : ''}
                </h3>
                ${totalBills > 0 ? `<p class="bills-integration-note">📋 Integrated with your actual bills (₱${formatCurrency(totalBills).replace('₱', '')})</p>` : ''}
                <ul class="breakdown-list">
                    ${essentials}
                    <li class="total-row">
                        <span class="category">Total Essential Expenses</span>
                        <span class="amount">${formatCurrency(totalEssential)}</span>
                    </li>
                    <li class="section-header">Savings and Discretionary</li>
                    ${savings}
                    <li class="total-row">
                        <span class="category">Total Savings</span>
                        <span class="amount">${formatCurrency(breakdown.total_savings)}</span>
                    </li>
                </ul>
                ${totalBills > 0 ? `<p class="bills-tip">💡 <a href="/bills" style="color: var(--primary-color); text-decoration: none;">Manage your bills</a> to see even more accurate breakdowns!</p>` : `<p class="bills-tip">💡 <a href="/bills" style="color: var(--primary-color); text-decoration: none;">Add your bills</a> for a more accurate budget breakdown!</p>`}
            </div>
        `;
    }
    
    // NEW: Update health score display with AI insights integration
    function updateHealthScoreDisplay(insights) {
        const healthContainer = document.getElementById('healthScoreContainer');
        const scoreValue = document.getElementById('healthScoreValue');
        const moodLabel = document.querySelector('.mood-label');
        const moodEmoji = document.querySelector('.mood-emoji');
        
        if (healthContainer && insights && insights.health_score !== undefined) {
            // Show the health score container
            healthContainer.style.display = 'flex';
            
            // Update score value
            if (scoreValue) {
                scoreValue.textContent = Math.round(insights.health_score);
            }
            
            // Update mood based on status
            if (moodLabel && moodEmoji) {
                switch(insights.status) {
                    case 'excellent':
                        moodLabel.textContent = 'Excellent!';
                        moodEmoji.textContent = '🎉';
                        break;
                    case 'on_track':
                        moodLabel.textContent = 'On Track!';
                        moodEmoji.textContent = '✅';
                        break;
                    case 'needs_improvement':
                        moodLabel.textContent = 'Needs Work';
                        moodEmoji.textContent = '⚠️';
                        break;
                    default:
                        moodLabel.textContent = 'Analyzing...';
                        moodEmoji.textContent = '🤖';
                }
            }
            
            // Add dynamic color based on score
            if (scoreValue) {
                const score = Math.round(insights.health_score);
                scoreValue.className = 'score-value';
                if (score >= 80) {
                    scoreValue.classList.add('score-excellent');
                } else if (score >= 60) {
                    scoreValue.classList.add('score-good');
                } else {
                    scoreValue.classList.add('score-needs-work');
                }
            }
        }
    }
    
    // NEW: Update insights-based recommendations
    function updateInsightsRecommendations(insights) {
        const moodInsight = document.querySelector('.mood-insight');
        
        if (insights && insights.insights && insights.recommendations && moodInsight) {
            // Create insights display
            let insightsHTML = '';
            
            // Add structured insights
            if (insights.insights.length > 0) {
                insightsHTML += '<div class="structured-insights">';
                insights.insights.forEach(insight => {
                    const iconMap = {
                        'success': '✅',
                        'warning': '⚠️', 
                        'info': 'ℹ️'
                    };
                    insightsHTML += `
                        <div class="insight-item insight-${insight.type}">
                            <span class="insight-icon">${iconMap[insight.type] || 'ℹ️'}</span>
                            <span class="insight-message">${insight.message}</span>
                        </div>
                    `;
                });
                insightsHTML += '</div>';
            }
            
            // Add recommendations
            if (insights.recommendations.length > 0) {
                insightsHTML += '<div class="structured-recommendations">';
                insightsHTML += '<h4>💡 Quick Actions:</h4>';
                insights.recommendations.forEach(recommendation => {
                    insightsHTML += `
                        <div class="recommendation-item">
                            <span class="rec-bullet">→</span>
                            <span class="rec-text">${recommendation}</span>
                        </div>
                    `;
                });
                insightsHTML += '</div>';
            }
            
            // Find or create insights container
            let insightsContainer = moodInsight.querySelector('.ai-enhanced-insights');
            if (!insightsContainer) {
                insightsContainer = document.createElement('div');
                insightsContainer.className = 'ai-enhanced-insights';
                moodInsight.appendChild(insightsContainer);
            }
            
            insightsContainer.innerHTML = insightsHTML;
        }
    }
});
