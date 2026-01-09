import os
import sys
import time
import random
import subprocess
import tkinter as tk
from tkinter import StringVar, BooleanVar, IntVar
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
# States
pause_event = threading.Event()
browser_loaded = False
hunting_active = False
# Globals
counter = 0
# GUI
root = None
counter_var = None
event_entry = None
price_entry = None
section_entry = None
seats_spinbox = None
check_price_var = None
check_section_var = None
check_page2_var = None
check_test_mode_var = None
check_prefer_more_seats_var = None
check_silent_near_miss_var = None
control_button = None
test_button = None
check_price_check = None
check_section_check = None
check_page2_check = None
check_test_mode_check = None
check_prefer_more_seats_check = None
check_silent_near_miss_check = None
driver = None
def update_counter():
    global counter
    counter += 1
    if counter_var:
        counter_var.set(f"Checks: {counter}")
def get_current_targets():
    try:
        p = price_entry.get().strip().replace("¥", "").replace(",", "")
        min_price = int(p) if p.isdigit() else 18000
    except:
        min_price = 18000
    try:
        s = section_entry.get().strip().upper()
        target_section = s
    except:
        target_section = ""
    try:
        min_seats = int(seats_spinbox.get())
    except:
        min_seats = 2
    return min_price, target_section, min_seats
def toggle_price_state(*args):
    if not hunting_active or pause_event.is_set():
        state = "normal" if check_price_var.get() else "disabled"
        price_entry.config(state=state)
def toggle_section_state(*args):
    if not hunting_active or pause_event.is_set():
        state = "normal" if check_section_var.get() else "disabled"
        section_entry.config(state=state)
def play_alert_sound(full_alert=False):
    if full_alert:
        count = 60
        freq = 2500
        duration = 80
    else:
        count = 3
        freq = 2500
        duration = 200
    for _ in range(count):
        winsound.Beep(freq, duration)
        if not full_alert:
            time.sleep(0.2)
def beep_once():
    winsound.Beep(2000, 300)
def play_sad_sound():
    # Play a short sad sound, e.g., descending tones
    winsound.Beep(800, 500)
    winsound.Beep(600, 500)
    winsound.Beep(400, 500)
def play_test_sound():
    print("Testing sounds: beep, then sad sound...")
    beep_once()
    time.sleep(1)
    play_sad_sound()
def control_button_click():
    global browser_loaded, hunting_active
    if not browser_loaded:
        load_browser()
    elif not hunting_active:
        start_hunting()
    else:
        if pause_event.is_set():
            pause_event.clear()
            update_button("Unpause Hunting", "#2ed573")
            enable_editing(True)
            disable_checkboxes_during_hunt()
            print("Hunting paused.")
        else:
            pause_event.set()
            update_button("Pause Hunting", "#ff4757")
            enable_editing(False)
            disable_checkboxes_during_hunt()
            print("Hunting resumed.")
def update_button(text, color):
    control_button.config(text=text, bg=color)
def enable_editing(editable):
    fg = "black" if editable else "grey"
    bg = "white" if editable else "#f0f0f0"
    price_entry.config(foreground=fg, background=bg)
    section_entry.config(foreground=fg, background=bg)
    event_entry.config(foreground=fg, background=bg)
    seats_spinbox.config(state="normal" if editable else "disabled", foreground=fg, background=bg)
def disable_checkboxes_during_hunt():
    state = "disabled" if hunting_active and pause_event.is_set() else "normal"
    check_price_check.config(state=state)
    check_section_check.config(state=state)
    check_page2_check.config(state=state)
    check_test_mode_check.config(state=state)
    check_prefer_more_seats_check.config(state=state)
    check_silent_near_miss_check.config(state=state)
