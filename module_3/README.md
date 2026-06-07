# Module 3 - Database Queries Assignment
Name: Liqing Yuan

JHED ID: lyuan20

## Overview
This project extends the GradCafe web scraping application from Module 2 by loading the scraped and cleaned data into a 
PostgreSQL database, querying the data to answer questions and creating a Flask web application for interactive analysis.
The dynamic webpage displays SQL results, and allows users to pull new GradCafe data and refresh analysis results.

## Approach
### Prerequisites
Before running the project, install:
* Python 3
* PostgreSQL
* Google Chrome and ChromeDriver (for scraping)
Create a PostgreSQL database named "gradcafe"

### Install Required Packages
pip install -r requirements.txt

### Run load_data.py
This script:
* Creates the applicants table
* Loads applicant records from the JSON dataset
* Inserts records into PostgreSQL

### Run query_data.py
This script executes all required SQL analysis queries and prints results to the console.

### Run the Flask Application
1. Run app.py to start the Flask server.
2. Open http://127.0.0.1:5000. This dynamic webpage displays queries and results.

### Pull Data
The Pull Data button reuses the Module 2 scraping workflow to:
1. Scrape new GradCafe entries.
2. Clean the scraped data.
3. Insert only new records into PostgreSQL. Duplicate records are ignored.

### Update Analysis
The Update Analysis button refreshes the query results using the latest data currently stored in PostgreSQL.

If a data pull is currently running, the application prevents analysis updates and displays a message to users.

### Project Files
* app.py – Flask web application
* load_data.py – database creation and loading
* query_data.py – SQL queries
* refresh_data.py – data refresh workflow
* templates/index.html – webpage template
* static/style.css – webpage styling

## Development Notes
### Query 8 and Query 9 Results
Query 8 and Query 9 analyze PhD Computer Science acceptance results for Carnegie Mellon University, Georgetown 
University, MIT, and Stanford University.

In the current dataset, Georgetown University has zero matching records after applying all filters (PhD, Accepted, 
Computer Science, and 2026 date criteria). Therefore, Georgetown does not appear in the displayed query results.

### ChromeDriver Configuration
During development on macOS, Selenium initially could not locate ChromeDriver automatically. A temporary machine-specific 
Chrome and ChromeDriver path configuration was used to test the scraper locally.

The final submitted version removes hard-coded local paths and relies on Selenium’s default driver discovery mechanism 
to improve portability across different systems.


### Module 2 Modifications for Faster Refresh
To make the Pull Data operation more practical for a Flask webpage demonstration, a few modifications were made to the 
original Module 2 workflow.

1. Reduced Scraping Scope: The original scraper was designed to process hundreds of pages. For data refresh operations 
within the web application, the scraper was modified to run a smaller number of pages: scrape_data(max_pages=3, 
use_progress=False). This allows refresh operations to complete in a reasonable amount of time while still demonstrating
the ability to include new records.

2. LLM Step Omitted During Refresh: The Pull Data workflow reuses the scraping and cleaning stages from Module 2 but 
does not rerun the LLM enrichment step. This significantly reduces refresh time. New records are cleaned and inserted 
into PostgreSQL, while previously generated LLM fields remain available for analysis.

