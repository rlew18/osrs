import time
import random
import pyautogui

pyautogui.FAILSAFE = True

print("Script will start in 15 seconds...")
time.sleep(15)

# ===== Coordinates =====
base_prayer = (1514, 732)
inventory_tab = (1432, 629)
prayer_tab = (1510, 631)

# Regular potion slots (6 rows x 4 columns)
potion_slots = [
    (1345, 734), (1401, 737), (1451, 737), (1501, 737),  # Row 1
    (1345, 783), (1405, 784), (1448, 783), (1502, 785),  # Row 2
    (1503, 830), (1452, 830), (1399, 829), (1350, 829),  # Row 3
    (1346, 870), (1398, 868), (1449, 872), (1504, 874),  # Row 4
    (1507, 913), (1451, 917), (1451, 917), (1399, 921),  # Row 5
    (1344, 920), (1349, 955), (1403, 965), (1400, 965)   # Row 6
]

# Overload potion slots (coordinates as provided)
overload_slots = [
    (1371, 689), (1425, 686), (1475, 685), (1532, 689),
    (1372, 733), (1425, 735), (1478, 728)
]

# Each potion slot (regular and overload) starts with 4 doses.
potion_inventory = {slot: 4 for slot in potion_slots}
overload_inventory = {slot: 4 for slot in overload_slots}

# Global variable to track prayer state (assumes prayer is off at start)
prayer_on = False

# ===== Helper Functions =====
def random_fidget():
    """Simulates a small, human-like fidget movement."""
    if random.random() < 0.3:
        current_x, current_y = pyautogui.position()
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-20, 20)
        move_duration = random.uniform(0.1, 0.3)
        pyautogui.moveTo(current_x + offset_x, current_y + offset_y, duration=move_duration)
        time.sleep(random.uniform(0.1, 0.4))

def human_click(target, jitter=2, pre_delay_range=(0.1, 0.3), move_duration_range=(0.2, 0.7), post_delay_range=(0.2, 0.8)):
    """
    Moves the mouse to a target coordinate with a bit of jitter,
    sometimes simulates a misclick, and uses human-like delays.
    """
    if random.random() < 0.1:
        time.sleep(random.uniform(0.2, 0.5))
    jittered_target = (target[0] + random.randint(-jitter, jitter),
                       target[1] + random.randint(-jitter, jitter))
    time.sleep(random.uniform(*pre_delay_range))
    move_duration = random.uniform(*move_duration_range)
    pyautogui.moveTo(jittered_target[0], jittered_target[1], duration=move_duration)
    
    # Simulate a misclick with low probability
    if random.random() < 0.05:
        misclick_offset = (random.randint(-10, 10), random.randint(-10, 10))
        misclick_target = (jittered_target[0] + misclick_offset[0], jittered_target[1] + misclick_offset[1])
        pyautogui.moveTo(misclick_target[0], misclick_target[1], duration=random.uniform(0.1, 0.3))
        pyautogui.click()
        time.sleep(random.uniform(0.1, 0.3))
        pyautogui.moveTo(jittered_target[0], jittered_target[1], duration=random.uniform(0.1, 0.3))
    
    time.sleep(random.uniform(0.05, 0.2))
    pyautogui.click()
    time.sleep(random.uniform(*post_delay_range))
    random_fidget()

def prayer_click(target):
    """
    A more precise click function for the prayer toggle.
    Uses minimal jitter and avoids misclick simulation.
    """
    jittered_target = (target[0] + random.randint(-1, 1),
                       target[1] + random.randint(-1, 1))
    time.sleep(random.uniform(0.05, 0.15))
    move_duration = random.uniform(0.1, 0.3)
    pyautogui.moveTo(jittered_target[0], jittered_target[1], duration=move_duration)
    time.sleep(random.uniform(0.05, 0.1))
    pyautogui.click()
    time.sleep(random.uniform(0.05, 0.15))

