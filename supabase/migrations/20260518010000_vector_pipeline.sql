-- Phase 0.3: Vector Database Pipeline
-- pgvector embedding store, chunk store, search index

-- Enable pgvector extension (requires pgvector/pgvector:pg16 image)
CREATE EXTENSION IF NOT EXISTS vector;

-- Embedding store: stores vector embeddings for documents/chunks
CREATE TABLE IF NOT EXISTS embedding_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    content TEXT NOT NULL,
    embedding vector(1536),
    token_estimate INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT embedding_store_source_chunk_unique UNIQUE (source_id, chunk_index)
);

-- Chunk store: stores raw text chunks before embedding
CREATE TABLE IF NOT EXISTS chunk_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    content TEXT NOT NULL,
    chunk_size INTEGER NOT NULL DEFAULT 0,
    chunk_overlap INTEGER NOT NULL DEFAULT 50,
    embedding_status TEXT DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chunk_store_source_chunk_unique UNIQUE (source_id, chunk_index)
);

-- Search index: tracks which documents are indexed and searchable
CREATE TABLE IF NOT EXISTS search_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT NOT NULL UNIQUE,
    document_type TEXT NOT NULL DEFAULT 'note',
    total_chunks INTEGER DEFAULT 0,
    indexed_at TIMESTAMPTZ,
    last_searched_at TIMESTAMPTZ,
    search_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_embedding_store_source ON embedding_store(source_id);
CREATE INDEX IF NOT EXISTS idx_chunk_store_source ON chunk_store(source_id);
CREATE INDEX IF NOT EXISTS idx_chunk_store_status ON chunk_store(embedding_status);
CREATE INDEX IF NOT EXISTS idx_search_index_type ON search_index(document_type);

-- HNSW index for vector similarity search (pgvector 0.5+)
CREATE INDEX IF NOT EXISTS idx_embedding_store_vector
    ON embedding_store
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- RLS policies
ALTER TABLE embedding_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunk_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_index ENABLE ROW LEVEL SECURITY;

-- Users can only access their own embeddings/chunks
CREATE POLICY "Users can view own embeddings"
    ON embedding_store FOR SELECT
    USING (source_id IN (
        SELECT id FROM notes WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can insert own embeddings"
    ON embedding_store FOR INSERT
    WITH CHECK (source_id IN (
        SELECT id FROM notes WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can delete own embeddings"
    ON embedding_store FOR DELETE
    USING (source_id IN (
        SELECT id FROM notes WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own chunks"
    ON chunk_store FOR SELECT
    USING (source_id IN (
        SELECT id FROM notes WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can insert own chunks"
    ON chunk_store FOR INSERT
    WITH CHECK (source_id IN (
        SELECT id FROM notes WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own search index"
    ON search_index FOR SELECT
    USING (source_id IN (
        SELECT id FROM notes WHERE user_id = auth.uid()
    ));

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_embedding_store_updated_at
    BEFORE UPDATE ON embedding_store
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_search_index_updated_at
    BEFORE UPDATE ON search_index
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Increment search count trigger
CREATE OR REPLACE FUNCTION increment_search_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE search_index
    SET search_count = search_count + 1,
        last_searched_at = NOW()
    WHERE source_id = NEW.source_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
