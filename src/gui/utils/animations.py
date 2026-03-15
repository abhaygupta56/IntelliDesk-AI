import time
import threading

def fade_in(widget, target_alpha=1.0, duration=0.3, step=0.05):
    """Fade in a toplevel window."""
    def _animate():
        current_alpha = 0.0
        widget.attributes("-alpha", current_alpha)
        widget.deiconify()  # Ensure visible
        
        steps = int(duration / step)
        increment = target_alpha / steps
        
        for _ in range(steps):
            current_alpha += increment
            try:
                widget.attributes("-alpha", min(current_alpha, target_alpha))
                time.sleep(step)
            except:
                break
                
    threading.Thread(target=_animate, daemon=True).start()

def fade_out_and_destroy(widget, duration=0.2, step=0.05):
    """Fade out a toplevel window and destroy it."""
    def _animate():
        current_alpha = widget.attributes("-alpha")
        steps = int(duration / step)
        decrement = current_alpha / steps
        
        for _ in range(steps):
            current_alpha -= decrement
            try:
                widget.attributes("-alpha", max(current_alpha, 0.0))
                time.sleep(step)
            except:
                break
        try:
            widget.destroy()
        except:
            pass
            
    threading.Thread(target=_animate, daemon=True).start()

def slide_up(widget, start_y_offset=20, duration=0.3):
    """Subtle slide up effect for widgets when they appear."""
    # This requires specific widget layout mgmt (place), harder with pack/grid.
    # Often used for floating toasts. For general layout, we leave it as a placeholder.
    pass
