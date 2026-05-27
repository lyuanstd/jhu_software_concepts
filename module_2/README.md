# Module 2 - Web Scraping Assignment
Name: Liqing Yuan
JHED ID: lyuan20

## Approach
This assignment gathers data from Grad Cafe data about recent applicants and parse applicant data. The scraper is
designed to use urllib for URL construction, Selenium for browser-rendered pages, and BeautifulSoup/ string method/ 
regex for parsing applicant information from the rendered HTML.

## robots.txt Check
Before scraping, I checked Grad Cafe's robots.txt file in a browser and saved a screenshot as robot_screenshot.jpg. I 
reviewed the file to confirm that the pages used for this assignment were not disallowed. The scraper only accesses 
publicly available applicant entries required for the assignment, uses reasonable delays and does not bypass of 
restrictions, logins, CAPTCHAs, or rate limits.