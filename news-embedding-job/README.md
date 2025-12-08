# News Embedding Job

This project is designed to embed news articles using the SentenceTransformer model. It connects to a PostgreSQL database, retrieves articles that do not have embeddings, processes them in batches, and updates the database with the generated embeddings.

## Project Structure

```
news-embedding-job
├── src
│   └── embed_news.py      # Main logic for embedding news articles
├── Dockerfile              # Dockerfile to build the image
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Requirements

- Docker
- PostgreSQL database

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd news-embedding-job
   ```

2. **Build the Docker image:**

   ```bash
   docker build -t news-embedding-job .
   ```

3. **Run the Docker container:**

   Make sure to set the necessary environment variables for database connection:

   ```bash
   docker run -e DB_NAME=<your_db_name> \
              -e DB_USER=<your_db_user> \
              -e DB_PASSWORD=<your_db_password> \
              -e DB_HOST=<your_db_host> \
              -e DB_PORT=<your_db_port> \
              news-embedding-job
   ```

## Usage

The script `src/embed_news.py` will automatically connect to the specified PostgreSQL database, retrieve news articles without embeddings, generate embeddings using the SentenceTransformer model, and update the database with the new embeddings.

## License

This project is licensed under the MIT License.