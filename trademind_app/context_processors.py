# trademind_app/context_processors.py

def theme_context(request):
    """
    Provides theme preference (dark/light mode) to all templates.
    
    For hackathon: Defaults to 'dark_mode' = True for maximum 'vibe'.
    Future: Can be extended to read from user session, cookies, or DB.
    
    Usage in templates:
        {% if dark_mode %}
            <link rel="stylesheet" href="/static/css/dark.css">
        {% else %}
            <link rel="stylesheet" href="/static/css/light.css">
        {% endif %}
    """
    # Default: Dark Mode (for trader vibe)
    # In future, check request.session or cookie
    dark_mode = True  # Override later via JS + cookie
    
    return {
        'dark_mode': dark_mode,
    }