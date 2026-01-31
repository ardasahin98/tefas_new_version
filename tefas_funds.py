import requests
import time
from lxml import html

# ------------------ DEFAULT FUND LIST ------------------

DEFAULT_FONDS = [
    "TI1", "TIV", "DCB", "BGP", "ALE", "TKM", "IGL", "APT",
    "AFT", "TTA", "IOG", "GO1", "GO3", "GO4", "TE3", "TPC"
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

results = {}

for fond_name in fonds:
    price = None
    url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fond_name}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        tree = html.fromstring(response.content)

        # Try multiple times (same HTML, but keeps logic consistent)
        for _ in range(20):
            element = tree.xpath(
                "//*[@id='MainContent_PanelInfo']//ul/li[1]/span"
            )
            if element:
                price = element[0].text_content().strip()
                if price:
                    break
            time.sleep(0.5)

    except requests.exceptions.RequestException as e:
        print(f"{fond_name}: request failed ({e})")

    results[fond_name] = price
    print(f"{fond_name}: {price}")

# ------------------ SUMMARY ------------------

print("\nCompleted.")