def load_browser():
    global browser_loaded, driver
    update_button("Loading Browser...", "#9b59b6")
    control_button.config(state="disabled")
    root.update_idletasks()
    print("Launching Chrome...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.get("https://store.anypass.jp/resale-list")
    print("Browser loaded - AnyPass resale list opened.")
    print("Log in and set your filters properly, then click 'Start Hunting'.")
    browser_loaded = True
    update_button("Start Hunting", "#9b59b6")
    control_button.config(state="normal")
def start_hunting():
    global hunting_active
    hunting_active = True
    pause_event.set()
    update_button("Pause Hunting", "#ff4757")
    enable_editing(False)
    disable_checkboxes_during_hunt()
    print("HUNTING STARTED! Freeword rotation only.")
def random_scroll():
    scroll_amount = random.randint(100, 600)
    direction = random.choice(["up", "down"])
    if direction == "up":
        driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
    else:
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    time.sleep(random.uniform(0.3, 0.8))
def rotate_free_word_and_search():
    try:
        if driver.current_url.startswith("data:"):
            print("White page detected - reloading...")
            driver.get("https://store.anypass.jp/resale-list")
            time.sleep(3)
            return False
        free_word_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "free_word"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", free_word_input)
        time.sleep(0.5)
        current_value = free_word_input.get_attribute("value") or ""
        base_word = event_entry.get().strip() or "BLACKPINK"
        if current_value == base_word:
            new_value = base_word[:-1] if len(base_word) > 3 else base_word
        elif len(current_value) > 3:
            new_value = current_value[:-1]
        else:
            new_value = base_word
        free_word_input.clear()
        time.sleep(0.2)
        free_word_input.send_keys(new_value)
        print(f"Free word rotated to: '{new_value}'")
        search_btn = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='button__container__inverted']//button | //button[contains(text(), '検索')]"))
        )
        search_btn.click()
        time.sleep(2)
        print("Search triggered via free word rotation.")
        return True
    except Exception as e:
        print(f"Free word rotation failed: {e}")
        return False
def check_page_2_if_available():
    if not check_page2_var.get():
        return False
    try:
        page2_link = driver.find_element(By.XPATH,
                                         "//ul[contains(@class, 'pagination')]//a[contains(@class, 'page-link') and (text()='2' or text()='＞' or contains(@href, 'page=2'))]")
        page2_link.click()
        time.sleep(2)
        print("Page 2 exists - checked.")
        if ticket_search():
            return True
        driver.back()
        time.sleep(1)
        print("Returned to Page 1.")
        return False
    except NoSuchElementException:
        print("Page 2 not available - skipping.")
        return False
def extract_price_and_seats(text):
    import re
    price_match = re.search(r'¥\s*([\d,]+)', text)
    price = int(price_match.group(1).replace(",", "")) if price_match else 0
    seats_match = re.search(r'×\s*(\d+)|(\d+)\s*枚', text)
    seats = int(seats_match.group(1) or seats_match.group(2)) if seats_match else 1
    return price, seats
def ticket_search():
    min_price, target_section, min_seats = get_current_targets()
    prefer_more_seats = check_prefer_more_seats_var.get()
    silent_near_miss = check_silent_near_miss_var.get()
    try:
        if driver.current_url.startswith("data:"):
            print("White page detected during search - reloading...")
            driver.get("https://store.anypass.jp/resale-list")
            time.sleep(3)
            return False
        all_items = driver.find_elements(By.CSS_SELECTOR, "a.item.resale-list-item")
        total_tickets = len(all_items)
        if check_test_mode_var.get():
            items = all_items
            print(f"TEST MODE: Checking all {total_tickets} tickets...")
        else:
            items = driver.find_elements(By.CSS_SELECTOR, "a.item.resale-list-item:not(:has(span.item__category.red))")
            available_count = len(items)
            reserved_count = total_tickets - available_count
            print(f"Found {total_tickets} tickets total, {reserved_count} reserved, {available_count} available.")
        candidates = []
        near_misses = []
        for item in items:
            try:
                text = item.text.upper()
                price_per, seats = extract_price_and_seats(item.text)
                if price_per < min_price:
                    if not check_test_mode_var.get():
                        near_misses.append((price_per, seats))
                    continue
                if seats < min_seats:
                    if not check_test_mode_var.get():
                        near_misses.append((price_per, seats))
                    continue
                if check_section_var.get() and target_section and target_section not in text:
                    if not check_test_mode_var.get():
                        near_misses.append((price_per, seats))
                    continue
                candidates.append((item, price_per, seats, text))
            except:
                continue
        if candidates:
            if prefer_more_seats:
                candidates.sort(key=lambda x: (-x[1], -x[2]))
            else:
                candidates.sort(key=lambda x: -x[1])
            best_item, best_price, best_seats, best_text = candidates[0]
            print(f"\n=== BEST MATCH FOUND ({best_price:,}¥ × {best_seats}) ===\n{best_text}\n")
            best_item.click()
            time.sleep(3)
            # Check for error message
            try:
                error_div = driver.find_element(By.XPATH, "//div[contains(text(), '他のお客様が購入手続き中です')]")
                print("Error: Another customer is purchasing this ticket.")
                play_sad_sound()
                driver.back()
                time.sleep(1)
                return False
            except NoSuchElementException:
                pass  # No error, proceed
            # Beep 3 times when ticket clicked
            beep_once()
            time.sleep(0.5)
            beep_once()
            time.sleep(0.5)
            beep_once()
            print("3 beeps - ticket clicked! Check now.")
            # Auto-select quantity (set hidden input)
            try:
                amount_select = driver.find_element(By.ID, "amount_select")
                driver.execute_script("arguments[0].value = arguments[1];", amount_select, str(min_seats))
                print(f"Set purchase quantity to {min_seats}.")
            except:
                print("Quantity select not found - default used.")
            # Auto-check all agreement checkboxes with real click
            try:
                terms_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "purchase_term_check"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", terms_box)
                time.sleep(1)
                labels = driver.find_elements(By.CSS_SELECTOR, ".terms_check label.container")
                for label in labels:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(label)).click()
                print("Auto-checked all agreement checkboxes by clicking labels.")
            except:
                print("Could not check checkboxes - check manually.")
            # Auto-click proceed with real click
            try:
                proceed_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "detail_submit"))
                )
                proceed_btn.click()
                print("Auto-clicked '購入手続きへ' - now on payment page.")
            except:
                print("Proceed button not clickable - check manually.")
            play_alert_sound(full_alert=True)
            pause_event.clear()
            update_button("Unpause Hunting", "#2ed573")
            enable_editing(True)
            disable_checkboxes_during_hunt()
            print("TICKET REACHED PAYMENT - COMPLETE PAYMENT NOW!")
            return True
        else:
            if near_misses and not check_test_mode_var.get():
                print(f"Found {len(near_misses)} unreserved tickets but none met requirements.")
                if not silent_near_miss:
                    beep_once()
            elif available_count == 0 and not check_test_mode_var.get():
                print("Found 0 available tickets.")
            return False
    except Exception as e:
        print(f"Search error: {e}")
        return False
