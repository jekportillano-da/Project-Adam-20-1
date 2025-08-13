-- Future database schema for storing budget tips and user data

-- Tips table for storing generated budget advice
CREATE TABLE IF NOT EXISTS tips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_amount DECIMAL(10,2) NOT NULL,
    duration VARCHAR(10) NOT NULL,  -- daily, weekly, monthly
    daily_equivalent DECIMAL(10,2) NOT NULL,
    tip_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),  -- For rate limiting
    user_agent TEXT,        -- For analytics
    response_time INTEGER   -- API response time in ms
);

-- User feedback table for collecting tip ratings
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tip_id INTEGER NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tip_id) REFERENCES tips (id)
);

-- Future user authentication table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Index for querying tips by date range
CREATE INDEX IF NOT EXISTS idx_tips_created_at ON tips(created_at);

-- Index for user authentication
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
