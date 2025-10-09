-- Initialize RavensRotoWire Database with pgvector extension

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for organizing tables
CREATE SCHEMA IF NOT EXISTS ravens;

-- Example table for storing embeddings
CREATE TABLE IF NOT EXISTS ravens.document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),  -- Dimension for OpenAI embeddings, adjust as needed
    metadata JSONB,
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS document_embeddings_embedding_idx 
ON ravens.document_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Example table for storing SQL queries and results
CREATE TABLE IF NOT EXISTS ravens.query_history (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    sql_query TEXT NOT NULL,
    result_summary JSONB,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example table for NFL data (customize based on your needs)
CREATE TABLE IF NOT EXISTS ravens.players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    position VARCHAR(50),
    team VARCHAR(100),
    stats JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ravens.games (
    id SERIAL PRIMARY KEY,
    game_date DATE NOT NULL,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    stats JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION ravens.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_document_embeddings_updated_at 
BEFORE UPDATE ON ravens.document_embeddings 
FOR EACH ROW EXECUTE FUNCTION ravens.update_updated_at_column();

CREATE TRIGGER update_players_updated_at 
BEFORE UPDATE ON ravens.players 
FOR EACH ROW EXECUTE FUNCTION ravens.update_updated_at_column();

-- Grant permissions (adjust user as needed)
GRANT USAGE ON SCHEMA ravens TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ravens TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ravens TO postgres;

-- Insert sample data (optional)
INSERT INTO ravens.players (name, position, team, stats) VALUES
('Lamar Jackson', 'QB', 'Baltimore Ravens', '{"passing_yards": 3678, "touchdowns": 24}'),
('Derrick Henry', 'RB', 'Baltimore Ravens', '{"rushing_yards": 1538, "touchdowns": 13}')
ON CONFLICT DO NOTHING;

COMMENT ON TABLE ravens.document_embeddings IS 'Stores document embeddings for semantic search';
COMMENT ON TABLE ravens.query_history IS 'Stores history of text-to-SQL queries';
COMMENT ON TABLE ravens.players IS 'NFL player information and statistics';
COMMENT ON TABLE ravens.games IS 'NFL game results and statistics';
