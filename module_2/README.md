# Module 2 - Web Scraping Assignment
Name: Liqing Yuan
JHED ID: lyuan20

## Module Information
Module 2 - Web Scraping
Assignment title: Web Scraping (a web scraper for Grad Cafe)
Due Date: May 31, 2026

## Approach
### Overview
The goal of this assignment was to collect graduate admissions data from The Grad Cafe, store the data in a structured 
JSON format, and then standardize program and university names using the provided local LLM cleaning pipeline.
The project consists of two major components:

1. Data Collection (scrape.py)
2. Data Cleaning (clean.py and provided LLM tools)

### Responsible Scraping
Before collecting data, I reviewed the site’s robots.txt file to verify that scraping the survey pages was permitted. A screenshot of the robots.txt file is included as screenshot.jpg.

To comply with responsible scraping practices:

* No login credentials were used.
* No CAPTCHAs were bypassed.
* No rate limits were bypassed.
* A delay of 21 seconds was added between page requests.
* Scraping automatically stops if blocking behavior is detected.
* Progress is saved so interrupted scraping jobs can be resumed later.

### Data Collection (scrape.py)
The scraper uses:

* urllib.parse.urlencode() to construct query URLs
* Selenium to render dynamic page content
* BeautifulSoup/string method to parse HTML

The scraper automatically handles pagination and iterates through result pages.

For each applicant record, the scraper extracts:

* program_name
* university
* applicant_status
* acceptance_date
* rejection_date
* date_added
* entry_url
* comment
* season
* student_type
* degree
* GPA
* GRE
* GRE V
* GRE AW

To preserve traceability, the original listing text is also stored in:

* raw_main_text
* raw_detail_text

All records are saved to: applicant_data.json

The final dataset contains 51991 graduate applicant entries.

### Progress Recovery and Blocking Handling
Because the dataset contains more than 50,000 records, scraping may run for many hours. The scraper saves page progress 
to a local progress file so that interrupted runs can resume automatically.

The scraper also detects temporary blocking pages. If a blocking page is encountered, scraping stops immediately instead
of repeatedly sending requests. The user can later resume scraping from the last successfully completed page.

### Data Structures
The data is stored as a list of dictionaries. Each dictionary represents one applicant record and contains fields 
such as program_name, university, degree, GPA, and applicant status.

Example:

{
    "program_name": "Statistics",
    "university": "Columbia University",
    "degree": "PhD",
    ...
}

The full dataset is stored as a JSON array.

### Data cleaning (clean.py)
The provided local language model expects a field named: program, which contains both the program and university name.
However, my scraped dataset stores these values separately as: program_name, and university. Therefore, clean.py creates
an intermediate field: program = "program_name, university"

This allows the provided LLM tool to process the records without modifying the original scraped data structure.

The cleaning pipeline preserves the original values while adding:

* llm-generated-program
* llm-generated-university

The cleaned output is saved as: llm_extend_applicant_data.json

### Reproducibility
To reproduce the results:
1. Install dependencies: pip install -r requirements.txt
2. Run the scraper: scrape.py
3. Run the cleaning pipeline: clean.py
4. Run the provided LLM standardization tool