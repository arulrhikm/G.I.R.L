"""
Simple Avatar Display using Tkinter
Shows an anime character image that indicates speaking state.
"""
import tkinter as tk
from pathlib import Path
import threading

# Avatar states
STATE_IDLE = "idle"
STATE_SPEAKING = "speaking"


class AvatarWindow:
    """Simple avatar display window"""
    
    def __init__(self, title="Riko", size=(300, 400)):
        self.root = None
        self.label = None
        self.size = size
        self.title = title
        self.running = False
        self.current_state = STATE_IDLE
        self.idle_image = None
        self.speaking_image = None
        self._thread = None
        
    def _create_window(self):
        """Create the tkinter window"""
        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.geometry(f"{self.size[0]}x{self.size[1]}")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(False, False)
        
        # Try to load images, or create placeholder
        self._load_images()
        
        # Create label for avatar
        self.label = tk.Label(
            self.root, 
            text="🎀 Riko 🎀\n\n[Avatar Image]\n\nListening...",
            font=("Segoe UI", 14),
            fg='#e94560',
            bg='#1a1a2e',
            justify='center'
        )
        self.label.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Status label at bottom
        self.status_label = tk.Label(
            self.root,
            text="● Online",
            font=("Segoe UI", 10),
            fg='#4ecca3',
            bg='#1a1a2e'
        )
        self.status_label.pack(pady=10)
        
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        
    def _load_images(self):
        """Load avatar images if available"""
        # Look for avatar images in character_files
        avatar_dir = Path(__file__).parent.parent.parent.parent / "character_files"
        
        # Check for idle/speaking images
        idle_path = avatar_dir / "avatar_idle.png"
        speaking_path = avatar_dir / "avatar_speaking.png"
        
        if idle_path.exists():
            try:
                self.idle_image = tk.PhotoImage(file=str(idle_path))
            except:
                pass
        
        if speaking_path.exists():
            try:
                self.speaking_image = tk.PhotoImage(file=str(speaking_path))
            except:
                pass
    
    def set_state(self, state: str, text: str = None):
        """Update avatar state (idle or speaking)"""
        if not self.root:
            return
            
        self.current_state = state
        
        def _update():
            if state == STATE_SPEAKING:
                self.label.config(
                    text=f"🎀 Riko 🎀\n\n💬 Speaking...\n\n{text[:50] + '...' if text and len(text) > 50 else text or ''}",
                    fg='#e94560'
                )
                self.status_label.config(text="● Speaking", fg='#e94560')
            else:
                self.label.config(
                    text="🎀 Riko 🎀\n\n[Avatar Image]\n\nListening...",
                    fg='#4ecca3'
                )
                self.status_label.config(text="● Online", fg='#4ecca3')
        
        if self.root:
            self.root.after(0, _update)
    
    def start(self):
        """Start the avatar window in a separate thread"""
        if self.running:
            return
            
        def _run():
            self._create_window()
            self.running = True
            self.root.mainloop()
            self.running = False
        
        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        
        # Give window time to initialize
        import time
        time.sleep(0.5)
    
    def close(self):
        """Close the avatar window"""
        self.running = False
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None
    
    def update(self):
        """Process pending events"""
        if self.root:
            try:
                self.root.update()
            except:
                pass


# Global avatar instance
_avatar = None

def get_avatar() -> AvatarWindow:
    """Get or create the global avatar instance"""
    global _avatar
    if _avatar is None:
        _avatar = AvatarWindow()
    return _avatar

def show_avatar():
    """Show the avatar window"""
    avatar = get_avatar()
    if not avatar.running:
        avatar.start()
    return avatar

def set_speaking(text: str = None):
    """Set avatar to speaking state"""
    avatar = get_avatar()
    avatar.set_state(STATE_SPEAKING, text)

def set_idle():
    """Set avatar to idle state"""
    avatar = get_avatar()
    avatar.set_state(STATE_IDLE)


if __name__ == "__main__":
    # Test the avatar
    import time
    
    print("Testing avatar display...")
    avatar = show_avatar()
    
    time.sleep(2)
    set_speaking("Hello senpai! This is a test message!")
    time.sleep(3)
    set_idle()
    time.sleep(2)
    
    print("Done!")
    avatar.close()
