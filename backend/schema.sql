-- schema.sql
-- Initializes the Cloudflare D1 Serverless SQL Database for Nemesis

DROP TABLE IF EXISTS darknet_intel;
CREATE TABLE darknet_intel (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    data TEXT NOT NULL,
    label TEXT NOT NULL,
    score INTEGER NOT NULL DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast text search on darknet_search endpoint
CREATE INDEX idx_darknet_data ON darknet_intel(data);
CREATE INDEX idx_darknet_label ON darknet_intel(label);

-- Insert dummy data (Replacing the MongoDB mock)
INSERT INTO darknet_intel (id, type, data, label, score) VALUES
('XYZ_1', 'WALLET', '0x1A2B3C4D...XYZ', 'Lazarus Group (DPRK)', 98),
('XYZ_2', 'DOMAIN', 'darknetsyndicate.onion', 'Darknet Syndicate', 85),
('XYZ_3', 'IP', '104.21.34.45', 'C2 Infrastructure', 70);

-- Table for Trace Graph Intelligence
DROP TABLE IF EXISTS trace_nodes;
CREATE TABLE trace_nodes (
    address TEXT PRIMARY KEY,
    network TEXT NOT NULL,
    entity_name TEXT,
    risk_score INTEGER DEFAULT 0,
    last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
