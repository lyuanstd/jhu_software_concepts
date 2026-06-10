import psycopg

conn = psycopg.connect(
    dbname="gradcafe",
    user="lyuan"
)

print("Connected!")

conn.close()