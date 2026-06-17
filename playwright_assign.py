import pandas as pd
import time
import random
from playwright.sync_api import sync_playwright

# Read Excel file
data = pd.read_excel("contacts.xlsx", engine="openpyxl")

def random_delay():
    time.sleep(random.randint(2, 5))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Open WhatsApp Web
    page.goto("https://web.whatsapp.com")
    page.wait_for_load_state("networkidle")

    print("Scan QR code and press ENTER...")
    input()

    for index, row in data.iterrows():
        name = row['Name']
        phone = row['Phone']
        message = row['Message']

        # Replace {name}
        message = message.replace("{name}", name)

        try:
            print(f"Sending message to {name}")

            # Open chat using phone number
            page.goto(f"https://web.whatsapp.com/send?phone={phone}&text={message}")
            page.wait_for_load_state("networkidle")

            # Wait for chat box
            page.wait_for_selector("div[contenteditable='true']", timeout=20000)

            random_delay()

            # Press Enter to send message
            page.keyboard.press("Enter")

            random_delay()

            # Take screenshot
            page.screenshot(path=f"{name}.png")

            print(f"Message sent to {name}")

        except Exception as e:
            print(f"Error with {name}: {e}")

            continue

    browser.close()
