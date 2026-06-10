from flask import Flask, jsonify, redirect, render_template

from query_data import get_connection, get_queries, run_query
from refresh_data import refresh_database


def get_analysis_results():
    """Run all SQL queries and return formatted results for the webpage."""
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


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["IS_PULLING_DATA"] = False

    if test_config:
        app.config.update(test_config)

    @app.route("/")
    def home():
        return redirect("/analysis")

    @app.route("/analysis")
    def analysis():
        return render_template(
            "index.html",
            results=get_analysis_results(),
            message=None,
            is_pulling_data=app.config["IS_PULLING_DATA"]
        )

    @app.route("/pull-data", methods=["POST"])
    def pull_data():
        if app.config["IS_PULLING_DATA"]:
            return jsonify({"ok": False, "busy": True}), 409

        app.config["IS_PULLING_DATA"] = True

        try:
            inserted_count = refresh_database()
            return jsonify({
                "ok": True,
                "inserted_count": inserted_count
            }), 200

        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500

        finally:
            app.config["IS_PULLING_DATA"] = False

    @app.route("/update-analysis", methods=["POST"])
    def update_analysis():
        if app.config["IS_PULLING_DATA"]:
            return jsonify({"ok": False, "busy": True}), 409

        results = get_analysis_results()

        return jsonify({
            "ok": True,
            "results": results
        }), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)