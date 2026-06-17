import pandas as pd
import time
import random
import json
from playwright.sync_api import sync_playwright
from datetime import datetime

# Read Excel file
data = pd.read_excel("contacts.xlsx", engine="openpyxl")

def random_delay():
    time.sleep(random.randint(2, 5))

def handle_popups(page):
    try:
        page.wait_for_timeout(3000)
        selectors = [
            "button[aria-label='Close']",
            "div[role='button'][aria-label='Close']",
            "span[data-icon='x']"
        ]
        for sel in selectors:
            
            if page.locator(sel).count() > 0:
                page.locator(sel).first.click()
                print("Popup closed")
                return
    except:
        pass

# ✅ Extract last 3 messages (incoming only)
def extract_last_messages(page):
    messages = []
    try:
        # All message bubbles
        msg_elements = page.locator("div.message-in span.selectable-text")

        count = msg_elements.count()

        # Get last 3 messages
        for i in range(max(0, count - 3), count):
            text = msg_elements.nth(i).inner_text()
            messages.append(text)

    except Exception as e:
        print("Error extracting messages:", e)

    return messages


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Open WhatsApp
    page.goto("https://web.whatsapp.com", timeout=0)

    print("Scan QR code and press ENTER...")
    input()

    handle_popups(page)

    results = []

    for index, row in data.iterrows():
        name = row['Name']
        phone = row['Phone']
        message = row['Message'].replace("{name}", name)

        try:
            print(f"Sending message to {name}")

            # Open chat
            page.goto(f"https://web.whatsapp.com/send?phone={phone}&text={message}", timeout=0)

            page.wait_for_selector("div[contenteditable='true']", timeout=30000)

            handle_popups(page)

            random_delay()

            # Send message
            page.keyboard.press("Enter")

            random_delay()

            # Screenshot
            page.screenshot(path=f"{name}.png")

            # ✅ Extract last 3 messages
            last_msgs = extract_last_messages(page)

            print(f"Extracted messages for {name}: {last_msgs}")

            results.append({
                "Name": name,
                "Phone": phone,
                "Status": "Sent",
                "LastMessages": last_msgs
            })

        except Exception as e:
            print(f"Error with {name}: {e}")

            results.append({
                "Name": name,
                "Phone": phone,
                "Status": "Failed",
                "LastMessages": []
            })

            continue

    today_date = datetime.now().strftime("%Y-%m-%d")    

    # ✅ Save Excel report
    report_df = pd.DataFrame(results)
    report_df.to_excel(f"report_{today_date}.xlsx", index=False)

    # ✅ Save JSON report
    with open(f"report_{today_date}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    browser.close()