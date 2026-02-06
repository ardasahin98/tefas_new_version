import requests
import time
import os
import sys
from datetime import datetime
from lxml import html
import openpyxl

# ------------------ DEFAULT FUND LIST ------------------

DEFAULT_FONDS = [
    "TI1", "TIV", "DCB", "BGP", "ALE", "TKM", "IGL", "APT",
    "AFT", "TTA", "IOG", "GO1", "GO3", "GO4", "TE3", "TPC", "AVT"
]

DEFAULT_TXT_FILE = "funds.txt"

# ------------------ USER INPUT ------------------

print(
    "\nChoose input method:\n"
    "1 - Use default fund list\n"
    "2 - Enter fund codes manually\n"
    "3 - Read fund codes from default txt file\n"
)

choice = input("Enter 1, 2, or 3: ").strip()

if choice == "1":
    fonds = DEFAULT_FONDS

elif choice == "2":
    user_input = input(
        "Enter fund codes (comma or space separated):\n> "
    ).strip()

    if not user_input:
        print("No fund codes entered.")
        sys.exit(1)

    fonds = [
        f.strip().upper()
        for f in user_input.replace(",", " ").split()
    ]

elif choice == "3":
    try:
        with open(DEFAULT_TXT_FILE, "r") as f:
            fonds = [
                line.strip().upper()
                for line in f
                if line.strip()
            ]
    except Exception as e:
        print(f"Failed to read {DEFAULT_TXT_FILE}: {e}")
        sys.exit(1)

else:
    print("Invalid choice. Please select 1, 2, or 3.")
    sys.exit(1)

print(f"\nFunds to be processed: {fonds}\n")

# ------------------ SAVE LOCATION ------------------

if getattr(sys, "frozen", False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

base_filename = "tefas_funds.xlsx"
file_path = os.path.join(base_dir, base_filename)

# ------------------ EXCEL SETUP ------------------

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Funds"
ws.append(["Fund", "Price"])

# ------------------ HEADERS ------------------

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
}

# ------------------ MAIN LOOP ------------------

for fond_name in fonds:
    price = ""

    url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fond_name}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        tree = html.fromstring(response.content)

        element = tree.xpath(
            "//*[@id='MainContent_PanelInfo']//ul/li[1]/span"
        )

        if element:
            price = element[0].text_content().strip()

    except requests.exceptions.RequestException as e:
        print(f"{fond_name}: request failed ({e})")

    ws.append([fond_name, price])
    print(f"{fond_name}: {price}")

    time.sleep(1)

# ------------------ SAVE ------------------

wb.save(file_path)

print(f"\nExcel file created:\n{file_path}")