def create_gui():
    global root, counter_var, event_entry, price_entry, section_entry, seats_spinbox
    global check_price_var, check_section_var, check_page2_var, check_test_mode_var, check_prefer_more_seats_var, check_silent_near_miss_var
    global check_price_check, check_section_check, check_page2_check, check_test_mode_check, check_prefer_more_seats_check, check_silent_near_miss_check
    global control_button, test_button
    root = tk.Tk()
    root.title("AnyPass Ticket Monitor")
    root.geometry("560x720")
    root.configure(bg="#2d2d2d")
    root.resizable(False, False)
    tk.Label(root, text="AnyPass Ticket Monitor", font=("Arial", 22, "bold"),
             fg="#ff69b4", bg="#2d2d2d").pack(pady=25)
    counter_var = StringVar(value="Checks: 0")
    tk.Label(root, textvariable=counter_var, font=("Arial", 16),
             fg="white", bg="#2d2d2d").pack(pady=10)
    frame_event = tk.Frame(root, bg="#2d2d2d")
    frame_event.pack(pady=12)
    tk.Label(frame_event, text="Event Name:", font=("Arial", 12), fg="white", bg="#2d2d2d").pack(side=tk.LEFT, padx=10)
    event_entry = tk.Entry(frame_event, width=40, font=("Arial", 12), justify="center")
    event_entry.insert(0, "BLACKPINK WORLD TOUR [BORN PINK]")
    event_entry.pack(side=tk.LEFT, padx=10)
    frame_price = tk.Frame(root, bg="#2d2d2d")
    frame_price.pack(pady=8)
    check_price_var = BooleanVar(value=True)
    check_price_var.trace("w", toggle_price_state)
    check_price_check = tk.Checkbutton(frame_price, text="Min Price per Ticket", variable=check_price_var,
                                       fg="white", bg="#2d2d2d", selectcolor="#2d2d2d")
    check_price_check.pack(side=tk.LEFT, padx=10)
    price_entry = tk.Entry(frame_price, width=20, font=("Arial", 12), justify="center")
    price_entry.insert(0, "¥28,000")
    price_entry.pack(side=tk.LEFT, padx=10)
    frame_section = tk.Frame(root, bg="#2d2d2d")
    frame_section.pack(pady=8)
    check_section_var = BooleanVar(value=False)
    check_section_var.trace("w", toggle_section_state)
    check_section_check = tk.Checkbutton(frame_section, text="Target Seat Contains", variable=check_section_var,
                                         fg="white", bg="#2d2d2d", selectcolor="#2d2d2d")
    check_section_check.pack(side=tk.LEFT, padx=10)
    section_entry = tk.Entry(frame_section, width=35, font=("Arial", 12), justify="center")
    section_entry.insert(0, "e.g. アリーナA, SS, VIP")
    section_entry.config(foreground="grey")
    section_entry.pack(side=tk.LEFT, padx=10)
    frame_seats = tk.Frame(root, bg="#2d2d2d")
    frame_seats.pack(pady=8)
    tk.Label(frame_seats, text="Minimum Seats:", font=("Arial", 11), fg="white", bg="#2d2d2d").pack(side=tk.LEFT, padx=10)
    seats_spinbox = tk.Spinbox(frame_seats, from_=1, to=10, width=5, font=("Arial", 12))
    seats_spinbox.delete(0, "end")
    seats_spinbox.insert(0, "2")
    seats_spinbox.pack(side=tk.LEFT, padx=10)
    frame_prefer = tk.Frame(root, bg="#2d2d2d")
    frame_prefer.pack(pady=4)
    check_prefer_more_seats_var = BooleanVar(value=True)
    check_prefer_more_seats_check = tk.Checkbutton(frame_prefer, text="Take higher seat count tickets if available",
                                                   variable=check_prefer_more_seats_var,
                                                   fg="#aaffaa", bg="#2d2d2d", selectcolor="#2d2d2d")
    check_prefer_more_seats_check.pack(side=tk.LEFT, padx=10)
    frame_page2 = tk.Frame(root, bg="#2d2d2d")
    frame_page2.pack(pady=8)
    check_page2_var = BooleanVar(value=True)
    check_page2_check = tk.Checkbutton(frame_page2, text="Check Page 2 before refresh (if available)", variable=check_page2_var,
                                       fg="white", bg="#2d2d2d", selectcolor="#2d2d2d")
    check_page2_check.pack(side=tk.LEFT, padx=10)
    frame_test = tk.Frame(root, bg="#2d2d2d")
    frame_test.pack(pady=8)
    check_test_mode_var = BooleanVar(value=False)
    check_test_mode_check = tk.Checkbutton(frame_test, text="Test Mode (clicks red/in-process tickets)", variable=check_test_mode_var,
                                           fg="#ff5555", bg="#2d2d2d", selectcolor="#2d2d2d", font=("Arial", 10, "bold"))
    check_test_mode_check.pack(side=tk.LEFT, padx=10)
    frame_silent = tk.Frame(root, bg="#2d2d2d")
    frame_silent.pack(pady=8)
    check_silent_near_miss_var = BooleanVar(value=True)
    check_silent_near_miss_check = tk.Checkbutton(frame_silent, text="Silent on tickets below requirements (no beep)",
                                                  variable=check_silent_near_miss_var,
                                                  fg="#8888ff", bg="#2d2d2d", selectcolor="#2d2d2d")
    check_silent_near_miss_check.pack(side=tk.LEFT, padx=10)
    tk.Label(root, text="Load Browser → Log in & filter → Start Hunting",
             font=("Arial", 10), fg="#aaaaaa", bg="#2d2d2d").pack(pady=20)
    control_button = tk.Button(root, text="Load Browser", width=22, height=3,
                               command=control_button_click, bg="#9b59b6", fg="white",
                               font=("Arial", 14, "bold"))
    control_button.pack(pady=10)
    test_button = tk.Button(root, text="Test Sound", command=play_test_sound,
                            bg="#e74c3c", fg="white", font=("Arial", 9))
    test_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
    toggle_price_state()
    toggle_section_state()
    root.mainloop()
def monitor_browser():
    global browser_loaded, hunting_active, driver
    while True:
        time.sleep(5)
        if driver is not None:
            try:
                _ = driver.title
            except WebDriverException:
                print("Browser closed detected.")
                driver = None
                browser_loaded = False
                if root is not None:
                    root.after(0, lambda: update_button("Load Browser", "#9b59b6"))
                    root.after(0, lambda: enable_editing(True))
                    root.after(0, disable_checkboxes_during_hunt)
                if hunting_active:
                    hunting_active = False
                    pause_event.clear()
gui_thread = threading.Thread(target=create_gui, daemon=True)
gui_thread.start()
monitor_thread = threading.Thread(target=monitor_browser, daemon=True)
monitor_thread.start()
# Winsound
try:
    import winsound
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
    import winsound
def generate_random_number():
    return round(random.uniform(1.5, 2.5), 4)
# Main loop
while True:
    pause_event.wait()
    try:
        random_scroll()
        if ticket_search():
            continue
        if check_page_2_if_available():
            continue
        if rotate_free_word_and_search():
            if ticket_search():
                continue
        if ticket_search():
            continue
        time.sleep(generate_random_number())
        update_counter()
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
    time.sleep(1)