# ===== Prayer Toggling Routine =====
def prayer_toggle_cycle():
    """
    Toggles prayer on and off using precise clicks.
    Ensures that the cycle always ends with prayer off.
    """
    global prayer_on
    # First click toggles the prayer state.
    prayer_click(base_prayer)
    prayer_on = not prayer_on
    time.sleep(random.uniform(0.2, 0.6))
    
    # Second click toggles the prayer state again.
    prayer_click(base_prayer)
    prayer_on = not prayer_on
    
    # If prayer is still on (i.e. if it started on), force it off.
    if prayer_on:
        prayer_click(base_prayer)
        prayer_on = not prayer_on
        
    time.sleep(random.uniform(20, 45))

# ===== Potion Usage Routine =====
def potion_usage_routine():
    """
    Switches to the inventory tab, uses 6-9 doses from the regular potion slots sequentially,
    then switches back to the prayer tab.
    """
    global potion_inventory
    human_click(inventory_tab, jitter=2)
    
    doses_to_use = random.randint(6, 9)
    print(f"Using {doses_to_use} regular potion doses this routine.")
    
    available_slots_ordered = [slot for slot in potion_slots if slot in potion_inventory]
    if not available_slots_ordered:
         print("No more regular potions available!")
         return
    
    # Choose a random starting index within the ordered list
    start_index = random.randint(0, len(available_slots_ordered) - 1)
    doses_used = 0
    current_index = start_index
    
    while doses_used < doses_to_use:
         available_slots_ordered = [slot for slot in potion_slots if slot in potion_inventory]
         if not available_slots_ordered:
              print("No more regular potions available!")
              break
         if current_index >= len(available_slots_ordered):
             current_index = 0
         chosen_slot = available_slots_ordered[current_index]
         human_click(chosen_slot, jitter=2)
         time.sleep(random.uniform(0.2, 0.5))
         
         potion_inventory[chosen_slot] -= 1
         if potion_inventory[chosen_slot] <= 0:
             print(f"Regular potion at {chosen_slot} has been used up and removed from inventory.")
             del potion_inventory[chosen_slot]
         doses_used += 1
         current_index += 1
    
    time.sleep(random.uniform(0.3, 0.8))
    human_click(prayer_tab, jitter=2)
    time.sleep(random.uniform(0.3, 0.8))

# ===== Overload Usage Routine =====
def overload_usage_routine():
    """
    Opens the inventory tab, uses one dose from the first available overload potion,
    and then clicks back to the prayer tab.
    """
    global overload_inventory
    available_slots = [slot for slot in overload_slots if slot in overload_inventory]
    if not available_slots:
         print("No more overload potions available!")
         return
    
    # Open the inventory tab first.
    human_click(inventory_tab, jitter=2)
    time.sleep(random.uniform(0.2, 0.5))
    
    # Select the first available overload potion slot.
    chosen_slot = available_slots[0]
    print("Taking one overload potion dose.")
    human_click(chosen_slot, jitter=2)
    time.sleep(random.uniform(0.2, 0.5))
    
    overload_inventory[chosen_slot] -= 1
    if overload_inventory[chosen_slot] <= 0:
         print(f"Overload potion at {chosen_slot} has been used up and removed from inventory.")
         del overload_inventory[chosen_slot]
    
    # Return to the prayer tab.
    human_click(prayer_tab, jitter=2)
    time.sleep(random.uniform(0.3, 0.8))

# ===== Script Start =====
# Take the first overload dose immediately when the script starts.
overload_usage_routine()

# Also start with a regular potion usage routine.
potion_usage_routine()

# Initialize next overload usage time (every 300-310 seconds)
overload_next_time = time.time() + random.uniform(300, 310)

# ===== Main Loop =====
while potion_inventory:
    # Wait for a random interval (13 to 17 minutes) while toggling prayer repeatedly.
    interval = random.uniform(13 * 60, 17 * 60)
    start_interval = time.time()
    while time.time() - start_interval < interval:
        prayer_toggle_cycle()
        # Check if it's time to take an overload potion.
        if time.time() >= overload_next_time:
            overload_usage_routine()
            overload_next_time = time.time() + random.uniform(300, 310)
        if random.random() < 0.1:
            time.sleep(random.uniform(0.5, 2))
    
    potion_usage_routine()

print("No more regular potions left in inventory. Ending script.")
