# Premium Theme Configuration for IntelliDesk AI
# Deep Dark Glassmorphism 

COLORS = {
    # Backgrounds
    "bg_root": "#050505",       # Deepest black for seamless look
    "bg_card": "#121212",       # Elevated card background
    "bg_glass": "#1a1a1a",      # Glassmorphism base
    
    # Accents (Premium Neon Glow)
    "accent_primary": "#3b82f6",    # Brilliant Blue
    "accent_hover": "#2563eb",      # Darker hover blue
    "accent_secondary": "#8b5cf6",  # Deep Purple secondary
    
    # Text
    "text_primary": "#ffffff",
    "text_secondary": "#9ca3af",
    "text_muted": "#52525b",
    
    # Borders & Shadows
    "border": "#27272a",
    "shadow_glow": "#3b82f644",     # Blue tinted shadow
    
    # Semantic Colors
    "success": "#10b981",       # Emerald Green
    "error": "#ef4444",         # Rose Red
    "warning": "#f59e0b",       # Amber
    "info": "#3b82f6",          # Blue
    
    # Chat specific
    "chat_user": "#212121",     # User bubble
    "chat_bot": "#18181b",      # Bot bubble
}

FONTS = {
    "h1": ("Segoe UI Variable Display", 28, "bold"),
    "h2": ("Segoe UI Variable Display", 20, "bold"),
    "body_large": ("Segoe UI Variable Text", 16),
    "body": ("Segoe UI Variable Text", 14),
    "body_small": ("Segoe UI Variable Text", 12),
    "mono": ("Consolas", 14),
    
    # Fallback fonts if Segoe UI Variable (Win11) isn't available
    "fallback_h1": ("Helvetica Neue", 28, "bold"),
    "fallback_body": ("Helvetica", 14)
}

SIZING = {
    "radius_large": 24,
    "radius_regular": 16,
    "radius_small": 8,
    "padding_large": 24,
    "padding_regular": 16,
    "padding_small": 8,
    "window_width": 1000,
    "window_height": 750
}
