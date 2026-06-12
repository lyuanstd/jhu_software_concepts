Testing Guide
=============

The test suite is written with Pytest and is located under ``module_4/tests``.

Run All Tests
-------------

From the ``module_4`` directory:

.. code-block:: bash

   python -m pytest

Run Marked Tests
----------------

All tests are marked with one or more required Pytest markers:

* ``web``: Flask page rendering and HTML structure tests.
* ``buttons``: Pull Data and Update Analysis endpoint behavior.
* ``analysis``: analysis labels and percentage formatting.
* ``db``: database schema, inserts, idempotency, and query-related tests.
* ``integration``: end-to-end pull, update, and render workflows.

Run the full marked suite:

.. code-block:: bash

   python -m pytest -m "web or buttons or analysis or db or integration"

Run only database tests:

.. code-block:: bash

   python -m pytest -m db

Selectors
---------

The HTML page uses stable selectors for button tests:

* ``data-testid="pull-data-btn"``
* ``data-testid="update-analysis-btn"``

These selectors allow tests to verify button presence without relying only on visible text.

Test Doubles and Mocks
----------------------

The tests use mocks and fake data to keep the suite fast and deterministic. The tests do not depend on live internet
access or long-running web scrapes.

Examples of mocked components include:

* ``refresh_database()``
* ``get_analysis_results()``
* ``psycopg.connect()``
* ``subprocess.run()``
* scraper and loader functions imported by ``refresh_data.py``

Database Tests
--------------

Database tests use a separate PostgreSQL test database named ``gradcafe_test`` locally. In GitHub Actions, the database
connection is provided through ``DATABASE_URL``.

The tests verify that:

* rows are inserted into PostgreSQL,
* required fields are not null,
* duplicate pulls do not create duplicate rows,
* query output dictionaries contain the keys used by the analysis template.

Coverage
--------

The project uses ``pytest-cov`` and requires 100 percent coverage for code under ``module_4/src``. The terminal coverage
output is saved in ``module_4/coverage_summary.txt``.