document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('budget-form');
    const suggestionBox = document.getElementById('suggestion');
    const submitButton = document.querySelector('button[type="submit"]'); // Changed: Find button anywhere in document
    const exportButton = document.getElementById('export-budget');
    const templateSelect = document.getElementById('budget-template');
    const budgetInput = document.getElementById('budget');
    
    // Store budget data for export
    let currentBudgetData = null;

    // Template functionality
    const budgetTemplates = {
        'fresh_graduate': {
            name: 'Fresh Graduate',
            income_range: [18000, 25000],
            allocations: {
                'Food & Dining': 25,
                'Transportation': 15,
                'Utilities': 12,
                'Personal Care': 8,
                'Entertainment': 10,
                'Emergency Fund': 15,
                'Savings': 15
            }
        },
        'young_professional': {
            name: 'Young Professional',
            income_range: [25000, 40000],
            allocations: {
                'Food & Dining': 22,
                'Transportation': 18,
                'Utilities': 15,
                'Personal Care': 7,
                'Entertainment': 8,
                'Emergency Fund': 15,
                'Savings': 15
            }
        },
        'family_breadwinner': {
            name: 'Family Breadwinner',
            income_range: [35000, 60000],
            allocations: {
                'Food & Dining': 30,
                'Transportation': 15,
                'Utilities': 20,
                'Personal Care': 5,
                'Entertainment': 5,
                'Emergency Fund': 15,
                'Savings': 10
            }
        },
        'ofw_remittance': {
            name: 'OFW Remittance Manager',
            income_range: [40000, 80000],
            allocations: {
                'Food & Dining': 20,
                'Transportation': 10,
                'Utilities': 15,
                'Personal Care': 5,
                'Entertainment': 10,
                'Emergency Fund': 20,
                'Savings': 20
            }
        },
        'senior_executive': {
            name: 'Senior Executive',
            income_range: [60000, 120000],
            allocations: {
                'Food & Dining': 20,
                'Transportation': 12,
                'Utilities': 10,
                'Personal Care': 8,
                'Entertainment': 10,
                'Emergency Fund': 20,
                'Savings': 20
            }
        },
        'entrepreneur': {
            name: 'Entrepreneur',
            income_range: [30000, 150000],
            allocations: {
                'Food & Dining': 18,
                'Transportation': 15,
                'Utilities': 12,
                'Personal Care': 5,
                'Entertainment': 10,
                'Emergency Fund': 25,
                'Savings': 15
            }
        }
    };

    // Handle template selection
    if (templateSelect) {
        templateSelect.addEventListener('change', function() {
            const selectedTemplate = this.value;
            
            if (selectedTemplate && budgetTemplates[selectedTemplate]) {
                const template = budgetTemplates[selectedTemplate];
                
                // Show template info
                showTemplateInfo(template);
                
                // If budget is entered, show preview
                const budgetValue = parseFloat(budgetInput.value.replace(/[^0-9.]/g, ''));
                if (budgetValue && budgetValue > 0) {
                    showTemplatePreview(template, budgetValue);
                }
            } else {
                hideTemplateInfo();
            }
        });
    }

    // Handle budget input changes to update template preview
    if (budgetInput) {
        budgetInput.addEventListener('input', function() {
            const selectedTemplate = templateSelect?.value;
            
            if (selectedTemplate && budgetTemplates[selectedTemplate]) {
                const template = budgetTemplates[selectedTemplate];
                const budgetValue = parseFloat(this.value.replace(/[^0-9.]/g, ''));
                
                if (budgetValue && budgetValue > 0) {
                    showTemplatePreview(template, budgetValue);
                }
            }
        });
    }

    function showTemplateInfo(template) {
        const existingInfo = document.querySelector('.template-info');
        if (existingInfo) {
            existingInfo.remove();
        }

        const templateInfo = document.createElement('div');
        templateInfo.className = 'template-info';
        templateInfo.innerHTML = `
            <div style="background: linear-gradient(135deg, #1B4965, #5FA8D3); color: white; padding: 15px; border-radius: 8px; margin: 10px 0; box-shadow: 0 4px 12px rgba(27, 73, 101, 0.2);">
                <h4 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700;">📋 ${template.name} Template</h4>
                <p style="margin: 0 0 12px 0; font-size: 14px; color: rgba(255, 255, 255, 0.9);">
                    Recommended for income: ₱${template.income_range[0].toLocaleString()} - ₱${template.income_range[1].toLocaleString()}
                </p>
                <button onclick="suggestBudgetAmount('${Object.keys(budgetTemplates).find(key => budgetTemplates[key] === template)}')" 
                        style="background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.3); padding: 8px 16px; border-radius: 6px; font-size: 13px; cursor: pointer; transition: all 0.2s; font-weight: 600;"
                        onmouseover="this.style.background='rgba(255, 255, 255, 0.3)'" 
                        onmouseout="this.style.background='rgba(255, 255, 255, 0.2)'">
                    💡 Suggest Budget Amount
                </button>
            </div>
        `;

        templateSelect.parentNode.appendChild(templateInfo);
    }

    function showTemplatePreview(template, budget) {
        let existingPreview = document.querySelector('.template-preview');
        if (existingPreview) {
            existingPreview.remove();
        }

        const preview = document.createElement('div');
        preview.className = 'template-preview';
        preview.innerHTML = `
            <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 15px; margin: 10px 0;">
                <h5 style="margin: 0 0 12px 0; color: #333; font-size: 14px;">💡 Template Preview (₱${budget.toLocaleString()})</h5>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    ${Object.entries(template.allocations).map(([category, percentage]) => {
                        const amount = Math.round(budget * percentage / 100);
                        return `
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px 0;">
                                <span style="font-size: 13px; color: #666;">${category}</span>
                                <span style="font-weight: bold; color: #333;">₱${amount.toLocaleString()}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
                <button type="button" onclick="applyTemplate('${Object.keys(budgetTemplates).find(key => budgetTemplates[key] === template)}')" 
                        style="background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; margin-top: 10px; cursor: pointer; font-size: 12px;">
                    ✨ Apply This Template
                </button>
            </div>
        `;

        const templateInfo = document.querySelector('.template-info');
        if (templateInfo) {
            templateInfo.appendChild(preview);
        }
    }

    function hideTemplateInfo() {
        const existingInfo = document.querySelector('.template-info');
        if (existingInfo) {
            existingInfo.remove();
        }
    }

    // Global function to suggest budget amount based on template range
    window.suggestBudgetAmount = function(templateId) {
        const template = budgetTemplates[templateId];
        if (!template) return;

        const [minAmount, maxAmount] = template.income_range;
        const suggestedAmount = Math.round((minAmount + maxAmount) / 2);
        
        // Fill the budget input with suggested amount
        budgetInput.value = suggestedAmount.toLocaleString('en-US');
        
        // Trigger the input event to update formatting and show preview
        budgetInput.dispatchEvent(new Event('input'));
        
        // Show confirmation message
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #1B4965, #5FA8D3);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(27, 73, 101, 0.3);
            z-index: 1000;
            font-size: 14px;
            font-weight: 600;
            animation: slideIn 0.3s ease-out;
        `;
        notification.innerHTML = `💡 Budget set to ₱${suggestedAmount.toLocaleString()} (recommended midpoint)`;
        
        document.body.appendChild(notification);
        
        // Add animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    };

    // Global function to apply template (called from button click)
    window.applyTemplate = function(templateId) {
        const template = budgetTemplates[templateId];
        const budgetValue = parseFloat(budgetInput.value.replace(/[^0-9.]/g, ''));
        
        if (!template || !budgetValue) {
            alert('Please enter a budget amount first');
            return;
        }

        // Add template data to form submission
        const templateData = {
            template_id: templateId,
            template_name: template.name,
            allocations: {}
        };

        Object.entries(template.allocations).forEach(([category, percentage]) => {
            templateData.allocations[category] = Math.round(budgetValue * percentage / 100);
        });

        // Store template data for use in form submission
        form.templateData = templateData;

        // Show confirmation
        const confirmationDiv = document.createElement('div');
        confirmationDiv.className = 'template-applied';
        confirmationDiv.innerHTML = `
            <div style="background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 10px; border-radius: 4px; margin: 10px 0;">
                ✅ Template applied! Your budget will use the <strong>${template.name}</strong> allocation when calculated.
            </div>
        `;

        const preview = document.querySelector('.template-preview');
        if (preview) {
            preview.appendChild(confirmationDiv);
        }

        setTimeout(() => {
            const applied = document.querySelector('.template-applied');
            if (applied) applied.remove();
        }, 3000);
    };

    function showLoading(isLoading) {
        if (submitButton) {
            submitButton.disabled = isLoading;
            submitButton.innerHTML = isLoading ? 
                '<span class="spinner"></span> Calculating...' : 
                'CALCULATE BUDGET';
        }
        
        if (isLoading && suggestionBox) {
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
            const response = await fetch(url, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const responseData = await response.json();
            
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

            // Prepare data for AI tips - include template data if available
            const aiRequestData = {
                budget: cleanBudget,
                duration: duration
            };

            // Add template information if a template was applied
            if (form.templateData) {
                aiRequestData.template = form.templateData;
                aiRequestData.template_applied = true;
            }

            // First, get AI-powered budget tips from GROQ
            const aiTipsData = await fetchFromAPI('/api/tip', aiRequestData);

            // Get budget breakdown through gateway - include template data
            const breakdownRequestData = {
                amount: cleanBudget,
                duration
            };

            if (form.templateData) {
                breakdownRequestData.template = form.templateData;
            }

            const breakdownData = await fetchFromAPI('/api/budget/calculate', breakdownRequestData);

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
            
            // Format the AI tips content with enhanced structure and news links
            const lines = aiTips.tip.split('\n');
            let formattedContent = '';
            let inList = false;
            
            lines.forEach(line => {
                const trimmed = line.trim();
                if (!trimmed) {
                    if (inList) {
                        formattedContent += '</ul>';
                        inList = false;
                    }
                    return;
                }
                
                // Handle headers (lines starting with ## or ### for markdown-style headers)
                if (trimmed.startsWith('##')) {
                    if (inList) {
                        formattedContent += '</ul>';
                        inList = false;
                    }
                    const headerText = trimmed.replace(/^###+\s*/, '');
                    const headerLevel = trimmed.startsWith('###') ? 'h5' : 'h4';
                    formattedContent += `<${headerLevel} class="ai-section-header">${headerText}</${headerLevel}>`;
                }
                // Handle emoji headers (lines starting with emojis or **text**)
                else if (trimmed.match(/^[🤖💡📊🎯💰📰⚠️]/)) {
                    if (inList) {
                        formattedContent += '</ul>';
                        inList = false;
                    }
                    formattedContent += `<h4 class="ai-section-header">${trimmed}</h4>`;
                }
                // Handle bold sections
                else if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
                    if (inList) {
                        formattedContent += '</ul>';
                        inList = false;
                    }
                    const text = trimmed.slice(2, -2);
                    formattedContent += `<h5 class="ai-subsection">${text}</h5>`;
                }
                // Handle news links and external links
                else if (trimmed.includes('[') && trimmed.includes('](')) {
                    if (inList) {
                        formattedContent += '</ul>';
                        inList = false;
                    }
                    // Parse markdown-style links [text](url)
                    const linkRegex = /\[([^\]]+)\]\(([^\)]+)\)/g;
                    const processedLine = trimmed.replace(linkRegex, (match, text, url) => {
                        return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="ai-news-link">
                            ${text} 🔗
                        </a>`;
                    });
                    formattedContent += `<p class="ai-insight ai-with-links">${processedLine}</p>`;
                }
                // Handle list items
                else if (trimmed.startsWith('•') || trimmed.startsWith('- ')) {
                    if (!inList) {
                        formattedContent += '<ul class="ai-recommendations">';
                        inList = true;
                    }
                    let text = trimmed.replace(/^[•-]\s*/, '');
                    
                    // Process links within list items
                    const linkRegex = /\[([^\]]+)\]\(([^\)]+)\)/g;
                    text = text.replace(linkRegex, (match, linkText, url) => {
                        return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="ai-news-link">
                            ${linkText} 🔗
                        </a>`;
                    });
                    
                    formattedContent += `<li>${text}</li>`;
                }
                // Handle special alert lines (starting with ⚠️, 💡, 📈, etc.)
                else if (trimmed.match(/^[⚠️💡📈⛽⚡🎯]/)) {
                    if (inList) {
                        formattedContent += '</ul>';
                        inList = false;
                    }
                    formattedContent += `<div class="ai-alert">${trimmed}</div>`;
                }
                // Handle source citations (lines starting with *Sources:*)
                else if (trimmed.startsWith('*Sources:') && trimmed.endsWith('*')) {
                    if (inList) {
                        formattedContent += '</ul>';
                        inList = false;
                    }
                    const sourceText = trimmed.slice(1, -1); // Remove asterisks
                    formattedContent += `<div class="ai-sources">${sourceText}</div>`;
                }
                // Handle regular paragraphs
                else {
                    if (inList) {
                        formattedContent += '</ul>';
                        inList = false;
                    }
                    // Process links in regular paragraphs too
                    let processedLine = trimmed;
                    const linkRegex = /\[([^\]]+)\]\(([^\)]+)\)/g;
                    processedLine = processedLine.replace(linkRegex, (match, text, url) => {
                        return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="ai-news-link">
                            ${text} 🔗
                        </a>`;
                    });
                    formattedContent += `<p class="ai-insight">${processedLine}</p>`;
                }
            });
            
            // Close any open list
            if (inList) {
                formattedContent += '</ul>';
            }
            
            aiContent.innerHTML = formattedContent;
        } else {
            // Show placeholder message if no tips
            aiContent.innerHTML = `
                <div class="ai-insights-placeholder">
                    <div class="placeholder-icon">💡</div>
                    <h4>AI-Powered Insights</h4>
                    <p>Enter your budget and click "Calculate Budget" to get personalized financial insights and smart recommendations!</p>
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
        
        // Check if we're in demo mode to determine the correct bills URL
        const isDemoMode = window.demoMode || false;
        const billsUrl = isDemoMode ? '/demo/bills' : '/bills';
        
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
                ${totalBills > 0 ? `<p class="bills-tip">💡 <a href="${billsUrl}" style="color: var(--primary-color); text-decoration: none;">Manage your bills</a> to see even more accurate breakdowns!</p>` : `<p class="bills-tip">💡 <a href="${billsUrl}" style="color: var(--primary-color); text-decoration: none;">Add your bills</a> for a more accurate budget breakdown!</p>`}
            </div>
        `;
    }
});
