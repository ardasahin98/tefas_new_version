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

# ------------------ USER INPUT ------------------

user_input = input(
    "Enter fund codes (comma or space separated).\n"
    "Press Enter to use default list:\n> "
).strip()

if user_input:
    fonds = [f.strip().upper() for f in user_input.replace(",", " ").split()]
else:
    fonds = DEFAULT_FONDS

print(f"\nFunds to be processed: {fonds}\n")

# ------------------ SAVE LOCATION ------------------

if getattr(sys, "frozen", False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

base_filename = f"tefac_funds.xlsx"
file_path = os.path.join(base_dir, base_filename)

# ------------------ EXCEL SETUP ------------------

wb = openpyxl.Workbook()
ws = wb.active
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

# ------------------ SAVE ------------------

wb.save(file_path)

print(f"\nExcel file created:\n{file_path}")