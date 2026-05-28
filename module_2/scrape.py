from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

BASE_SURVEY_URL = "https://www.thegradcafe.com/survey"

# build a Grad Cafe survey URL
def build_url(query=None, page=1):
    params = {}

    if page > 1:
        params["page"] = page

    if query:
        params["q"] = query
        params["query"] = query

    query_string = urlencode(params)

    full_url = f"{BASE_SURVEY_URL}?{query_string}"
    return full_url

# Open a webpage with Selenium and return the rendered HTML
def get_page_html(url):
    chrome_options = Options()
    chrome_options.page_load_strategy = "eager"
    chrome_options.binary_location = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    service = Service("/Users/lyuan/Desktop/LY/13. Tools/chromedriver")
    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    driver.set_page_load_timeout(30)

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
        elif item.startswith("GRE"):
            detail["gre_score"] = item.replace("GRE", "").strip()
        elif item.startswith("GRE V"):
            detail["gre_v_score"] = item.replace("GRE V", "").strip()
        elif item.startswith("GRE AW"):
            detail["gre_aw"] = item.replace("GRE AW", "").strip()

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
    blocked = "Sorry, you have been blocked"

    if blocked in html:
        return True

    return False

# save date to json
def save_data(records, filename = "applicant_data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

# load data
def load_data(filename = "applicant_data.json"):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# append date
def append_data(new_records, filename = "applicant_data.json"):
    try:
        existing_records = load_data(filename)
    except FileNotFoundError:
        existing_records = []

    existing_records.extend(new_records)
    save_data(existing_records, filename)

# save html for testing
def save_html(html, filename="test_page.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

# save page progress
PROGRESS_FILE = "scrape_progression.txt"
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

# load html for testing
def load_html(filename="test_page.html"):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    # build url
    # url = build_url(query="Computer Science", page=1)
    # print("URL:")
    # print(url)

    # get html
    # html = get_page_html(url)
    # print("HTML length: ")
    # print(len(html))

    # html parser
    # soup = BeautifulSoup(html, "html.parser")
    # print("Page title: ")
    # print(soup.title)

    # get rows
    # rows = soup.find_all("tr")
    # print("Number of tr rows: ")
    # print(len(rows))

    # find main rows
    # for i, row in enumerate(rows):
    #     print("\n---ROW", i, "---")
    #     print(" ".join(row.stripped_strings))

    # get main rows
    # main_rows = []
    # for row in rows:
    #     if is_main_row(row):
    #         main_rows.append(row)
    # print("Number of main rows:")
    # print(len(main_rows))
    # for i, row in enumerate(main_rows[:5]):
        # print(f"\n--- MAIN ROW {i} ---")
        # print(" ".join(row.stripped_strings))

    # find main row cells
    # first_row = main_rows[0]
    # cells = first_row.find_all("td")
    # print("Number of cells: ")
    # print(len(cells))
    # for i, cell in enumerate(cells):
    #     print(f"\n--- CELL {i} ---")
    #     print(" ".join(cell.stripped_strings))

    # test main row parser
    # first_record = parse_main_row(main_rows[0])
    # print("\nFirst record:")
    # print(first_record)

    # test details
    # first_detail = parse_detail_row(rows[2])
    # print("\nFirst detail:")
    # print(first_detail)

    # test record combination
    # first_record.update(first_detail)
    # print("\nFirst record:")
    # print(first_record)

    # test page parser
    # records = parse_page(rows)
    # print(len(records))
    # for record in records[:5]:
    #     print(record)

    # test multiple pages
    # all_records = []
    # for page in range(1, 2):
    #     print(f"\nScraping page {page}...")
    #     url = build_url(query="Computer Science", page=page)
    #     html = get_page_html(url)
    #     if is_blocked(html):
    #         print("You have been blocked.")
    #         break
    #     else:
    #         save_html(html)
    #         print("Saved HTML locally")
    #     soup = BeautifulSoup(html, "html.parser")
    #     rows = soup.find_all("tr")
    #     page_records = parse_page(rows)
    #     print(f"Number of Records: {len(page_records)}")
    #     all_records.extend(page_records)
    #     time.sleep(60)
    # print("\nAll records:")
    # print(len(all_records))
    # print(all_records[0])
    # print(all_records[1])
    # print(all_records[10])
    # print(all_records[30])
    #
    # save_data(all_records)
    # print("Data saved.")
    #
    # loaded_data = load_data()
    # print("\nLoaded data:")
    # print(len(loaded_data))
    # print("\nFirst loaded record: ")
    # print(loaded_data[0])

    # test locally saved html
    # url = build_url(query="Computer Science", page=1)
    # html = get_page_html(url)
    # if is_blocked(html):
    #     print("You have been blocked.")
    # else:
    #     save_html(html, "test_page.html")
    #     print("Saved test HTML locally")
    #     soup = BeautifulSoup(html, "html.parser")
    #     rows = soup.find_all("tr")
    #     records = parse_page(rows)
    #     print(f"Number of Records: {len(records)}")
    #     if len(records) > 0:
    #         print(f"First Record: \n{records[0]}")
    #     save_data(records, "test_applicant_data.json")
    #     print("Data saved.")
    #     loaded_data = load_data("test_applicant_data.json")
    #     print("\nLoaded data:")
    #     print(len(loaded_data))
    #     print("\nFirst loaded record: ")
    #     print(loaded_data[0])

    # test using local html
    html = load_html("test_page.html")
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")
    records = parse_page(rows)
    print(f"Number of Records: {len(records)}")
    if len(records) > 0:
        print(f"First Record: \n{records[0]}")
    save_data(records, "test_applicant_data.json")
    print("Data saved.")

    # check required categories
    required_keys = [
        "program_name",
        "university",
        "comment",
        "date_added",
        "entry_url",
        "applicant_status",
        "acceptance_date",
        "rejection_date",
        "season",
        "student_type",
        "gre_score",
        "gre_v_score",
        "degree",
        "gpa",
        "gre_aw",
        "raw_main_text",
        "raw_detail_text",
        ]
    for key in required_keys:
        missing_count = sum(1 for record in records if key not in record)
        print(f"{key} missing records: {missing_count}")