document.addEventListener('DOMContentLoaded', () => {
    const profileIcon = document.getElementById('profileIcon');
    const profileDropdown = document.getElementById('profileDropdown');
    
    // Toggle dropdown menu when profile icon is clicked
    profileIcon.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent this click from being captured by the document listener
        profileDropdown.classList.toggle('active');
    });
    
    // Close dropdown when clicking anywhere else on the page
    document.addEventListener('click', (e) => {
        if (!profileDropdown.contains(e.target) && !profileIcon.contains(e.target)) {
            profileDropdown.classList.remove('active');
        }
    });
    
    // Prevent clicks inside the dropdown from closing it
    profileDropdown.addEventListener('click', (e) => {
        e.stopPropagation();
    });
});
