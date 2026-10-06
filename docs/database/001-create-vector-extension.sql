-- Enables the pgvector extension used to store and search embeddings (DATA-002).
-- Tables are created and managed by LangChain PGVector.
CREATE EXTENSION IF NOT EXISTS vector;
