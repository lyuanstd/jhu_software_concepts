from flask import Flask, render_template
from query_data import get_connection, get_queries, run_query
from refresh_data import refresh_database

app = Flask(__name__)

is_pulling_data = False

# run all SQL queries and return results for the webpage
def get_analysis_results():
    conn = get_connection()
    results = []

    for item in get_queries():
        result = run_query(conn, item["question"], item["sql"])
        results.append({
            "question": item["question"],
            "result": result
        })

    conn.close()
    return results

@app.route("/")
def index():
    results = get_analysis_results()

    return render_template(
        "index.html",
        results=results,
        message=None,
        is_pulling_data=is_pulling_data
    )

@app.route("/pull-data")
def pull_data():
    global is_pulling_data

    if is_pulling_data:
        return render_template(
            "index.html",
            results=None,
            message="A data pull is already running. Please wait before starting another one.",
            is_pulling_data=is_pulling_data
        )

    is_pulling_data = True

    try:
        inserted_count = refresh_database()
        message = f"Data Pull completed. {inserted_count} new records were added to the database. Click Update Analysis to refresh the results."

    except Exception as e:
        message = f"Data pull failed: {e}"

    finally:
        is_pulling_data = False

    return render_template(
        "index.html",
        results=None,
        message=message,
        is_pulling_data=is_pulling_data
    )

@app.route("/update-analysis")
def update_analysis():
    if is_pulling_data:
        return render_template(
            "index.html",
            results=None,
            message="Analysis was not updated because a data pull is currently running.",
            is_pulling_data=is_pulling_data
        )

    return render_template(
        "index.html",
        results=get_analysis_results(),
        message="Analysis was updated using the latest data in the database.",
        is_pulling_data=is_pulling_data
    )


if __name__ == "__main__":
    app.run(debug=True)