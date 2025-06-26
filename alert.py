import winsound
import logging
import time
from my_email_config import send_email

def alert_mismatch(csv_val, xml_val, hour, csv_file, xml_file):
    """
    Handles RNP-DS mismatch alerts by:
    - Logging the issue
    - Printing a formatted alert message
    - Sounding an audible alert (Windows only)
    - Sending an email notification to configured recipients

    Parameters:
        csv_val (int): Value extracted from the RNP CSV file.
        xml_val (int): Value extracted from the DS XML file.
        hour (str): Time frame of the mismatch (e.g., "14:00 - 15:00").
        csv_file (str): Path to the CSV file used for comparison.
        xml_file (str): Path to the XML file used for comparison.
    """
    
    # Compose the alert message
    msg_text = f"""
    ⚠️ RNP-DS Mismatch Detected

    Time-Frame: {hour}
    RNP Flow Value: {csv_val}
    DS Quantity Value: {xml_val}

    RNP File: {csv_file}
    DS File: {xml_file}

    Please investigate manually.
    
    📢 Kindly Note: Suggested Correct Flow Value based on RNP = {csv_val}
    """

    # Print to console and log the warning
    print(msg_text)
    logging.warning(msg_text)

    # Trigger an audible alert (3 beeps)
    for _ in range(3):
        winsound.Beep(2000, 1000)  # Beep at 2000 Hz for 1 second
        time.sleep(0.3)  # Short pause between beeps

    # Send email alert
    #send_email(msg_text, hour)
