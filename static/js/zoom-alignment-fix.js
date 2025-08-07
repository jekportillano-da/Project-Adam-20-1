// Script to fix input alignment issues at different zoom levels

document.addEventListener('DOMContentLoaded', function() {
    const budgetInput = document.getElementById('budget');
    const durationSelect = document.getElementById('duration');
    
    // Function to fix alignment
    function fixAlignment() {
        // Apply to budget input
        if (budgetInput) {
            budgetInput.style.cssText = `
                text-align: left !important;
                direction: ltr !important;
                text-indent: 0 !important;
                padding-left: 10px !important;
            `;
        }
        
        // Apply to duration select
        if (durationSelect) {
            durationSelect.style.cssText = `
                text-align: left !important;
                direction: ltr !important;
                text-indent: 0 !important;
                padding-left: 10px !important;
                text-align-last: left !important;
            `;
            
            // Apply to each option
            if (durationSelect.options) {
                Array.from(durationSelect.options).forEach(option => {
                    option.style.textAlign = 'left';
                    option.style.direction = 'ltr';
                });
            }
        }
    }
    
    // Fix alignment initially
    fixAlignment();
    
    // Fix alignment on window resize (which includes zoom changes)
    window.addEventListener('resize', fixAlignment);
    
    // Fix alignment after any input
    if (budgetInput) {
        ['input', 'focus', 'blur', 'change'].forEach(event => {
            budgetInput.addEventListener(event, fixAlignment);
        });
    }
    
    // Fix alignment after select changes
    if (durationSelect) {
        ['change', 'focus', 'blur'].forEach(event => {
            durationSelect.addEventListener(event, fixAlignment);
        });
    }
    
    // Apply after a slight delay to ensure DOM is fully processed
    setTimeout(fixAlignment, 100);
    
    // Check periodically to make sure alignment persists
    setInterval(fixAlignment, 1000);
});
