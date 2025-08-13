// Minimal test script to check if JavaScript is working
console.log('JavaScript is loading...');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded');
    
    const templateSelect = document.getElementById('budget-template');
    console.log('Template select found:', !!templateSelect);
    
    if (templateSelect) {
        templateSelect.addEventListener('change', function() {
            console.log('Template changed to:', this.value);
            alert('Template selected: ' + this.value);
        });
    } else {
        console.log('Template select not found');
        alert('Template select element not found!');
    }
});
