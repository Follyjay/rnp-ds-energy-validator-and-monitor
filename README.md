# ⚡ Automated Monitoring and Validation of RNP-DS Energy Flow Data

This Python-based project automates the validation of hourly energy flow data between the **Regional Nomination Platform (RNP)** and **Day Schedule (DS)** system. It replaces tedious manual comparisons with an efficient, scheduled validation pipeline that alerts users in real time when mismatches occur.

---

## 📌 Key Features

- 🌐 Scrapes hourly flow data from the RNP website using a persistent Selenium session
- 📂 Monitors new DS XML files placed in a directory
- 🔍 Compares RNP and DS flow values for each hour
- 📧 Sends alert emails when mismatches occur
- 🔊 Beeps audibly for local alerts (Windows only)
- 🧾 Logs results and stores outputs with time-stamped filenames

---

## 🗂 Project Structure

├── rnp_files/ # RNP CSV files (scraped)
├── ds_files/ # DS XML files (uploaded externally)
├── logs/ # Text-based validation logs
├── alert.py # Sound and email alert handler
├── config.py # File paths and email credentials
├── helper.py # Utility functions (CSV/XML parsing, monitoring)
├── main.py # Entry point: runs scraper and validation
├── scraper.py # Web scraping and CSV saving
├── validate.py # Core validation logic
├── my_email_config.py # SMTP logic for email alerts
└── README.md # Project documentation

yaml
Copy
Edit

---

## ⚙️ Technologies Used

- **Python 3.x**
- `selenium` – for browser automation
- `xml.etree.ElementTree` – for DS XML parsing
- `pandas` – for CSV handling
- `smtplib` – for email notifications
- `winsound` – for audible alerts (Windows only)
- `pytz` – timezone handling
- `logging` – logging events and outcomes

---

## 🧪 Validation Logic

- At **HH:45**, the system scrapes the latest RNP flow data.
- It waits for a **new DS XML file** to be dropped into `ds_files/`.
- It then compares flow values for the current hour.
- If there’s a mismatch, it:
  - Logs the event
  - Sounds 3 beeps
  - Sends an email to configured recipients

**Sample Output:**

| Hour         | Direction | RNP Value | DS Value | Result             |
|--------------|-----------|-----------|----------|--------------------|
| 06:00–07:00  | FRGB      | 1000      | 1000     | ✅ Match           |
| 07:00–08:00  | GBFR      | 1531      | 1000     | ❌ Mismatch Alert  |

---

## ▶️ How to Run

### 1. Install Dependencies

```bash
pip install selenium pandas pytz

### 2. Set Up Your Environment
.Place your Firefox WebDriver in PATH.
.Update your credentials in config.py and my_email_config.py.

EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
EMAIL_RECIPIENTS = ["recipient1@example.com", "recipient2@example.com"]

### 3. Run the Application
```bash
python main.py

Make sure:

. RNP site is accessible
. DS XML files are added to the ds_files/ directory

🛠 Challenges Tackled
✅ Timezone offset between UTC and BST (RNP uses UTC)
✅ Parsing nested XML namespaces
✅ SMTP setup requiring app passwords for Gmail
✅ Circular imports resolved by modularizing shared logic

📬 Contact
Want to collaborate or learn more?
Connect on LinkedIn

📝 License
This project is licensed under the MIT License.