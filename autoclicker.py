#!/usr/bin/env python3
"""
Smart Autoclicker - Variable timing and positioning
"""

import tkinter as tk
from tkinter import ttk
import pyautogui
import time
import random
import threading
from pynput import keyboard
from pynput.mouse import Button, Controller

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart AutoClicker")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        # State variables
        self.is_clicking = False
        self.click_count = 0
        self.mouse = Controller()
        self.click_thread = None
        self.hotkey_listener = None
        
        # Settings
        self.base_interval = tk.DoubleVar(value=1.0)
        self.interval_variance = tk.DoubleVar(value=0.2)
        self.position_variance = tk.IntVar(value=5)
        self.click_type = tk.StringVar(value="left")
        self.hotkey = tk.StringVar(value="F6")
        
        self.setup_ui()
        self.setup_hotkey()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="Smart AutoClicker", 
                         font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Click Interval Settings
        interval_frame = ttk.LabelFrame(main_frame, text="Click Timing", 
                                       padding="10")
        interval_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                           pady=5)
        
        ttk.Label(interval_frame, text="Base Interval (seconds):").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        interval_spin = ttk.Spinbox(interval_frame, from_=0.01, to=10.0, 
                                   increment=0.1, textvariable=self.base_interval,
                                   width=10)
        interval_spin.grid(row=0, column=1, sticky=tk.E, pady=5)
        
        ttk.Label(interval_frame, text="Variance (±seconds):").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        variance_spin = ttk.Spinbox(interval_frame, from_=0.0, to=2.0, 
                                   increment=0.05, textvariable=self.interval_variance,
                                   width=10)
        variance_spin.grid(row=1, column=1, sticky=tk.E, pady=5)
        
        # Info label
        info_label = ttk.Label(interval_frame, 
                              text="Actual delay will vary randomly within the range",
                              font=("Arial", 8), foreground="gray")
        info_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        # Position Settings
        position_frame = ttk.LabelFrame(main_frame, text="Position Variation", 
                                       padding="10")
        position_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                           pady=5)
        
        ttk.Label(position_frame, text="Position Variance (pixels):").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        pos_spin = ttk.Spinbox(position_frame, from_=0, to=50, 
                              increment=1, textvariable=self.position_variance,
                              width=10)
        pos_spin.grid(row=0, column=1, sticky=tk.E, pady=5)
        
        pos_info = ttk.Label(position_frame, 
                            text="Clicks will vary within this radius from center",
                            font=("Arial", 8), foreground="gray")
        pos_info.grid(row=1, column=0, columnspan=2, pady=(5, 0))
        
        # Click Type
        click_frame = ttk.LabelFrame(main_frame, text="Click Settings", 
                                    padding="10")
        click_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                        pady=5)
        
        ttk.Label(click_frame, text="Click Type:").grid(row=0, column=0, 
                                                        sticky=tk.W, pady=5)
        click_combo = ttk.Combobox(click_frame, textvariable=self.click_type,
                                  values=["left", "right", "middle"], 
                                  state="readonly", width=15)
        click_combo.grid(row=0, column=1, sticky=tk.E, pady=5)
        
        # Hotkey Settings
        hotkey_frame = ttk.LabelFrame(main_frame, text="Hotkey Control", 
                                     padding="10")
        hotkey_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                         pady=5)
        
        ttk.Label(hotkey_frame, text="Start/Stop Hotkey:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        hotkey_combo = ttk.Combobox(hotkey_frame, textvariable=self.hotkey,
                                   values=["F6", "F7", "F8", "F9"], 
                                   state="readonly", width=15)
        hotkey_combo.grid(row=0, column=1, sticky=tk.E, pady=5)
        hotkey_combo.bind("<<ComboboxSelected>>", lambda e: self.setup_hotkey())
        
        # Status
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                         pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Idle", 
                                      font=("Arial", 10, "bold"),
                                      foreground="gray")
        self.status_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        self.count_label = ttk.Label(status_frame, text="Clicks: 0",
                                     font=("Arial", 9))
        self.count_label.grid(row=1, column=0, columnspan=2)
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start (or press hotkey)", 
                                      command=self.toggle_clicking, width=25)
        self.start_button.grid(row=0, column=0, padx=5)
        
        reset_button = ttk.Button(button_frame, text="Reset Count", 
                                 command=self.reset_count, width=15)
        reset_button.grid(row=0, column=1, padx=5)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text=f"Press {self.hotkey.get()} to start/stop clicking at cursor position",
                                font=("Arial", 8), foreground="blue")
        instructions.grid(row=7, column=0, columnspan=2, pady=(0, 5))
        
    def setup_hotkey(self):
        """Setup global hotkey listener"""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        hotkey_map = {
            "F6": keyboard.Key.f6,
            "F7": keyboard.Key.f7,
            "F8": keyboard.Key.f8,
            "F9": keyboard.Key.f9
        }
        
        selected_key = hotkey_map.get(self.hotkey.get(), keyboard.Key.f6)
        
        def on_press(key):
            if key == selected_key:
                self.toggle_clicking()
        
        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.start()
        
    def toggle_clicking(self):
        """Toggle clicking on/off"""
        if self.is_clicking:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def start_clicking(self):
        """Start the autoclicker"""
        self.is_clicking = True
        self.status_label.config(text="Active - Clicking!", foreground="green")
        self.start_button.config(text="Stop (or press hotkey)")
        
        # Get initial cursor position
        self.base_x, self.base_y = self.mouse.position
        
        # Start clicking thread
        self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
        self.click_thread.start()
    
    def stop_clicking(self):
        """Stop the autoclicker"""
        self.is_clicking = False
        self.status_label.config(text="Stopped", foreground="orange")
        self.start_button.config(text="Start (or press hotkey)")
    
    def reset_count(self):
        """Reset click counter"""
        self.click_count = 0
        self.count_label.config(text="Clicks: 0")
    
    def click_loop(self):
        """Main clicking loop with variance"""
        button_map = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle
        }
        
        while self.is_clicking:
            try:
                # Calculate varied position
                variance = self.position_variance.get()
                offset_x = random.randint(-variance, variance)
                offset_y = random.randint(-variance, variance)
                
                click_x = self.base_x + offset_x
                click_y = self.base_y + offset_y
                
                # Perform click
                self.mouse.position = (click_x, click_y)
                button = button_map.get(self.click_type.get(), Button.left)
                self.mouse.click(button, 1)
                
                # Update counter
                self.click_count += 1
                self.root.after(0, self.update_count_display)
                
                # Calculate varied delay
                base = self.base_interval.get()
                variance = self.interval_variance.get()
                delay = base + random.uniform(-variance, variance)
                delay = max(0.01, delay)  # Ensure positive delay
                
                time.sleep(delay)
                
            except Exception as e:
                print(f"Error in click loop: {e}")
                self.stop_clicking()
                break
    
    def update_count_display(self):
        """Update click count label"""
        self.count_label.config(text=f"Clicks: {self.click_count}")
    
    def on_closing(self):
        """Cleanup when closing"""
        self.is_clicking = False
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
