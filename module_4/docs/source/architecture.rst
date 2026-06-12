Architecture
============

The GradCafe analytics application has three main layers: the web layer, the ETL layer, and the database layer.

Web Layer
---------

The web layer is implemented with Flask in ``src/app.py``. It exposes a testable ``create_app(...)`` factory and provides the following routes:

* ``GET /`` redirects to ``/analysis``.
* ``GET /analysis`` renders the analysis page.
* ``POST /pull-data`` triggers the data refresh workflow.
* ``POST /update-analysis`` refreshes analysis results from the database.

The page includes stable UI selectors such as ``data-testid="pull-data-btn"`` and ``data-testid="update-analysis-btn"``
so tests can locate buttons reliably.

ETL Layer
---------

The ETL workflow is coordinated by ``src/refresh_data.py``. It runs the scraper, executes the cleaning process, loads
cleaned JSON records, and inserts new rows into PostgreSQL.

The lower-level database loading logic lives in ``src/load_data.py``. It parses dates and numeric fields, creates the
required ``applicants`` table, and inserts cleaned records.

Database Layer
--------------

The application stores records in PostgreSQL using the Module 3 schema. The ``applicants`` table includes fields such as
``program``, ``date_added``, ``url``, ``status``, ``term``, ``degree``, ``us_or_international``, ``gpa``, GRE fields,
and LLM-generated program and university fields.

The ``url`` field is unique and is used as the idempotency key. Duplicate rows are ignored with ``ON CONFLICT (url) DO
NOTHING``.

Analysis Layer
--------------

The query layer is implemented in ``src/query_data.py``. It defines SQL questions, runs queries, formats result rows,
and returns the analysis data used by the Flask template.