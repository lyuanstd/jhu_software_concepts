# Module 4 - Testing and Documentation
Name: Liqing Yuan

JHED ID: lyuan20

## Overview

This project extends the GradCafe Analytics System developed in Module 3 by adding automated testing, continuous 
integration, and documentation.

The application collects graduate admissions data from GradCafe, stores the data in PostgreSQL, performs SQL-based 
analysis, and presents the results through a Flask web application.

This module focuses on software quality and maintainability through:

- Automated Pytest test suites
- Database integration tests
- End-to-end workflow testing
- GitHub Actions continuous integration
- Sphinx-generated developer documentation

---

## Features

The system provides the following functionality:

- Flask web application for viewing admissions analysis
- PostgreSQL database using the Module 3 schema
- Automated data refresh workflow
- SQL-based admissions statistics and reporting
- Idempotent database inserts using uniqueness constraints
- Comprehensive Pytest test suite
- GitHub Actions automated testing
- Sphinx documentation and API reference

---

## Project Structure

```text

module_4/

├── src/

│   ├── app.py

│   ├── load_data.py

│   ├── query_data.py

│   ├── refresh_data.py

│   ├── static/

│   └── templates/

├── tests/

├── docs/

├── pytest.ini

├── requirements.txt

├── coverage_summary.txt

└── actions_success.png
```


---

## Prerequisites

The project was developed using:

- Python 3.13
- PostgreSQL
- Flask
- Pytest
- Sphinx

Install all dependencies with:

```bash

pip install -r requirements.txt

```

---

## PostgreSQL Configuration

The application supports configuration through the DATABASE_URL environment variable.

If DATABASE_URL is not provided, the application falls back to the local PostgreSQL configuration defined in the source 
code.

---

## Running the Application

From the repository root:

```bash

cd module_4

python src/app.py

```


Open the application in a browser: http://127.0.0.1:5000/analysis 


---

## Running Tests

Run the full test suite: 

```bash

python -m pytest 

```

Run only marked tests: 

```bash

python -m pytest -m "web or buttons or analysis or db or integration"

```

---

## Test Coverage

The project uses pytest-cov to measure code coverage.

Coverage proof is stored in: module_4/coverage_summary.txt 

The project achieves 100% coverage for all application logic under module_4/src.

---

## Documentation

Sphinx documentation is generated locally. 

Generated HTML files: module_4/docs/build/html

Open the documentation homepage: module_4/docs/build/html/index.html 

Documentation includes:

- Overview and setup
- Architecture
- Testing guide
- API reference

Because the GitHub repository is private, Read the Docs Community cannot host the documentation. The generated HTML 
documentation is included directly in the repository.

The active GitHub Actions workflow is located at the repository root under .github/workflows/tests.yml, because GitHub 
Actions only recognizes workflow files stored in the repository-level .github/workflows directory. A copy is also 
included under module_4/.github/workflows/tests.yml for assignment deliverables.
---
