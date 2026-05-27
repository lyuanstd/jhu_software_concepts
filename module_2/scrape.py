from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

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
        html = driver.page_source
    finally:
        driver.quit()

    return html

# get main row
def is_main_row(row):
    cells = row.find_all("td")
    return len(cells) >= 5

# parse main row
def parse_main_row(row):
    cells = row.find_all("td")

    university = " ".join(cells[0].stripped_strings)
    program_and_degree = list(cells[1].stripped_strings)
    date_added = " ".join(cells[2].stripped_strings)
    status = " ".join(cells[3].stripped_strings)

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
        "university": university,
        "program_name": program_name,
        "degree": degree,
        "date_added": date_added,
        "applicant_status": status,
        "entry_url": entry_url,
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


if __name__ == "__main__":
    # build url
    url = build_url(query="Computer Science", page=1)
    # print("URL:")
    # print(url)

    # get html
    html = get_page_html(url)
    # print("HTML length: ")
    # print(len(html))

    # html parser
    soup = BeautifulSoup(html, "html.parser")
    # print("Page title: ")
    # print(soup.title)

    # get rows
    rows = soup.find_all("tr")
    # print("Number of tr rows: ")
    # print(len(rows))

    # find main rows
    # for i, row in enumerate(rows):
    #     print("\n---ROW", i, "---")
    #     print(" ".join(row.stripped_strings))

    # get main rows
    main_rows = []
    for row in rows:
        if is_main_row(row):
            main_rows.append(row)
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
    first_record = parse_main_row(main_rows[0])
    # print("\nFirst record:")
    # print(first_record)

    # test details
    first_detail = parse_detail_row(rows[2])
    # print("\nFirst detail:")
    # print(first_detail)

    # test record combination
    first_record.update(first_detail)
    # print("\nFirst record:")
    # print(first_record)


