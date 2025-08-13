document.addEventListener('DOMContentLoaded', () => {
    console.log('Budget Buddy loading...');
    
    // Get form elements
    const form = document.getElementById('budget-form');
    const templateSelect = document.getElementById('budget-template');
    const budgetInput = document.getElementById('budget');
    const suggestionBox = document.getElementById('suggestion');
    
    console.log('Elements found:', {
        form: !!form,
        templateSelect: !!templateSelect,
        budgetInput: !!budgetInput,
        suggestionBox: !!suggestionBox
    });

    // Template definitions
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
            console.log('Template selected:', selectedTemplate);
            
            if (selectedTemplate && budgetTemplates[selectedTemplate]) {
                const template = budgetTemplates[selectedTemplate];
                console.log('Template found:', template);
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

    // Show template information
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

    // Show template preview
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

    // Hide template info
    function hideTemplateInfo() {
        const existingInfo = document.querySelector('.template-info');
        if (existingInfo) {
            existingInfo.remove();
        }
    }

    // Global functions for onclick handlers
    window.suggestBudgetAmount = function(templateId) {
        const template = budgetTemplates[templateId];
        if (!template) return;

        const [minAmount, maxAmount] = template.income_range;
        const suggestedAmount = Math.round((minAmount + maxAmount) / 2);
        
        budgetInput.value = suggestedAmount.toLocaleString('en-US');
        budgetInput.dispatchEvent(new Event('input'));
        
        // Show notification
        alert(`Budget set to ₱${suggestedAmount.toLocaleString()} (recommended midpoint)`);
    };

    window.applyTemplate = function(templateId) {
        const template = budgetTemplates[templateId];
        const budgetValue = parseFloat(budgetInput.value.replace(/[^0-9.]/g, ''));
        
        if (!template || !budgetValue) {
            alert('Please enter a budget amount first');
            return;
        }

        // Store template data for form submission
        const templateData = {
            template_id: templateId,
            template_name: template.name,
            allocations: {}
        };

        Object.entries(template.allocations).forEach(([category, percentage]) => {
            templateData.allocations[category] = Math.round(budgetValue * percentage / 100);
        });

        form.templateData = templateData;
        alert(`Template applied! Your budget will use the ${template.name} allocation.`);
    };

    // Handle budget input changes
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

    // Form submission
    if (form) {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            console.log('Form submitted');
            
            const budget = budgetInput.value;
            const duration = document.getElementById('duration').value;
            
            console.log('Budget:', budget, 'Duration:', duration);
            
            try {
                // Show loading state
                const submitButton = document.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.innerHTML = 'Calculating...';
                }
                
                // Clean budget input
                const cleanBudget = parseFloat(budget.replace(/[^0-9.]/g, ''));
                if (isNaN(cleanBudget) || cleanBudget <= 0) {
                    throw new Error('Please enter a valid budget amount');
                }

                // Prepare data for budget calculation
                const breakdownRequestData = {
                    amount: cleanBudget,
                    duration: duration
                };

                // Add template information if a template was applied
                if (form.templateData) {
                    breakdownRequestData.template = form.templateData;
                    console.log('Sending template data:', form.templateData);
                }

                // Call the budget calculation API
                console.log('Calling budget API with:', breakdownRequestData);
                const response = await fetch('/api/budget/calculate', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(breakdownRequestData)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `API request failed: ${response.status}`);
                }

                const breakdownData = await response.json();
                console.log('Budget calculation result:', breakdownData);

                // Now call savings and insights services for the financial insights panel
                try {
                    // Calculate savings forecast
                    console.log('Calling savings API...');
                    const savingsResponse = await fetch('/api/savings/forecast', {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({
                            monthly_savings: breakdownData.total_savings,
                            emergency_fund: breakdownData.categories.emergency_fund || 0,
                            current_goal: 50000
                        })
                    });

                    let savingsData = null;
                    if (savingsResponse.ok) {
                        savingsData = await savingsResponse.json();
                        updateSavingsPanel(savingsData);
                    }

                    // Get financial insights
                    console.log('Calling insights API...');
                    const insightsResponse = await fetch('/api/insights/analyze', {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({
                            budget_breakdown: breakdownData,
                            savings_data: savingsData
                        })
                    });

                    if (insightsResponse.ok) {
                        const insightsData = await insightsResponse.json();
                        updateInsightsPanel(insightsData);
                    }

                } catch (insightsError) {
                    console.error('Insights error:', insightsError);
                    // Don't break the main flow if insights fail
                }

                // Display the main budget results
                if (suggestionBox) {
                    suggestionBox.innerHTML = `
                        <div style="background: #e8f5e8; border: 1px solid #4caf50; border-radius: 8px; padding: 20px; margin: 20px 0;">
                            <h3 style="color: #2e7d32; margin: 0 0 15px 0;">✅ Budget Calculation Complete!</h3>
                            <div style="display: grid; gap: 10px;">
                                <div><strong>Total Essential:</strong> ₱${parseFloat(breakdownData.total_essential).toLocaleString()}</div>
                                <div><strong>Total Savings:</strong> ₱${parseFloat(breakdownData.total_savings).toLocaleString()}</div>
                                <h4 style="margin: 15px 0 10px 0; color: #2e7d32;">Category Breakdown:</h4>
                                ${Object.entries(breakdownData.categories).map(([category, amount]) => 
                                    `<div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #e0e0e0;">
                                        <span style="text-transform: capitalize;">${category.replace('_', ' ')}</span>
                                        <span style="font-weight: bold;">₱${parseFloat(amount).toLocaleString()}</span>
                                    </div>`
                                ).join('')}
                            </div>
                            ${form.templateData ? `<p style="margin-top: 15px; font-style: italic; color: #666;">✨ Using ${form.templateData.template_name} template</p>` : ''}
                        </div>
                    `;
                }

            } catch (error) {
                console.error('Error:', error);
                if (suggestionBox) {
                    suggestionBox.innerHTML = `
                        <div style="background: #ffebee; border: 1px solid #f44336; border-radius: 8px; padding: 20px; margin: 20px 0;">
                            <h3 style="color: #c62828; margin: 0 0 10px 0;">⚠️ Error</h3>
                            <p style="color: #c62828; margin: 0;">${error.message}</p>
                        </div>
                    `;
                }
            } finally {
                // Reset button state
                const submitButton = document.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'CALCULATE BUDGET';
                }
            }
        });
    }
});
