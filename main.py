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


# Function to update the counter
def update_counter():
    global counter
    counter += 1
    counter_text.set(f"Checks: {counter}")


# GUI Setup
def create_gui():
    global root, counter_text
    root = tk.Tk()
    root.title("Ticket Check Counter")
    counter_text = StringVar()
    counter_text.set("Checks: 0")
    label = tk.Label(root, textvariable=counter_text)
    label.pack()
    root.mainloop()


# Start the GUI in a separate thread
gui_thread = threading.Thread(target=create_gui, daemon=True)
gui_thread.start()

# Install the required libraries if not already installed
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

# Path to ChromeDriver
CHROMEDRIVER_PATH = 'C:\\chromedriver-win64\\chromedriver.exe'

# Check if ChromeDriver is present at the specified path
if not os.path.isfile(CHROMEDRIVER_PATH):
    print("ChromeDriver not found at the specified path.")
    print("Please download ChromeDriver from https://sites.google.com/a/chromium.org/chromedriver/downloads")
    print("and place it at:", CHROMEDRIVER_PATH)
    sys.exit(1)

# Set the path in the environment variables
os.environ['PATH'] += os.pathsep + CHROMEDRIVER_PATH

# Initialize the WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)


def generate_random_number():
    return round(random.uniform(1.5, 2.5), 4)


def load_page_with_unique_query():
    timestamp = int(time.time())  # Current time in seconds since the Epoch
    unique_url = f"https://store.anypass.jp/resale-list?t={timestamp}&page=1"
    driver.get(unique_url)


counter = 0  # Initialize the counter


def ticket_search():
    global paused
    try:
        ticket_link_element = driver.find_element(By.CLASS_NAME, "resale-list-item")
        ticket_link = ticket_link_element.get_attribute('href')
        if ticket_link:
            paused = True
            print("Ticket found. Opening the ticket page.")
            full_link = f"{ticket_link}"
            print(full_link)
            driver.get(full_link)

            # Wait for the checkbox to be visible and clickable
            checkbox_xpath = "/html/body/main/div/div[2]/form/div[3]/div/div[3]/label/span"
            try:
                checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, checkbox_xpath))
                )
                checkbox.click()
            except Exception as e:
                print(f"Failed to click checkbox using normal method: {e}")
                # Fallback: Using JavaScript to click
                checkbox = driver.find_element(By.XPATH, checkbox_xpath)
                driver.execute_script("arguments[0].click();", checkbox)

            print("Checkbox clicked.")

            try:
                # Get the text from the element with XPath
                date_text = driver.find_element(By.XPATH,
                                                "/html/body/main/div/div[2]/form/div[1]/div/table/tbody/tr[2]/td[1]/p/span[1]").text
                #if "¥22,800" not in date_text:
                if "¥22,800" in date_text or "¥30,000" in date_text:
                    # print("Ticket IS SS or SS")
                    pass
                else:
                    print("Ticket price is not S or SS")
                    driver.back()  # Go back to the previous page
                    time.sleep(1)
                    paused = False
                    return False
            except NoSuchElementException:
                pass  # Handle the case when the element is not found or other exceptions

            try:
                # Get the text from the element with XPath
                date_text = driver.find_element(By.XPATH,
                                                "/html/body/main/div/div[1]/div/div/div/p[4]/span[1]").text
                if "2024/02/09" in date_text:
                    print("Ticket Has Wrong Date 2/9")
                    driver.back()  # Go back to the previous page
                    time.sleep(1)
                    paused = False
                    return False
            except NoSuchElementException:
                pass  # Handle the case when the element is not found or other exceptions

            # Check if the page contains specific text indicating the ticket is being used by another customer
            if "Another customer is in the process of purchasing" in driver.page_source:
                print("Ticket in use by other customer.")
                driver.back()  # Go back to the previous page
                time.sleep(1)
                paused = False
                return False

            # Detect Button that says "To purchase procedure"
            try:
                purchase_button = driver.find_element(By.XPATH, "//button[contains(., 'To purchase procedure')]")
                print("Purchase button found.")
                purchase_button.click()
            except NoSuchElementException:
                print("Purchase button not found.")
            except Exception as e:
                print(f"Failed to click the purchase button: {e}")

            # Pausing the script, playing a sound
            winsound.Beep(1000, 1000)
            time.sleep(.10)
            return True
    except NoSuchElementException:
        # print("No Ticket Found")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during ticket search: {e}")
        return False


# Open the webpage
driver.get("https://store.anypass.jp/resale-list")

# Wait for 60 seconds before starting the loop
time.sleep(20)

paused = False  # Flag to track if the script is paused

# Loop to continuously check for the search button and the specific text
while True:
    try:
        if not paused:
            # Click the search button
            search_button_xpath = "//button[contains(., 'Search')]"
            search_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, search_button_xpath))
            )
            search_button.click()

            time.sleep(.5)

            if ticket_search():
                continue

            time.sleep(.5)

            # Reload the page with a unique query parameter
            load_page_with_unique_query()
            time.sleep(1)

            if ticket_search():
                continue

            # Generate a random wait time
            random_number = generate_random_number()
            time.sleep(random_number)

            if ticket_search():
                continue

            update_counter()

        else:
            # Check if the 'S' key is pressed to resume
            if keyboard.is_pressed('S'):
                paused = False
                print("Resuming.")
                time.sleep(.01)

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(5)  # Wait for 5 seconds before retrying

    time.sleep(1)  # Check the conditions once per second
