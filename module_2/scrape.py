from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from pathlib import Path
import time
import json

BASE_SURVEY_URL = "https://www.thegradcafe.com/survey"

MODULE_DIR = Path(__file__).resolve().parent
DATA_FILE = MODULE_DIR / "applicant_data.json"
PROGRESS_FILE = MODULE_DIR / "scrape_progress.txt"
TEST_HTML_FILE = MODULE_DIR / "test_page.html"

# build a Grad Cafe survey URL
def build_url(query=None, page=1):
    params = {}

    if page > 1:
        params["page"] = page

    if query:
        params["q"] = query
        params["query"] = query

    query_string = urlencode(params)
    if query_string:
        return f"{BASE_SURVEY_URL}?{query_string}"
    return BASE_SURVEY_URL

# Open a webpage with Selenium and return the rendered HTML
def get_page_html(url):
    chrome_options = Options()
    chrome_options.page_load_strategy = "eager"

    # Selenium automatically locate ChromeDriver
    #driver = webdriver.Chrome(options=chrome_options)

    #Local environment
    chrome_options.binary_location = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    service = Service("/Users/lyuan/Desktop/LY/13. Tools/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.set_page_load_timeout(60)

    try:
        driver.get(url)
        # wait for elements to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "tr"))
        )

        html = driver.page_source

    finally:
        driver.quit()

    return html

# get main row
def is_main_row(row):
    cells = row.find_all("td")
    return len(cells) >= 5

# parse decision date
def parse_decision_date(status):
    acceptance_date = None
    rejection_date = None

    if status.startswith("Accepted on"):
        acceptance_date = status.replace("Accepted on", "").strip()
    elif status.startswith("Rejected on"):
        rejection_date = status.replace("Rejected on", "").strip()

    return acceptance_date, rejection_date

# parse main row
def parse_main_row(row):
    cells = row.find_all("td")

    university = " ".join(cells[0].stripped_strings)
    program_and_degree = list(cells[1].stripped_strings)
    date_added = " ".join(cells[2].stripped_strings)
    status = " ".join(cells[3].stripped_strings)
    acceptance_date, rejection_date = parse_decision_date(status)

    DEGREE_TYPE = ["PhD", "Masters", "MFA", "MBA", "JD", "EdD", "Other (use notes)", "PsyD"]
    program_name = None
    degree = None

    for item in program_and_degree:
        if item in DEGREE_TYPE:
            degree = item
        else:
            program_name = item

    link_tag = cells[4].find("a")
    entry_url = None

    if link_tag:
        entry_url = "https://www.thegradcafe.com" + link_tag.get("href")

    return {
        "program_name": program_name,
        "university": university,
        "date_added": date_added,
        "entry_url": entry_url,
        "applicant_status": status,
        "acceptance_date": acceptance_date,
        "rejection_date": rejection_date,
        "degree": degree,
        "raw_main_text": " ".join(row.stripped_strings),
    }

# parse details
def parse_detail_row(row):
    items = list(row.stripped_strings)

    detail = {
        "season": None,
        "student_type": None,
        "gpa": None,
        "gre_score": None,
        "gre_v_score": None,
        "gre_aw": None,
        "raw_detail_text": " ".join(items)
    }

    for item in items:
        if item.startswith("Fall") or item.startswith("Spring") or item.startswith("Summer") or item.startswith("Winter"):
            detail["season"] = item
        elif item.startswith("American") or item.startswith("International"):
            detail["student_type"] = item
        elif item.startswith("GPA"):
            detail["gpa"] = item.replace("GPA", "").strip()
        elif item.startswith("GRE V"):
            detail["gre_v_score"] = item.replace("GRE V", "").strip()
        elif item.startswith("GRE AW"):
            detail["gre_aw"] = item.replace("GRE AW", "").strip()
        elif item.startswith("GRE"):
            detail["gre_score"] = item.replace("GRE", "").strip()

    return detail

# parse comment row
def parse_comment_row(row):
    cells = row.find_all("td")
    comment = " ".join(row.stripped_strings)
    if len(cells) == 1 and comment != "":
        return comment
    return None

# parse page
def parse_page(rows):
    records = []
    for i, row in enumerate(rows):
        if is_main_row(row):
            main_data = parse_main_row(row)

            detail_data = {}
            if i + 1 < len(rows):
                detail_data = parse_detail_row(rows[i + 1])

            comment = None
            if i + 2 < len(rows):
                comment = parse_comment_row(rows[i + 2])

            main_data.update(detail_data)
            main_data["comment"] = comment

            records.append(main_data)

    return records

# block detection
def is_blocked(html):
    blocked = [
        "Sorry, you have been blocked",
        "You are unable to access thegradcafe.com",
        "Cloudflare Ray ID"
    ]
    for b in blocked:
        if b in html:
            return True
    return False

# save date to json
def save_data(records, filename=DATA_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

# load data
def load_data(filename=DATA_FILE):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# append data
def append_data(new_records, filename=DATA_FILE):
    try:
        existing_records = load_data(filename)
    except FileNotFoundError:
        existing_records = []
    existing_urls = set()
    for record in existing_records:
        if record.get("entry_url"):
            existing_urls.add(record["entry_url"])

    unique_new_records = []

    for record in new_records:
        entry_url = record.get("entry_url")
        if entry_url not in existing_urls:
            unique_new_records.append(record)
            if entry_url:
                existing_urls.add(entry_url)
    existing_records.extend(unique_new_records)

    save_data(existing_records, filename)
    print(f"Added {len(unique_new_records)} new records.")
    print(f"Skipped {len(new_records) - len(unique_new_records)} duplicate records.")

# save page progress
def save_progress(page):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write(str(page))

# load page progress
def load_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 1


def scrape_data(max_pages=500, use_progress=True):
    if use_progress:
        start_page = load_progress()
    else:
        start_page = 1
    end_page = start_page + max_pages - 1

    for page in range(start_page, end_page + 1):
        print(f"\nScraping page: {page}")
        url = build_url(page=page)
        try:
            html = get_page_html(url)
        except Exception as e:
            print(f"Error on page {page}: {e}")
            print("Waiting 60 seconds and retrying...")

            time.sleep(60)

            try:
                html = get_page_html(url)
            except Exception:
                print("Retry failed. Stopping scraping...")
                break

        if is_blocked(html):
            print("Blocked")
            break

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr")
        records = parse_page(rows)
        print(f"Number of Records: {len(records)}")
        if len(records) == 0:
            print("No records found")
            break
        append_data(records)
        if use_progress:
            save_progress(page + 1)
            print(f"Saved Progress: {page} pages")

        time.sleep(21)


if __name__ == "__main__":
    scrape_data()