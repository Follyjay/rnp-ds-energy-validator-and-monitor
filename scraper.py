# ------------------------------------------------------------------------------
# RNP Data Scraper and Validator
# ------------------------------------------------------------------------------
# This script:
# - Launches the RNP website once in a persistent Firefox session
# - Scrapes nomination data every hour at 45 minutes past the hour
# - Saves the data to a timestamped CSV file
# - Runs validation against DS XML data and triggers alerts on mismatch
# ------------------------------------------------------------------------------

# --------------------------
# Import necessary libraries
# --------------------------
import time
import datetime
import os
import logging
import pandas as pd
import pytz
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import CSV_DIR, LOG_FILE
from validate import validate_hourly_flow

#def scrap_rnp_data():
# -----------------------------
# Setup directories and logging
# -----------------------------
rnp_dir = os.path.abspath(CSV_DIR)
os.makedirs(rnp_dir, exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# ---------------------------------------
# Initialize a persistent Firefox browser
# ---------------------------------------
options = FirefoxOptions()
options.set_preference("detach", True)  # Keeps browser open after script runs
service = FirefoxService(executable_path=FirefoxService().path)
driver = webdriver.Firefox(service=service, options=options)

# Load RNP website
driver.get("https://rnp.unicorn.com/NOM04")
wait_60 = WebDriverWait(driver, 60)
wait_10 = WebDriverWait(driver, 10)

print("📡 Browser launched and URL loaded.")

# ---------------------------------------
# Main hourly scrape and validate routine
# ---------------------------------------
prev_hour = None
prev_execution_key = None

try:
    while True:
        # Get current time in UTC and convert to local time zone
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=pytz.utc)
        local_tz = pytz.timezone("Europe/London") # Define local time zone
        local_time = now.astimezone(local_tz)  # Convert to local time zone

        current_hour = local_time.hour # Extracts the current Hour of the day
        current_minute = local_time.minute # Extracts the current Minute of the hour
        current_offset = local_time.utcoffset() # Extracts the current UTC offset
        current_execution_key = (current_hour, current_offset)

        # Check if it's 45 minutes past the hour
        #if current_execution_key != prev_execution_key and now.minute % 44 == 0:
        if now.minute % 5 == 0:

            # Refresh the page before scraping
            driver.refresh()
            time.sleep(10)  # Wait for page reload

            # Check If we are in the 21st hour of the day, set the business day to the next day
            if now.hour >= 21:
                business_day_input = wait_60.until(EC.element_to_be_clickable((By.NAME, "tradingDay")))
                next  = now + datetime.timedelta(days=1)
                nextDay = next.day

                if nextDay != now.day:
                    business_day_input.click()
                    try:
                        date_cell = driver.find_element(By.XPATH,f"//table/tbody//td[.//div/div[text()='{nextDay}']]")
                    except:
                        date_cell = driver.find_element(By.XPATH,f"//table/tbody//td[.//div/div/span[text()='{nextDay}']]")
                    
                    date_cell.click()
                    logging.info(f"Set business day to next day: {next.strftime('%d-%m-%Y')}")
                    print(f"🛑 RNP for next day {next.strftime('%d-%m-%Y')} Loaded.")

            print(f"\n⏰ Running RNP scrape at {now.strftime('%H:%M:%S')}")
            logging.info(f"Triggering scrape at {now.strftime('%H:%M')}")

            try:
                # Code to check if the rnp website has been set to the next day to match the ds_file vlaue
                # and the input the parameter for the next day

                # Wait for the Show Data button to be clickable and click it
                show_data_button = wait_60.until(EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div/div/div[5]/div[1]/div/div/div/div[1]/div[2]/div[1]/div/div[4]/button")
                ))
                driver.execute_script("arguments[0].click();", show_data_button)
                time.sleep(5)  # Wait for table to load

                # Find the first table body containing data
                table_body = driver.find_elements(By.TAG_NAME, "tbody")
                if not table_body:
                    logging.warning("Table not found.")
                    continue

                # Extract data rows
                rows = table_body[1].find_elements(By.TAG_NAME, "tr")
                data = []
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    data.append([cell.text for cell in cells])

                # Handle empty result
                if not data:
                    logging.warning("No data extracted.")
                    continue

                # Save to CSV
                df = pd.DataFrame(data)
                timestamp = now.strftime("%Y%m%d_%H%M%S")
                filename = f"rnp_at_{timestamp}.csv"
                filepath = os.path.join(rnp_dir, filename)
                df.to_csv(filepath, index=False, header=False)

                print(f"✅ Data saved to {filename}")
                logging.info(f"✅ Data saved to {filename}")

                # Trigger data validation routine
                validate_hourly_flow()

            except Exception as scrape_error:
                logging.error(f"Scraping error: {scrape_error}")
                print(f"🚨 Scraping failed: {scrape_error}")

            # Mark this hour as completed
            prev_hour = current_hour
            prev_execution_key = current_execution_key

            # Pause to avoid duplicate runs in the same minute
            time.sleep(60)

        else:
            # Print current time every 10 seconds while waiting
            print(f"⌛ Waiting... {now.strftime('%H:%M:%S')}", end="\r")
            time.sleep(5)

# Handle user-initiated termination
except KeyboardInterrupt:
    print("\n🛑 Script interrupted by user.")

# Ensure browser is closed cleanly on exit
finally:
    driver.quit()
    print("🌐 Browser session closed.")