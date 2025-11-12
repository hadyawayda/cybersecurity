#!/usr/bin/env python3
"""ft_otp_gui — Graphical interface for ft_otp (BONUS feature).

A simple GUI for generating and viewing TOTP codes.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from ft_otp_pkg.crypto_utils import decrypt_key
from ft_otp_pkg.io_utils import read_bytes
from ft_otp_pkg.otp import totp

class OTPTimer:
    """Timer that tracks TOTP validity period."""
    def __init__(self, period: int = 30):
        self.period = period
    
    def get_remaining_seconds(self) -> int:
        """Get seconds remaining in current period."""
        return self.period - (int(time.time()) % self.period)
    
    def get_progress(self) -> float:
        """Get progress through current period (0.0 to 1.0)."""
        return (self.period - self.get_remaining_seconds()) / self.period

class FtOtpGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ft_otp — TOTP Generator")
        self.geometry("500x400")
        self.resizable(False, False)
        
        self.key_data = None
        self.timer = OTPTimer(period=30)
        self.update_thread = None
        self.running = False
        
        self._build_ui()
    
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#2c3e50", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="🔐 ft_otp TOTP Generator",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title.pack(pady=15)
        
        # Main content
        content = tk.Frame(self, padx=30, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Key file section
        key_frame = tk.LabelFrame(content, text="Key File", padx=10, pady=10)
        key_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.key_path_var = tk.StringVar(value="No key file loaded")
        key_label = tk.Label(
            key_frame,
            textvariable=self.key_path_var,
            fg="gray",
            font=("Arial", 9)
        )
        key_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        load_btn = tk.Button(
            key_frame,
            text="Load Key",
            command=self.load_key,
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            cursor="hand2"
        )
        load_btn.pack(side=tk.RIGHT, padx=5)
        
        # TOTP display
        totp_frame = tk.LabelFrame(content, text="Current TOTP Code", padx=10, pady=10)
        totp_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.totp_var = tk.StringVar(value="------")
        totp_label = tk.Label(
            totp_frame,
            textvariable=self.totp_var,
            font=("Courier New", 36, "bold"),
            fg="#27ae60"
        )
        totp_label.pack(pady=20)
        
        # Timer progress bar
        timer_frame = tk.Frame(totp_frame)
        timer_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            timer_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X)
        
        self.timer_label_var = tk.StringVar(value="--s remaining")
        timer_label = tk.Label(
            timer_frame,
            textvariable=self.timer_label_var,
            font=("Arial", 9),
            fg="gray"
        )
        timer_label.pack(pady=5)
        
        # Copy button
        copy_btn = tk.Button(
            content,
            text="📋 Copy to Clipboard",
            command=self.copy_to_clipboard,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 11),
            cursor="hand2",
            height=2
        )
        copy_btn.pack(fill=tk.X)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Load a key file to begin.")
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 8),
            fg="gray"
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_key(self):
        path = filedialog.askopenfilename(
            title="Select Encrypted Key File",
            filetypes=[("Key files", "*.key"), ("All files", "*.*")]
        )
        
        if not path:
            return
        
        # Prompt for passphrase
        dialog = tk.Toplevel(self)
        dialog.title("Enter Passphrase")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Enter passphrase to decrypt key:", font=("Arial", 10)).pack(pady=15)
        
        passphrase_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=passphrase_var, show="●", font=("Arial", 12), width=30)
        entry.pack(pady=10)
        entry.focus()
        
        result = {"passphrase": None}
        
        def on_ok():
            result["passphrase"] = passphrase_var.get()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        entry.bind("<Return>", lambda e: on_ok())
        entry.bind("<Escape>", lambda e: on_cancel())
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="OK", command=on_ok, width=10, bg="#27ae60", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        self.wait_window(dialog)
        
        if not result["passphrase"]:
            return
        
        # Try to decrypt
        try:
            blob = read_bytes(path)
            self.key_data = decrypt_key(blob, result["passphrase"])
            self.key_path_var.set(path)
            self.status_var.set(f"Loaded: {path}")
            self.start_totp_updates()
            messagebox.showinfo("Success", "Key loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load key:\n{e}")
            self.status_var.set("Error loading key file")
    
    def start_totp_updates(self):
        if self.running:
            return
        
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _update_loop(self):
        while self.running and self.key_data:
            try:
                # Generate TOTP
                code = totp(self.key_data, digits=6, period=30, algo="sha1")
                self.totp_var.set(code)
                
                # Update timer
                remaining = self.timer.get_remaining_seconds()
                progress = self.timer.get_progress() * 100
                
                self.timer_label_var.set(f"{remaining}s remaining")
                self.progress_var.set(progress)
                
                time.sleep(0.1)  # Update 10 times per second for smooth progress bar
            except Exception as e:
                self.status_var.set(f"Error: {e}")
                break
    
    def copy_to_clipboard(self):
        code = self.totp_var.get()
        if code == "------":
            messagebox.showwarning("No Code", "No TOTP code to copy. Load a key first.")
            return
        
        self.clipboard_clear()
        self.clipboard_append(code)
        self.status_var.set("Code copied to clipboard!")
        
        # Flash the label
        original_bg = self.totp_var
        self.after(100, lambda: self.status_var.set(f"Loaded: {self.key_path_var.get()}"))
    
    def on_close(self):
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1)
        self.destroy()

def main():
    app = FtOtpGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()

if __name__ == "__main__":
    main()
