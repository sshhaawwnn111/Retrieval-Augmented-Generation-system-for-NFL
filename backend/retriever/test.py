# backend/retriever/test_retriever.py
import psycopg2
from retriever import PGVectorRetriever

def main():
    conn = psycopg2.connect(
        dbname="Rotowire_Data",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port=5432
    )

    retriever = PGVectorRetriever(
        db_conn=conn
    )

    query = "Players with ankle injury?"
    results = retriever.search(query)

    print("\nQuery:", query)
    print("Top Results:\n")
    for r in results:
        print(
            f"{r['citation']}\n"
            f"Player:   {r['player_name']}\n"
            f"Date:     {r['date']}\n"
            f"Headline: {r['headline']}\n"
            f"Status:   {r['injury_status']}\n"
            f"Detail:   {r['injury_detail']}\n"
            "----"
        )

    conn.close()

if __name__ == "__main__":
    main()
