import psycopg
from decimal import Decimal

# convert decimal result to string
def format_value(value):
    if isinstance(value, Decimal):
        return str(value)
    return str(value)

def format_row(row):
    return ", ".join(format_value(value) for value in row)

# connect to the local PostgreSQL database
def get_connection():
    return psycopg.connect(
        dbname="gradcafe",
        user="lyuan"
    )

# run SQL query and print the result
def run_query(conn, question, sql):
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()

    formatted_results = []

    print("\n" + question)
    print("-" * len(question))

    for row in result:
        formatted_row = format_row(row)
        formatted_results.append(formatted_row)
        print(formatted_row)

    cur.close()
    return formatted_results

# get list of questions and sql results
def get_queries():
    return [
        {
            "question": "1. How many entries are for Fall 2026?",
            "sql": """
                   SELECT COUNT(*)
                   FROM applicants
                   WHERE term = 'Fall 2026';
           """
        },
        {
            "question": "2. What percentage of entries are from international students (not American or Other) ?",
            "sql": """
                   SELECT CONCAT(
                      ROUND(
                          100.0 * COUNT(*) /
                          (SELECT COUNT(*) FROM applicants), 2
                      ),'%')
                   FROM applicants
                   WHERE us_or_international = 'International';
                   """
        },
        {
            "question": "3. What is the average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics?",
            "sql": """
                   SELECT ROUND(AVG(gpa)::numeric, 2)    AS avg_gpa,
                          ROUND(AVG(gre)::numeric, 2)    AS avg_gre,
                          ROUND(AVG(gre_v)::numeric, 2)  AS avg_gre_v,
                          ROUND(AVG(gre_aw)::numeric, 2) AS avg_gre_aw
                   FROM applicants
                   """
        },
        {
            "question": "4. What is their average GPA of American students in Fall 2026?",
            "sql": """
                   SELECT ROUND(AVG(gpa)::numeric, 2) AS avg_gpa
                   FROM applicants
                   WHERE us_or_international = 'American'
                     AND term = 'Fall 2026';
                   """
        },
        {
            "question": "5. What percent of entries for Fall 2026 are Acceptances (to two decimal places)?",
            "sql": """
                   SELECT CONCAT(ROUND(
                                  100.0 * COUNT(*) /
                                  (SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026'), 2
                          ),'%')
                   FROM applicants
                   WHERE term = 'Fall 2026'
                     AND status LIKE 'Accepted%';
                   """
        },
        {
            "question": "6. What is the average GPA of applicants who applied for Fall 2026 who are Acceptances?",
            "sql": """
                   SELECT ROUND(AVG(gpa)::numeric, 2) AS avg_gpa_accepted
                   FROM applicants
                   WHERE term = 'Fall 2026'
                     AND status LIKE 'Accepted%';
                   """
        },
        {
            "question": "7. How many entries are from applicants who applied to JHU for a masters degrees in Computer Science?",
            "sql": """
                   SELECT COUNT(*)
                   FROM applicants
                   WHERE program = 'Computer Science, Johns Hopkins University'
                     AND degree ILIKE '%master%';
                   """
        },
        {
            "question": "8. How many entries from 2026 are acceptances from applicants who applied to Georgetown University, MIT, Stanford University, or Carnegie Mellon University for a PhD in Computer Science?",
            "sql": """
                   SELECT program, COUNT(*) AS acceptance_count
                   FROM applicants
                   WHERE degree = 'PhD'
                     AND status LIKE 'Accepted%'
                     AND EXTRACT(year FROM date_added) = 2026
                     AND program IN ('Computer Science, Carnegie Mellon University',
                                     'Computer Science, Georgetown University',
                                     'Computer Science, Massachusetts Institute of Technology (MIT)',
                                     'Computer Science, Stanford University')
                   GROUP BY program
                   ORDER BY program;
                   """
        },
        {
            "question": "9. Do your numbers for question 8 change if you use LLM Generated Fields rather than your downloaded fields",
            "sql": """
                   SELECT llm_generated_university, COUNT(*) AS acceptance_count_llm
                   FROM applicants
                   WHERE degree = 'PhD'
                     AND status LIKE 'Accepted%'
                     AND EXTRACT(year FROM date_added) = 2026
                     AND llm_generated_program = 'Computer Science'
                     AND llm_generated_university IN ('Carnegie Mellon University',
                                                      'Georgetown University',
                                                      'Massachusetts Institute of Technology',
                                                      'Stanford University')
                   GROUP BY llm_generated_university
                   ORDER BY llm_generated_university;
                   """
        },
        {
            "question": "10. How many applications were submitted to Artificial Intelligence master’s programs, and what was the acceptance rate?",
            "sql": """
                    SELECT COUNT(*) AS total_applications,
                           CONCAT(ROUND(
                                   100.0 * SUM(
                                           CASE
                                               WHEN status LIKE 'Accepted%' THEN 1
                                               ELSE 0
                                               END
                                           ) / COUNT(*),
                                   2
                           ),'%') AS acceptance_rate
                    FROM applicants
                    WHERE degree = 'Masters'
                      AND program ILIKE '%artificial intelligence%';
                    """
        },
        {
            "question": "11. What are the application counts and the acceptance rate of JHU and UT Austin?",
            "sql": """
                    SELECT
                        CASE
                           When program ILIKE '%johns hopkins%' THEN 'Johns Hopkins University'
                           When program ILIKE '%university of texas at austin%' THEN 'University of Texas at Austin'
                           END    AS university,
                           COUNT(*)   AS total_applications,
                           CONCAT(ROUND(
                                   100.0 * SUM(
                                           CASE
                                               WHEN status LIKE 'Accepted%' THEN 1
                                               ELSE 0
                                               END) / COUNT(*),
                                   2),'%') AS acceptance_rate
                    FROM applicants
                    WHERE program ILIKE '%johns hopkins%'
                          OR program ILIKE '%university of texas at austin%'
                    GROUP BY university
                    ORDER BY university;
                    """
        }
    ]

def main():
    conn = get_connection()

    for item in get_queries():
        run_query(conn, item["question"], item["sql"])

    conn.close()


if __name__ == "__main__":
    main()