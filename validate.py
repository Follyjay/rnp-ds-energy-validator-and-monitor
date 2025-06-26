import time
import winsound
import pytz
from time import sleep
import datetime
import logging
from config import CSV_DIR, XML_DIR
from alert import alert_mismatch
from helper import (
    ds_file_monitor,
    get_latest_file,
    get_csv_quantity_for_hour,
    get_csv_direction_flow_for_hour,
    get_xml_quantity_for_hour
)

def validate_hourly_flow():
    """
    Validates RNP-DS flow for the current London hour.
    Compares the quantity values in the latest CSV and XML files.
    If a mismatch is detected, triggers an alert notification.
    """
    # Get current time in Europe/London timezone (GMT/BST)
    london_tz = pytz.timezone('Europe/London')
    now = datetime.datetime.now(london_tz)

    # Calculate current London hour and label for display
    london_hour = (now.hour + 2) % 24
    hour_label = f"{london_hour:02d}:00 - {london_hour+1:02d}:00"
    hour_index = (london_hour + 1) % 24  # Adjust index for CSV row (0-based index)

    print(f"\n⏰ Running validation for hour: {hour_label}")
    logging.info(f"Running validation for hour: {hour_label}")

    # Wait briefly to ensure CSV has been saved
    time.sleep(2)
    print("🔁 Waiting for a new DS XML file...")

    while True:
        new_files = ds_file_monitor()
        if new_files:
            print(f"🆕 New DS file(s) detected: {new_files}")
            break
        else:
            winsound.Beep(2000, 3000)  # Beep at 2000 Hz for 2 second
            print("⏳ Still waiting... No new DS file yet.")
            time.sleep(60)  # Wait 60 seconds before checking again

    # Retrieve the most recently saved RNP CSV and DS XML files
    csv_file = get_latest_file(CSV_DIR)
    xml_file = get_latest_file(XML_DIR)

    if not csv_file or not xml_file:
        print("🚫 Missing CSV or XML file.")
        logging.warning("Missing CSV or XML file during validation.")
        return

    try:
        # Extract quantities from both files for the target hour
        csv_value = get_csv_quantity_for_hour(hour_index, csv_file)
        direction_of_flow = get_csv_direction_flow_for_hour(hour_index, csv_file)
        xml_value = get_xml_quantity_for_hour(hour_index, direction_of_flow, xml_file)

        print(f"🔄 Direction: {direction_of_flow} | CSV: {csv_value} | XML: {xml_value}")

        print(f"XML Value: {xml_value}")

        # Compare values and log the result
        if csv_value == xml_value:
            print(f"✅ Match for {hour_label}: {csv_value}")
            logging.info(f"✅ Match for {hour_label}: {csv_value}")
        else:
            # Trigger alert in case of mismatch
            alert_mismatch(csv_value, xml_value, hour_label, csv_file, xml_file)

    except Exception as e:
        logging.error(f"🚨 Error during validation: {e}")
        print(f"🚨 Error: {e}")


# last_time_zone = datetime.datetime.now().astimezone().tzinfo
#utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
# london = pytz.timezone("Europe/London")
# local_now = datetime.datetime.now(london)
# print(local_now)

# now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/London'))
# offset = now.utcoffset()
# print(now.minute)