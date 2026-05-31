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
Before collecting data, I reviewed the site’s robots.txt file to verify that scraping the survey pages was permitted. 
A screenshot of the robots.txt file is included as screenshot.jpg.

To comply with responsible scraping practices:

* No login credentials were used.
* No CAPTCHAs were bypassed.
* No rate limits were bypassed.
* A delay of 21 seconds was added between page requests.
* Scraping automatically stops if blocking behavior is detected.
* Progress is saved so interrupted scraping jobs can be resumed later.

### Data Collection (scrape.py)

The scraper uses a hybrid workflow: urllib constructs Grad Cafe URLs, Selenium with Chrome + Selenium Manager renders 
public result pages, explicit waits wait for table rows, and BeautifulSoup parses the rendered HTML.
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
The scraped dataset contains many inconsistent representations of program and university names.
To address this issue, I used the local LLM standardization workflow provided with the assignment. The cleaning process 
was implemented in multiple stages.

First, clean.py prepares the scraped dataset for LLM processing. The script reads applicant_data.json and creates a new 
field called program, which combines the original program_name and university fields into a single text string. 
This format matches the input expected by the provided LLM standardization tool.
The prepared records are saved to applicant_data_for_llm.json.

The actual LLM standardization is performed using the provided files in the llm_hosting directory. The model generates 
two additional fields:

* llm-generated-program
* llm-generated-university

These fields contain standardized versions of the program and university names while preserving the original scraped 
values.

Because the dataset contained more than 50,000 entries, the LLM standardization step was performed in batches 
of approximately 5,000 records using run_llm_batches. Processing the data in batches improved reliability, and allowed 
interrupted runs to be resumed without repeating previously completed work. After all batches were processed, the 
outputs were merged into a single cleaned JSON file: llm_extend_applicant_data.json.

### Reproducibility
To reproduce the results:
1. Install dependencies: pip install -r requirements.txt
2. Run the scraper: scrape.py
3. Run the cleaning pipeline: clean.py
4. Run the provided LLM standardization tool

## Known Bugs
During development on macOS, Selenium initially could not locate ChromeDriver automatically. A temporary local path 
configuration was used for testing. The final submitted version removes machine-specific paths and relies on Selenium's 
default driver discovery mechanism for portability.