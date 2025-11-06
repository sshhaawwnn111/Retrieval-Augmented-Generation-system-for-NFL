from sentence_transformers import SentenceTransformer
import psycopg2
import time


model = SentenceTransformer("all-MiniLM-L6-v2")  # <--- sentence transformer model used



conn = psycopg2.connect(
    dbname="Rotowire_Data",
    user="postgres",
    password="put your password here", # <------ put ur own password and other info
    host="localhost",
    port="5432"
)
cur = conn.cursor()


cur.execute("SELECT id, notes, analysis FROM nfl_news WHERE embedding IS NULL;")
rows = cur.fetchall()


batch_size = 128
total = len(rows)

for i in range(0, total, batch_size):
    batch = rows[i:i + batch_size]
    ids = [row[0] for row in batch]
    texts = [f"{notes or ''} {analysis or ''}".strip() for _, notes, analysis in batch]

    try:
        embeddings = model.encode(texts, batch_size=batch_size)

        for row_id, emb in zip(ids, embeddings):
            cur.execute(
                "UPDATE nfl_news SET embedding = %s WHERE id = %s;",
                (emb.tolist(), row_id)
            )

        print(f"✅ Processed {i + len(batch)} / {total} rows")
    except Exception as e:
        print(f"❌ Error on batch {i}-{i+batch_size}: {e}")
        time.sleep(1)


conn.commit()
cur.close()
conn.close()
print("🎉 All embeddings stored successfully!")
