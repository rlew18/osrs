#!/usr/bin/env python3
"""
Smart AutoClicker - With Recording & Playback
Record mouse movements and clicks, then replay with variance
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyautogui
import time
import random
import threading
import json
from datetime import datetime
from pynput import keyboard
from pynput.mouse import Button, Controller, Listener as MouseListener

class RecordableAutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart AutoClicker - Recorder")
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        
        # State variables
        self.is_clicking = False
        self.is_recording = False
        self.is_playing = False
        self.click_count = 0
        self.mouse = Controller()
        self.click_thread = None
        self.record_thread = None
        self.hotkey_listener = None
        self.mouse_listener = None
        
        # Recording data
        self.recorded_actions = []
        self.recording_start_time = None
        self.last_position = None
        
        # Settings
        self.base_interval = tk.DoubleVar(value=1.0)
        self.interval_variance = tk.DoubleVar(value=0.2)
        self.position_variance = tk.IntVar(value=5)
        self.click_type = tk.StringVar(value="left")
        self.hotkey = tk.StringVar(value="F6")
        self.playback_speed = tk.DoubleVar(value=1.0)
        self.apply_variance = tk.BooleanVar(value=True)
        self.loop_playback = tk.BooleanVar(value=False)
        
        self.setup_ui()
        self.setup_hotkey()
        
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Simple Autoclicker
        self.simple_tab = ttk.Frame(notebook)
        notebook.add(self.simple_tab, text="Simple Clicker")
        self.setup_simple_tab()
        
        # Tab 2: Recorder
        self.recorder_tab = ttk.Frame(notebook)
        notebook.add(self.recorder_tab, text="Record & Replay")
        self.setup_recorder_tab()
        
    def setup_simple_tab(self):
        """Setup the simple autoclicker tab"""
        main_frame = ttk.Frame(self.simple_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Simple AutoClicker", 
                         font=("Arial", 14, "bold"))
        title.pack(pady=(0, 10))
        
        # Click Interval Settings
        interval_frame = ttk.LabelFrame(main_frame, text="Click Timing", padding="10")
        interval_frame.pack(fill='x', pady=5)
        
        row1 = ttk.Frame(interval_frame)
        row1.pack(fill='x', pady=2)
        ttk.Label(row1, text="Base Interval (seconds):").pack(side='left')
        ttk.Spinbox(row1, from_=0.01, to=10.0, increment=0.1, 
                   textvariable=self.base_interval, width=10).pack(side='right')
        
        row2 = ttk.Frame(interval_frame)
        row2.pack(fill='x', pady=2)
        ttk.Label(row2, text="Variance (±seconds):").pack(side='left')
        ttk.Spinbox(row2, from_=0.0, to=2.0, increment=0.05, 
                   textvariable=self.interval_variance, width=10).pack(side='right')
        
        # Position Settings
        position_frame = ttk.LabelFrame(main_frame, text="Position Variation", padding="10")
        position_frame.pack(fill='x', pady=5)
        
        row3 = ttk.Frame(position_frame)
        row3.pack(fill='x', pady=2)
        ttk.Label(row3, text="Position Variance (pixels):").pack(side='left')
        ttk.Spinbox(row3, from_=0, to=50, increment=1, 
                   textvariable=self.position_variance, width=10).pack(side='right')
        
        # Click Type
        click_frame = ttk.LabelFrame(main_frame, text="Click Settings", padding="10")
        click_frame.pack(fill='x', pady=5)
        
        row4 = ttk.Frame(click_frame)
        row4.pack(fill='x', pady=2)
        ttk.Label(row4, text="Click Type:").pack(side='left')
        ttk.Combobox(row4, textvariable=self.click_type,
                    values=["left", "right", "middle"], 
                    state="readonly", width=15).pack(side='right')
        
        # Hotkey
        hotkey_frame = ttk.LabelFrame(main_frame, text="Hotkey Control", padding="10")
        hotkey_frame.pack(fill='x', pady=5)
        
        row5 = ttk.Frame(hotkey_frame)
        row5.pack(fill='x', pady=2)
        ttk.Label(row5, text="Start/Stop Hotkey:").pack(side='left')
        hotkey_combo = ttk.Combobox(row5, textvariable=self.hotkey,
                                   values=["F6", "F7", "F8", "F9"], 
                                   state="readonly", width=15)
        hotkey_combo.pack(side='right')
        hotkey_combo.bind("<<ComboboxSelected>>", lambda e: self.setup_hotkey())
        
        # Status
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill='x', pady=5)
        
        self.simple_status_label = ttk.Label(status_frame, text="Idle", 
                                            font=("Arial", 10, "bold"),
                                            foreground="gray")
        self.simple_status_label.pack(pady=5)
        
        self.simple_count_label = ttk.Label(status_frame, text="Clicks: 0")
        self.simple_count_label.pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.simple_start_button = ttk.Button(button_frame, text="Start", 
                                             command=self.toggle_simple_clicking, 
                                             width=15)
        self.simple_start_button.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Reset Count", 
                  command=self.reset_simple_count, width=15).pack(side='left', padx=5)
        
    def setup_recorder_tab(self):
        """Setup the recorder tab"""
        main_frame = ttk.Frame(self.recorder_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Record & Replay", 
                         font=("Arial", 14, "bold"))
        title.pack(pady=(0, 10))
        
        # Recording Controls
        record_frame = ttk.LabelFrame(main_frame, text="Recording", padding="10")
        record_frame.pack(fill='x', pady=5)
        
        self.record_status = ttk.Label(record_frame, text="Not Recording", 
                                      font=("Arial", 10, "bold"),
                                      foreground="gray")
        self.record_status.pack(pady=5)
        
        self.record_info = ttk.Label(record_frame, text="Actions recorded: 0")
        self.record_info.pack(pady=2)
        
        rec_button_frame = ttk.Frame(record_frame)
        rec_button_frame.pack(pady=5)
        
        self.record_button = ttk.Button(rec_button_frame, text="Start Recording", 
                                       command=self.toggle_recording, width=15)
        self.record_button.pack(side='left', padx=5)
        
        ttk.Button(rec_button_frame, text="Clear Recording", 
                  command=self.clear_recording, width=15).pack(side='left', padx=5)
        
        # Playback Settings
        playback_frame = ttk.LabelFrame(main_frame, text="Playback Settings", 
                                       padding="10")
        playback_frame.pack(fill='x', pady=5)
        
        row1 = ttk.Frame(playback_frame)
        row1.pack(fill='x', pady=2)
        ttk.Label(row1, text="Playback Speed:").pack(side='left')
        ttk.Spinbox(row1, from_=0.1, to=5.0, increment=0.1, 
                   textvariable=self.playback_speed, width=10).pack(side='right')
        
        ttk.Checkbutton(playback_frame, text="Apply variance during playback",
                       variable=self.apply_variance).pack(anchor='w', pady=2)
        
        ttk.Checkbutton(playback_frame, text="Loop playback continuously",
                       variable=self.loop_playback).pack(anchor='w', pady=2)
        
        # Playback Controls
        play_frame = ttk.LabelFrame(main_frame, text="Playback", padding="10")
        play_frame.pack(fill='x', pady=5)
        
        self.play_status = ttk.Label(play_frame, text="Idle", 
                                    font=("Arial", 10, "bold"),
                                    foreground="gray")
        self.play_status.pack(pady=5)
        
        self.play_info = ttk.Label(play_frame, text="")
        self.play_info.pack(pady=2)
        
        play_button_frame = ttk.Frame(play_frame)
        play_button_frame.pack(pady=5)
        
        self.play_button = ttk.Button(play_button_frame, text="Play Recording", 
                                     command=self.toggle_playback, width=15)
        self.play_button.pack(side='left', padx=5)
        
        ttk.Button(play_button_frame, text="Stop Playback", 
                  command=self.stop_playback, width=15).pack(side='left', padx=5)
        
        # File Operations
        file_frame = ttk.LabelFrame(main_frame, text="Save/Load", padding="10")
        file_frame.pack(fill='x', pady=5)
        
        file_button_frame = ttk.Frame(file_frame)
        file_button_frame.pack(pady=5)
        
        ttk.Button(file_button_frame, text="Save Recording", 
                  command=self.save_recording, width=15).pack(side='left', padx=5)
        
        ttk.Button(file_button_frame, text="Load Recording", 
                  command=self.load_recording, width=15).pack(side='left', padx=5)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="Record: Move mouse and click\nPlayback: Replays with optional variance",
                                font=("Arial", 8), foreground="blue",
                                justify='center')
        instructions.pack(pady=10)
        
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
                self.toggle_simple_clicking()
        
        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.start()
    
    # Simple Clicker Methods
    def toggle_simple_clicking(self):
        if self.is_clicking:
            self.stop_simple_clicking()
        else:
            self.start_simple_clicking()
    
    def start_simple_clicking(self):
        self.is_clicking = True
        self.simple_status_label.config(text="Active - Clicking!", foreground="green")
        self.simple_start_button.config(text="Stop")
        
        self.base_x, self.base_y = self.mouse.position
        
        self.click_thread = threading.Thread(target=self.simple_click_loop, daemon=True)
        self.click_thread.start()
    
    def stop_simple_clicking(self):
        self.is_clicking = False
        self.simple_status_label.config(text="Stopped", foreground="orange")
        self.simple_start_button.config(text="Start")
    
    def reset_simple_count(self):
        self.click_count = 0
        self.simple_count_label.config(text="Clicks: 0")
    
    def simple_click_loop(self):
        button_map = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle
        }
        
        while self.is_clicking:
            try:
                variance = self.position_variance.get()
                offset_x = random.randint(-variance, variance)
                offset_y = random.randint(-variance, variance)
                
                click_x = self.base_x + offset_x
                click_y = self.base_y + offset_y
                
                self.mouse.position = (click_x, click_y)
                button = button_map.get(self.click_type.get(), Button.left)
                self.mouse.click(button, 1)
                
                self.click_count += 1
                self.root.after(0, self.update_simple_count_display)
                
                base = self.base_interval.get()
                variance = self.interval_variance.get()
                delay = base + random.uniform(-variance, variance)
                delay = max(0.01, delay)
                
                time.sleep(delay)
                
            except Exception as e:
                print(f"Error in click loop: {e}")
                self.stop_simple_clicking()
                break
    
    def update_simple_count_display(self):
        self.simple_count_label.config(text=f"Clicks: {self.click_count}")
    
    # Recording Methods
    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        self.is_recording = True
        self.recorded_actions = []
        self.recording_start_time = time.time()
        self.last_position = self.mouse.position
        
        self.record_status.config(text="Recording...", foreground="red")
        self.record_button.config(text="Stop Recording")
        
        # Start mouse listener
        self.mouse_listener = MouseListener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click
        )
        self.mouse_listener.start()
        
    def stop_recording(self):
        self.is_recording = False
        self.record_status.config(text="Recording Stopped", foreground="orange")
        self.record_button.config(text="Start Recording")
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        self.update_record_info()
    
    def on_mouse_move(self, x, y):
        if self.is_recording:
            current_time = time.time() - self.recording_start_time
            
            # Only record if position changed significantly (reduce noise)
            if self.last_position is None or \
               abs(x - self.last_position[0]) > 2 or \
               abs(y - self.last_position[1]) > 2:
                
                self.recorded_actions.append({
                    'type': 'move',
                    'x': x,
                    'y': y,
                    'time': current_time
                })
                self.last_position = (x, y)
                self.root.after(0, self.update_record_info)
    
    def on_mouse_click(self, x, y, button, pressed):
        if self.is_recording and pressed:  # Only record press, not release
            current_time = time.time() - self.recording_start_time
            
            button_name = "left" if button == Button.left else \
                         "right" if button == Button.right else "middle"
            
            self.recorded_actions.append({
                'type': 'click',
                'x': x,
                'y': y,
                'button': button_name,
                'time': current_time
            })
            self.root.after(0, self.update_record_info)
    
    def update_record_info(self):
        moves = len([a for a in self.recorded_actions if a['type'] == 'move'])
        clicks = len([a for a in self.recorded_actions if a['type'] == 'click'])
        self.record_info.config(text=f"Moves: {moves}, Clicks: {clicks}")
    
    def clear_recording(self):
        self.recorded_actions = []
        self.update_record_info()
        self.record_status.config(text="Recording Cleared", foreground="gray")
    
    # Playback Methods
    def toggle_playback(self):
        if not self.recorded_actions:
            messagebox.showwarning("No Recording", "Please record some actions first!")
            return
        
        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        self.is_playing = True
        self.play_status.config(text="Playing...", foreground="green")
        self.play_button.config(text="Pause Playback")
        
        self.click_thread = threading.Thread(target=self.playback_loop, daemon=True)
        self.click_thread.start()
    
    def stop_playback(self):
        self.is_playing = False
        self.play_status.config(text="Stopped", foreground="orange")
        self.play_button.config(text="Play Recording")
    
    def playback_loop(self):
        button_map = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle
        }
        
        while self.is_playing:
            try:
                last_time = 0
                
                for i, action in enumerate(self.recorded_actions):
                    if not self.is_playing:
                        break
                    
                    # Update progress
                    progress = f"Action {i+1}/{len(self.recorded_actions)}"
                    self.root.after(0, lambda p=progress: self.play_info.config(text=p))
                    
                    # Calculate delay
                    time_diff = action['time'] - last_time
                    last_time = action['time']
                    
                    # Apply speed multiplier
                    delay = time_diff / self.playback_speed.get()
                    
                    # Apply variance if enabled
                    if self.apply_variance.get() and delay > 0:
                        variance = self.interval_variance.get()
                        delay = delay + random.uniform(-variance, variance)
                        delay = max(0.01, delay)
                    
                    if delay > 0:
                        time.sleep(delay)
                    
                    # Apply position variance if enabled
                    x, y = action['x'], action['y']
                    if self.apply_variance.get():
                        variance = self.position_variance.get()
                        x += random.randint(-variance, variance)
                        y += random.randint(-variance, variance)
                    
                    # Execute action
                    if action['type'] == 'move':
                        self.mouse.position = (x, y)
                    elif action['type'] == 'click':
                        self.mouse.position = (x, y)
                        button = button_map.get(action['button'], Button.left)
                        self.mouse.click(button, 1)
                
                # Loop if enabled
                if self.loop_playback.get() and self.is_playing:
                    continue
                else:
                    break
                    
            except Exception as e:
                print(f"Error in playback: {e}")
                break
        
        self.is_playing = False
        self.root.after(0, lambda: self.play_status.config(text="Completed", 
                                                          foreground="blue"))
        self.root.after(0, lambda: self.play_button.config(text="Play Recording"))
    
    # File Operations
    def save_recording(self):
        if not self.recorded_actions:
            messagebox.showwarning("No Recording", "Nothing to save!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump({
                        'actions': self.recorded_actions,
                        'settings': {
                            'position_variance': self.position_variance.get(),
                            'interval_variance': self.interval_variance.get()
                        }
                    }, f, indent=2)
                messagebox.showinfo("Success", f"Recording saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def load_recording(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    self.recorded_actions = data.get('actions', [])
                    
                    # Load settings if available
                    if 'settings' in data:
                        settings = data['settings']
                        self.position_variance.set(settings.get('position_variance', 5))
                        self.interval_variance.set(settings.get('interval_variance', 0.2))
                
                self.update_record_info()
                messagebox.showinfo("Success", f"Loaded {len(self.recorded_actions)} actions")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")
    
    def on_closing(self):
        self.is_clicking = False
        self.is_recording = False
        self.is_playing = False
        
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
            
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RecordableAutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
