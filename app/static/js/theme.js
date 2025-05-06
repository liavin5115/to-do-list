document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    const theme = localStorage.getItem('theme') || 'light';
    
    // Set initial theme
    html.setAttribute('data-theme', theme);
    updateThemeButton(theme);

    themeToggle.addEventListener('click', function() {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeButton(newTheme);
    });
});

function updateThemeButton(theme) {
    const button = document.getElementById('themeToggle');
    if (theme === 'dark') {
        button.innerHTML = '<i class="fas fa-moon"></i>';
        button.title = 'Switch to light mode';
    } else {
        button.innerHTML = '<i class="fas fa-sun"></i>';
        button.title = 'Switch to dark mode';
    }
}