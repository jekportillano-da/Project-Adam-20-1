document.addEventListener('DOMContentLoaded', () => {
    const profileIcon = document.getElementById('profileIcon');
    const profileDropdown = document.getElementById('profileDropdown');
    
    if (!profileIcon || !profileDropdown) {
        console.error('Profile elements not found');
        return;
    }
    
    // Toggle dropdown menu when profile icon is clicked
    profileIcon.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('Profile icon clicked');
        
        // Update auth UI when dropdown opens
        if (typeof updateAuthUI === 'function') {
            await updateAuthUI();
        }
        
        profileDropdown.classList.toggle('active');
    });
    
    // Close dropdown when clicking anywhere else on the page
    document.addEventListener('click', (e) => {
        if (!profileDropdown.contains(e.target) && !profileIcon.contains(e.target)) {
            profileDropdown.classList.remove('active');
        }
    });
    
    // Handle menu item clicks with explicit targeting
    const budgetInsightsLink = document.getElementById('budget-insights-link');
    const monthlyBillsLink = document.getElementById('monthly-bills-link');
    
    if (budgetInsightsLink) {
        budgetInsightsLink.addEventListener('click', (e) => {
            console.log('Budget insights clicked, href:', budgetInsightsLink.href);
            if (budgetInsightsLink.href && budgetInsightsLink.href !== window.location.href + '#') {
                profileDropdown.classList.remove('active');
                window.location.href = budgetInsightsLink.href;
            }
            e.preventDefault();
        });
    }
    
    if (monthlyBillsLink) {
        monthlyBillsLink.addEventListener('click', (e) => {
            console.log('Monthly bills clicked, href:', monthlyBillsLink.href);
            if (!monthlyBillsLink.classList.contains('disabled') && monthlyBillsLink.href && monthlyBillsLink.href !== window.location.href + '#') {
                profileDropdown.classList.remove('active');
                window.location.href = monthlyBillsLink.href;
            }
            e.preventDefault();
        });
    }
    
    // Handle other menu items (login/register/logout)
    const loginLink = profileDropdown.querySelector('#auth-login a');
    const registerLink = profileDropdown.querySelector('#auth-register a');
    
    if (loginLink) {
        loginLink.addEventListener('click', (e) => {
            console.log('Login clicked');
            profileDropdown.classList.remove('active');
            // Let default navigation proceed
        });
    }
    
    if (registerLink) {
        registerLink.addEventListener('click', (e) => {
            console.log('Register clicked');
            profileDropdown.classList.remove('active');
            // Let default navigation proceed
        });
    }
});
