// Script to force left alignment on input fields - using the Monthly Bills approach
document.addEventListener('DOMContentLoaded', function() {
    // Force left alignment on budget input and duration select
    const budgetInput = document.getElementById('budget');
    const durationSelect = document.getElementById('duration');
    
    function forceLeftAlignment(element) {
        if (!element) return;
        
        // Apply styles immediately
        element.style.cssText = `
            text-align: left !important; 
            direction: ltr !important;
            text-indent: 0 !important;
            padding-left: 10px !important;
            -webkit-text-align: left !important;
            -moz-text-align: left !important;
        `;
        
        if (element.tagName.toLowerCase() === 'select') {
            element.style.textAlignLast = 'left';
        }
        
        // Set HTML attribute as well
        element.setAttribute('align', 'left');
        
        // Apply to children if any
        if (element.children && element.children.length > 0) {
            Array.from(element.children).forEach(child => {
                child.style.textAlign = 'left';
                child.style.direction = 'ltr';
            });
        }
    }
    
    // Apply to budget input
    if (budgetInput) {
        forceLeftAlignment(budgetInput);
        
        // Add event listeners to maintain alignment
        ['input', 'focus', 'blur', 'change', 'click'].forEach(event => {
            budgetInput.addEventListener(event, () => {
                forceLeftAlignment(budgetInput);
                setTimeout(() => forceLeftAlignment(budgetInput), 10); // Apply again after a small delay
            });
        });
    }
    
    // Apply to duration select
    if (durationSelect) {
        forceLeftAlignment(durationSelect);
        
        // For selects, also force alignment on all options
        if (durationSelect.options) {
            Array.from(durationSelect.options).forEach(option => {
                option.style.textAlign = 'left';
                option.style.direction = 'ltr';
            });
        }
    }
    
    // Apply to all input elements in budget-form for good measure
    const budgetForm = document.getElementById('budget-form');
    if (budgetForm) {
        const inputs = budgetForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            forceLeftAlignment(input);
            
            // Add event listeners to maintain alignment for all inputs
            ['input', 'focus', 'blur', 'change', 'click'].forEach(event => {
                input.addEventListener(event, () => {
                    forceLeftAlignment(input);
                });
            });
        });
    }
    
    // Override form styles on window load as well
    window.addEventListener('load', function() {
        if (budgetInput) forceLeftAlignment(budgetInput);
        if (durationSelect) forceLeftAlignment(durationSelect);
        
        // Force all input fields in the form to be left-aligned
        if (budgetForm) {
            const inputs = budgetForm.querySelectorAll('input, select');
            inputs.forEach(input => forceLeftAlignment(input));
        }
    });
});
