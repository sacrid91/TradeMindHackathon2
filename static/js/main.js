// static/js/main.js

// Optional: Theme Toggle (Future-Proof)
function initThemeToggle() {
    const toggle = document.getElementById('theme-toggle');
    if (!toggle) return;
  
    // Check user preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const saved = localStorage.getItem('dark_mode');
    const darkMode = saved ? JSON.parse(saved) : prefersDark;
  
    if (!darkMode) {
      document.body.classList.add('light-mode');
    }
  
    toggle.addEventListener('click', () => {
      document.body.classList.toggle('light-mode');
      const isLight = document.body.classList.contains('light-mode');
      localStorage.setItem('dark_mode', !isLight);
    });
  }
  
  // Run on load
  document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
  
    // Optional: Add confetti on insight load
    const insightPage = document.querySelector('h2[content*="AI Insight"]');
    if (insightPage) {
      console.log("Psychee analyzed.");
    }
  });