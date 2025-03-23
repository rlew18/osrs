import pyautogui
import time
import random

''' 
Grand Exchange. Western banker, lower.
Camera: medium zoom, medium angle.
Start with full inventory and magic tab open.
'''

# Enable PyAutoGUI failsafe (moving mouse to top-left corner aborts the script)
pyautogui.FAILSAFE = True

# Set reduced jitter values for improved accuracy
INTERMEDIATE_JITTER = 2  # minimal jitter for the intermediate waypoint
FINAL_JITTER = 1         # very low jitter for the final target

def human_click(x, y, delay_range=(1.0, 1.5)):
    # Get the current mouse position
    start_x, start_y = pyautogui.position()
    
    # Compute final target coordinates with reduced jitter for more accuracy
    final_x = x + random.randint(-FINAL_JITTER, FINAL_JITTER)
    final_y = y + random.randint(-FINAL_JITTER, FINAL_JITTER)
    
    # Calculate an intermediate waypoint with minimal random offset to simulate natural movement
    mid_x = (start_x + final_x) / 2 + random.randint(-INTERMEDIATE_JITTER, INTERMEDIATE_JITTER)
    mid_y = (start_y + final_y) / 2 + random.randint(-INTERMEDIATE_JITTER, INTERMEDIATE_JITTER)
    
    # Move to the intermediate point then to the final point with random durations
    pyautogui.moveTo(mid_x, mid_y, duration=random.uniform(0.15, 0.3))
    pyautogui.moveTo(final_x, final_y, duration=random.uniform(0.15, 0.3))
    
    # Optional slight pause before clicking to mimic human hesitance
    time.sleep(random.uniform(0.1, 0.2))
    pyautogui.click()
    
    # Wait for a post-click delay
    time.sleep(random.uniform(*delay_range))

def random_break(chance=0.1):
    # With a given probability, take an extra short break to simulate human distraction
    if random.random() < chance:
        extra_wait = random.uniform(1.0, 1.8)
        print(f"Taking an extra break for {extra_wait:.2f} seconds")
        time.sleep(extra_wait)

def superheat_cycle():
    # Speed up superheating by using a slightly reduced delay after each click
    human_click(1451, 760, delay_range=(0.8, 1.2))
    random_break(chance=0.05)
    human_click(1531, 951, delay_range=(0.8, 1.2))
    random_break(chance=0.05)

def bank_cycle():
    # Banking actions use the default human_click delay to preserve realistic timing
    human_click(885, 527)
    random_break(chance=0.1)
    human_click(1531, 951)
    random_break(chance=0.1)
    human_click(444, 151)
    random_break(chance=0.1)
    human_click(939, 52)
    random_break(chance=0.1)

def main():
    # Set script to run for 4 hours (4 * 60 * 60 seconds)
    start_time = time.time()
    end_time = start_time + 4 * 60 * 60

    try:
        while time.time() < end_time:
            # Superheat 27 gold ores with a slight speed boost for superheating actions
            for i in range(27):
                print(f"Superheating ore {i+1} of 27")
                superheat_cycle()
            # After 27 superheats, perform the banking sequence
            print("Performing banking actions")
            bank_cycle()
    except (KeyboardInterrupt, pyautogui.FailSafeException):
        print("Script terminated due to a manual interrupt or failsafe trigger.")

if __name__ == '__main__':
    main()
