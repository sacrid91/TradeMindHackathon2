// static/js/ai.js
// Optional: Show loading state when fetching AI insight
function initAILoader() {
    const insightButton = document.querySelector('.ai-insight-btn');
    if (!insightButton) return;
  
    insightButton.addEventListener('click', function () {
      const originalText = this.innerHTML;
      this.innerHTML = 'Analyzing Psychee...';
      this.disabled = true;
      this.style.opacity = '0.7';
  
      setTimeout(() => {
        this.innerHTML = originalText;
        this.disabled = false;
        this.style.opacity = '1';
      }, 2000);
    });
  }
  
  document.addEventListener('DOMContentLoaded', initAILoader);