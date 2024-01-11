import os
import sys
import time
import random
import subprocess
import tkinter as tk
from tkinter import StringVar
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Use a threading event to manage the paused state
pause_event = threading.Event()


def update_counter():
    global counter
    counter += 1
    counter_text.set(f"Checks: {counter}")


def pause_script():
    pause_event.clear()  # Clear the event to pause
    print("Script paused.")


def unpause_script():
    pause_event.set()  # Set the event to unpause
    print("Script unpaused.")


def create_gui():
    global root, counter_text
    root = tk.Tk()
    root.title("Ticket Check Counter")

    counter_text = StringVar()
    counter_text.set("Checks: 0")
    label = tk.Label(root, textvariable=counter_text)
    label.pack()

    pause_button = tk.Button(root, text="Pause", command=pause_script)
    pause_button.pack()

    unpause_button = tk.Button(root, text="Unpause", command=unpause_script)
    unpause_button.pack()

    root.mainloop()


gui_thread = threading.Thread(target=create_gui, daemon=True)
gui_thread.start()


try:
    import winsound
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
    import winsound

try:
    import keyboard
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "keyboard"])
    import keyboard

try:
    import pyautogui
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
    import pyautogui

CHROMEDRIVER_PATH = 'C:\\chromedriver-win64\\chromedriver.exe'

if not os.path.isfile(CHROMEDRIVER_PATH):
    print("ChromeDriver not found at the specified path.")
    print("Please download ChromeDriver from https://sites.google.com/a/chromium.org/chromedriver/downloads")
    print("and place it at:", CHROMEDRIVER_PATH)
    sys.exit(1)

os.environ['PATH'] += os.pathsep + CHROMEDRIVER_PATH

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)


def generate_random_number():
    return round(random.uniform(1.5, 2.5), 4)


def load_page_with_unique_query():
    timestamp = int(time.time())
    unique_url = f"https://store.anypass.jp/resale-list?t={timestamp}&page=1"
    driver.get(unique_url)


counter = 0


def ticket_search():

    try:
        ticket_items = driver.find_elements(By.CLASS_NAME, "resale-list-item")

        for item in ticket_items:
            try:
                price_text = item.find_element(By.XPATH, ".//p[contains(@class, 'ticket-info')]/span").text
                date_text = item.find_element(By.XPATH, ".//p[@class='date']/span").text
                seats_text = item.find_element(By.XPATH, ".//span[@class='ticket-info']/span").text
                link = item.get_attribute('href')

                try:
                    num_seats = int(seats_text)
                except ValueError:
                    print("Couldn't convert number of seats to an integer:", seats_text)
                    continue

                if ("¥30,000" in price_text) and "2024/02/09" not in date_text and num_seats >= 2:
                    print(f"Desired ticket found: {link}, Price: {price_text}, Number of Seats: {num_seats}")
                    driver.get(link)

                    checkbox_xpath = "/html/body/main/div/div[2]/form/div[3]/div/div[3]/label/span"
                    try:
                        checkbox = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, checkbox_xpath))
                        )
                        checkbox.click()
                    except Exception as e:
                        print(f"Failed to click checkbox using normal method: {e}")
                        checkbox = driver.find_element(By.XPATH, checkbox_xpath)
                        driver.execute_script("arguments[0].click();", checkbox)

                    if "Another customer is in the process of purchasing" in driver.page_source:
                        print("Ticket in use by other customer.")
                        driver.back()
                        time.sleep(1)
                        return False

                    try:
                        purchase_button = driver.find_element(By.XPATH, "//button[contains(., 'To purchase procedure')]")
                        print("Purchase button found.")
                        purchase_button.click()
                    except NoSuchElementException:
                        print("Purchase button not found.")
                    except Exception as e:
                        print(f"Failed to click the purchase button: {e}")
                    pause_event.clear()
                    winsound.Beep(1000, 1000)
                    time.sleep(.10)
                    return True

            except NoSuchElementException:
                continue

        return False

    except Exception as e:
        print(f"An unexpected error occurred during ticket search: {e}")
        return False


driver.get("https://store.anypass.jp/resale-list")
# Sleep time for Login/Setup
time.sleep(40)
# Initially set the event (unpaused)
pause_event.set()

while True:
    pause_event.wait()  # This will block when the script is paused

    try:
        search_button_xpath = "//button[contains(., 'Search')]"
        search_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, search_button_xpath))
        )
        search_button.click()

        time.sleep(.5)

        if ticket_search():
            continue

        time.sleep(.5)
        load_page_with_unique_query()
        time.sleep(1)

        if ticket_search():
            continue

        random_number = generate_random_number()
        time.sleep(random_number)

        if ticket_search():
            continue

        update_counter()

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(5)

    time.sleep(1)
