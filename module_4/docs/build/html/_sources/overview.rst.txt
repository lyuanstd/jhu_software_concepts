Overview and Setup
==================

This project is a Flask and PostgreSQL application for analyzing graduate admissions data from GradCafe.

The application provides an Analysis page with two main actions:

* Pull Data: refreshes the local PostgreSQL database with newly scraped and cleaned GradCafe records.
* Update Analysis: refreshes the displayed analysis results using the current database contents.

Environment Variables
---------------------

The application supports the following environment variable:

``DATABASE_URL``
    PostgreSQL connection string used by the application, tests, and GitHub Actions.

If ``DATABASE_URL`` is not set, the local development fallback connects to the ``gradcafe`` database with the local user
configured in the code.

Run the Flask App
-----------------

From the ``module_4`` directory:

.. code-block:: bash

   cd module_4
   python src/app.py

Then open the Analysis page:

.. code-block:: text

   http://127.0.0.1:5000/analysis

Run Tests
---------

From the ``module_4`` directory:

.. code-block:: bash

   python -m pytest

To run the full marked suite explicitly:

.. code-block:: bash

   python -m pytest -m "web or buttons or analysis or db or integration"