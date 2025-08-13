// Helper functions to update insights panels
function updateSavingsPanel(savingsData) {
    console.log('Updating savings panel:', savingsData);
    
    // Update emergency fund progress
    const emergencyProgress = document.getElementById('emergencyProgress');
    if (emergencyProgress && savingsData.emergency_fund_progress) {
        const percentage = Math.min(parseFloat(savingsData.emergency_fund_progress), 100);
        emergencyProgress.style.width = percentage + '%';
        
        // Update progress labels with real data
        const currentLabel = document.querySelector('.progress-labels .current');
        const goalLabel = document.querySelector('.progress-labels .goal');
        if (currentLabel && goalLabel) {
            const goal = 50000; // Default goal
            const current = (goal * percentage) / 100;
            currentLabel.textContent = `Current: ₱${current.toLocaleString()}`;
            goalLabel.textContent = `Goal: ₱${goal.toLocaleString()}`;
        }
    }

    // Update savings forecast section  
    const savingsForecastSection = document.querySelector('.savings-forecast-bottom');
    if (savingsForecastSection && savingsData.monthly_projections) {
        const projections = savingsData.monthly_projections;
        // Replace the chart container with text-based forecast for now
        const chartContainer = savingsForecastSection.querySelector('.chart-container');
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="forecast-content" style="padding: 20px; text-align: center;">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 15px;">
                        <div class="forecast-item">
                            <h4>Monthly Growth</h4>
                            <p style="font-size: 1.5em; color: var(--primary-color); font-weight: bold;">₱${parseFloat(projections[0] || 0).toLocaleString()}</p>
                        </div>
                        <div class="forecast-item">
                            <h4>6-Month Target</h4>
                            <p style="font-size: 1.5em; color: var(--secondary-color); font-weight: bold;">₱${parseFloat(projections[3] || 0).toLocaleString()}</p>
                        </div>
                        <div class="forecast-item">
                            <h4>1-Year Projection</h4>
                            <p style="font-size: 1.5em; color: var(--accent-color); font-weight: bold;">₱${parseFloat(projections[4] || 0).toLocaleString()}</p>
                        </div>
                    </div>
                </div>
            `;
        }
    }
}

function updateInsightsPanel(insightsData) {
    console.log('Updating insights panel:', insightsData);
    
    // Update AI insights content
    const aiInsightsContent = document.getElementById('aiInsightsContent');
    if (aiInsightsContent && insightsData.insights) {
        aiInsightsContent.innerHTML = `
            <div class="ai-insights-active">
                <div class="insight-item">
                    <h4>💡 Smart Recommendations</h4>
                    <p>${insightsData.insights.recommendation || 'Great job managing your budget!'}</p>
                </div>
                <div class="insight-item">
                    <h4>📊 Budget Health Score</h4>
                    <p>Your budget looks <strong>${insightsData.insights.health_status || 'healthy'}</strong></p>
                </div>
                <div class="insight-item">
                    <h4>🎯 Optimization Tips</h4>
                    <p>${insightsData.insights.optimization_tip || 'Consider increasing your emergency fund by 5%'}</p>
                </div>
            </div>
        `;
    }

    // Update budget health indicator in the emergency fund section
    const budgetMoodEmoji = document.getElementById('budgetMood');
    const moodLabel = document.querySelector('.mood-label');
    if (budgetMoodEmoji && moodLabel && insightsData.insights) {
        budgetMoodEmoji.textContent = insightsData.insights.health_emoji || '😊';
        moodLabel.textContent = insightsData.insights.health_status || 'On track!';
    }
}
