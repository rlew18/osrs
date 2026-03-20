# Smart AutoClicker

A sophisticated autoclicker with variable timing and positioning to make automated clicks appear more natural and human-like.

## Features

### Variable Timing
- **Base Interval**: Set the average time between clicks (0.01 to 10 seconds)
- **Variance**: Add randomization (±0 to 2 seconds) to make timing unpredictable
- Example: Base interval of 1.0s with 0.2s variance = clicks happen between 0.8s and 1.2s apart

### Position Variation
- **Pixel Variance**: Clicks vary within a radius around the initial cursor position
- Range: 0 to 50 pixels
- Example: 5 pixel variance means each click lands randomly within a 5-pixel radius

### Click Options
- Left, Right, or Middle mouse button
- Click counting with reset capability
- Real-time status display

### Hotkey Control
- Global hotkey (F6, F7, F8, or F9) to start/stop from anywhere
- Works even when the window is minimized or in the background

## Installation

### Prerequisites
- Python 3.7 or higher

### Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python autoclicker.py
   ```

### Platform-Specific Notes

**macOS:**
- You'll need to grant Accessibility permissions to your terminal/Python
- Go to: System Preferences → Security & Privacy → Accessibility
- Add Terminal.app or your Python interpreter

**Linux:**
- May need to install additional dependencies:
  ```bash
  sudo apt-get install python3-tk python3-dev
  ```

**Windows:**
- Should work out of the box after installing requirements

## Usage

1. **Configure Settings:**
   - Set your desired **Base Interval** (time between clicks)
   - Adjust **Variance** to add randomness to timing
   - Set **Position Variance** to add random offset to click locations
   - Choose your **Click Type** (left/right/middle button)
   - Select your preferred **Hotkey** (F6-F9)

2. **Start Clicking:**
   - Position your mouse cursor where you want clicking to occur
   - Press the hotkey (default: F6) or click "Start"
   - The app will click at that position with slight variations

3. **Stop Clicking:**
   - Press the hotkey again or click "Stop"

4. **Monitor Activity:**
   - Status indicator shows current state (Idle/Active/Stopped)
   - Click counter tracks total clicks
   - Use "Reset Count" to clear the counter

## Examples

### Slow, Precise Clicking
- Base Interval: 2.0 seconds
- Variance: 0.1 seconds
- Position Variance: 2 pixels
- **Result**: Clicks every 1.9-2.1 seconds within 2 pixels

### Fast, Natural Clicking
- Base Interval: 0.5 seconds
- Variance: 0.3 seconds
- Position Variance: 10 pixels
- **Result**: Clicks every 0.2-0.8 seconds within 10 pixels

### Consistent Clicking
- Base Interval: 1.0 seconds
- Variance: 0.0 seconds
- Position Variance: 0 pixels
- **Result**: Exact clicks every 1.0 second at same position

## Safety Features

- Minimum delay of 0.01 seconds enforced to prevent system overload
- Easy emergency stop via hotkey
- Thread-safe implementation
- Clean shutdown handling

## Common Use Cases

- Automating repetitive clicking tasks in applications
- Testing click-heavy interfaces
- Data entry automation
- Gaming (check game TOS - many prohibit automation)
- Accessibility assistance

## Troubleshooting

**Hotkey not working:**
- Make sure no other application is using the same hotkey
- Try a different hotkey from the dropdown

**Clicks not registering:**
- Check if the target application requires admin privileges
- Ensure Python has necessary permissions

**Application not starting:**
- Verify all dependencies are installed: `pip list`
- Check Python version: `python --version` (need 3.7+)

## License

Free to use for personal automation tasks. Not responsible for misuse or violations of software Terms of Service.

## Disclaimer

Use responsibly and in accordance with the terms of service of any applications you automate. Some applications prohibit automation tools - check before using.
