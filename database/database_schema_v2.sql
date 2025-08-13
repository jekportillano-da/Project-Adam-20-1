-- Enhanced Budget Buddy Database Schema
-- Comprehensive user financial management system

-- Core Users Table (Enhanced)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    
    -- Personal Details for Analysis
    age INTEGER,
    civil_status TEXT CHECK(civil_status IN ('single', 'married', 'divorced', 'widowed', 'in_relationship')),
    number_of_dependents INTEGER DEFAULT 0,
    number_of_kids INTEGER DEFAULT 0,
    location TEXT, -- city/region for cost of living analysis
    
    -- Lifestyle & Behavior Analysis
    hobbies TEXT, -- JSON array of hobbies
    free_time_activities TEXT, -- JSON array of activities
    spending_personality TEXT CHECK(spending_personality IN ('saver', 'spender', 'balanced', 'impulsive')),
    financial_goals_priority TEXT CHECK(financial_goals_priority IN ('emergency_fund', 'investments', 'debt_payoff', 'lifestyle')),
    
    -- User Preferences
    preferred_currency TEXT DEFAULT 'PHP',
    timezone TEXT DEFAULT 'Asia/Manila',
    notification_preferences TEXT -- JSON for notification settings
);

-- Multiple Income Sources Table
CREATE TABLE IF NOT EXISTS user_income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    source_name TEXT NOT NULL, -- 'Primary Salary', 'Freelance', 'Side Hustle', etc.
    income_type TEXT NOT NULL CHECK(income_type IN ('salary', 'freelance', 'business', 'investment', 'rental', 'other')),
    amount DECIMAL(12,2) NOT NULL,
    frequency TEXT NOT NULL CHECK(frequency IN ('weekly', 'bi_weekly', 'monthly', 'quarterly', 'annually', 'irregular')),
    is_active BOOLEAN DEFAULT 1,
    start_date DATE,
    end_date DATE, -- for temporary income sources
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Enhanced Bills Table with History Tracking
CREATE TABLE IF NOT EXISTS user_bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bill_name TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('housing', 'utilities', 'insurance', 'subscriptions', 'loans', 'telecommunications', 'transportation', 'other')),
    
    -- Current Bill Details
    current_amount DECIMAL(10,2) NOT NULL,
    due_date_day INTEGER, -- day of month (1-31)
    frequency TEXT NOT NULL CHECK(frequency IN ('weekly', 'monthly', 'quarterly', 'annually')),
    
    -- Bill Management
    is_active BOOLEAN DEFAULT 1,
    is_auto_pay BOOLEAN DEFAULT 0,
    payment_method TEXT, -- 'bank_transfer', 'credit_card', 'cash', etc.
    
    -- Analysis Fields
    priority_level TEXT CHECK(priority_level IN ('essential', 'important', 'optional')) DEFAULT 'important',
    is_fixed_amount BOOLEAN DEFAULT 1, -- false for variable bills like utilities
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Bill Payment History (Track every payment and amount changes)
CREATE TABLE IF NOT EXISTS bill_payment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    
    -- Payment Details
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    due_date DATE,
    
    -- Status Tracking
    status TEXT CHECK(status IN ('paid', 'overdue', 'partial', 'cancelled')) DEFAULT 'paid',
    payment_method TEXT,
    
    -- Analysis Data
    was_amount_different BOOLEAN DEFAULT 0, -- true if amount changed from previous
    previous_amount DECIMAL(10,2), -- for tracking amount changes
    late_fee DECIMAL(10,2) DEFAULT 0,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES user_bills(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Financial Goals (Enhanced from in-memory version)
CREATE TABLE IF NOT EXISTS financial_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    goal_name TEXT NOT NULL,
    description TEXT,
    
    -- Goal Details
    target_amount DECIMAL(12,2) NOT NULL,
    current_amount DECIMAL(12,2) DEFAULT 0,
    target_date DATE NOT NULL,
    
    -- Goal Classification
    category TEXT NOT NULL CHECK(category IN ('emergency_fund', 'vacation', 'house_down_payment', 'car', 'education', 'retirement', 'debt_payoff', 'investment', 'other')),
    priority TEXT NOT NULL CHECK(priority IN ('high', 'medium', 'low')) DEFAULT 'medium',
    
    -- Progress Tracking
    monthly_contribution DECIMAL(10,2) DEFAULT 0,
    auto_transfer BOOLEAN DEFAULT 0,
    
    -- Status
    status TEXT CHECK(status IN ('active', 'completed', 'paused', 'cancelled')) DEFAULT 'active',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Goal Progress Tracking
CREATE TABLE IF NOT EXISTS goal_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    
    -- Progress Entry
    amount_added DECIMAL(10,2) NOT NULL,
    new_total DECIMAL(10,2) NOT NULL,
    entry_date DATE NOT NULL,
    source TEXT, -- 'manual', 'auto_transfer', 'bonus', etc.
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES financial_goals(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Budget Templates & User Budgets
CREATE TABLE IF NOT EXISTS user_budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    budget_name TEXT NOT NULL,
    
    -- Budget Period
    budget_month INTEGER NOT NULL, -- 1-12
    budget_year INTEGER NOT NULL,
    total_income DECIMAL(12,2) NOT NULL,
    
    -- Budget Categories (JSON for flexibility)
    budget_allocations TEXT NOT NULL, -- JSON: {"housing": 15000, "food": 8000, ...}
    actual_spending TEXT, -- JSON: actual amounts spent
    
    -- Budget Status
    is_active BOOLEAN DEFAULT 1,
    is_template BOOLEAN DEFAULT 0, -- true if this is a reusable template
    
    -- Analysis
    variance_analysis TEXT, -- JSON: analysis of budget vs actual
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, budget_month, budget_year)
);

-- Transaction/Expense Tracking
CREATE TABLE IF NOT EXISTS user_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- Transaction Details
    description TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_date DATE NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    
    -- Transaction Type
    transaction_type TEXT CHECK(transaction_type IN ('income', 'expense', 'transfer', 'investment')) NOT NULL,
    payment_method TEXT,
    
    -- Linking
    bill_id INTEGER, -- link to bill if this is a bill payment
    goal_id INTEGER, -- link to goal if this contributes to a goal
    
    -- Analysis Tags
    is_essential BOOLEAN DEFAULT 0,
    is_recurring BOOLEAN DEFAULT 0,
    mood_tag TEXT, -- 'happy', 'stressed', 'planned', 'impulse'
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bill_id) REFERENCES user_bills(id) ON DELETE SET NULL,
    FOREIGN KEY (goal_id) REFERENCES financial_goals(id) ON DELETE SET NULL
);

-- AI Analysis & Insights Cache
CREATE TABLE IF NOT EXISTS ai_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- Insight Details
    insight_type TEXT NOT NULL CHECK(insight_type IN ('spending_analysis', 'budget_recommendation', 'goal_progress', 'bill_optimization', 'income_opportunity')),
    insight_title TEXT NOT NULL,
    insight_content TEXT NOT NULL,
    
    -- Analysis Data
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    data_period_start DATE,
    data_period_end DATE,
    
    -- User Interaction
    is_read BOOLEAN DEFAULT 0,
    is_dismissed BOOLEAN DEFAULT 0,
    user_rating INTEGER CHECK(user_rating BETWEEN 1 AND 5), -- user feedback on insight quality
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- some insights may expire
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User Financial Profile (Computed/Analysis Table)
CREATE TABLE IF NOT EXISTS user_financial_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    
    -- Computed Financial Metrics
    monthly_income_avg DECIMAL(12,2),
    monthly_expenses_avg DECIMAL(12,2),
    monthly_savings_avg DECIMAL(12,2),
    savings_rate DECIMAL(5,2), -- percentage
    
    -- Risk & Behavior Profile
    spending_volatility DECIMAL(5,2), -- standard deviation of spending
    financial_health_score INTEGER CHECK(financial_health_score BETWEEN 0 AND 100),
    emergency_fund_months DECIMAL(4,2),
    debt_to_income_ratio DECIMAL(5,2),
    
    -- Behavior Analysis
    primary_spending_categories TEXT, -- JSON array of top spending categories
    spending_patterns TEXT, -- JSON: analysis of spending timing, frequency
    financial_stress_indicators TEXT, -- JSON: late payments, overdrafts, etc.
    
    -- Goals Achievement
    goals_completion_rate DECIMAL(5,2),
    avg_goal_achievement_time INTEGER, -- days
    
    -- Last Analysis
    last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calculation_data_range_days INTEGER DEFAULT 90,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_user_income_user_id ON user_income(user_id);
CREATE INDEX IF NOT EXISTS idx_user_bills_user_id ON user_bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bill_history_bill_id ON bill_payment_history(bill_id);
CREATE INDEX IF NOT EXISTS idx_bill_history_user_id ON bill_payment_history(user_id);
CREATE INDEX IF NOT EXISTS idx_financial_goals_user_id ON financial_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goal_progress_goal_id ON goal_progress(goal_id);
CREATE INDEX IF NOT EXISTS idx_user_budgets_user_id ON user_budgets(user_id);
CREATE INDEX IF NOT EXISTS idx_user_transactions_user_id ON user_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_transactions_date ON user_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_ai_insights_user_id ON ai_insights(user_id);

-- Views for Common Queries
CREATE VIEW IF NOT EXISTS user_active_income AS
SELECT 
    ui.*,
    CASE ui.frequency
        WHEN 'weekly' THEN ui.amount * 52 / 12
        WHEN 'bi_weekly' THEN ui.amount * 26 / 12
        WHEN 'monthly' THEN ui.amount
        WHEN 'quarterly' THEN ui.amount / 3
        WHEN 'annually' THEN ui.amount / 12
        ELSE ui.amount
    END as monthly_equivalent
FROM user_income ui
WHERE ui.is_active = 1;

CREATE VIEW IF NOT EXISTS user_active_bills AS
SELECT 
    ub.*,
    CASE ub.frequency
        WHEN 'weekly' THEN ub.current_amount * 52 / 12
        WHEN 'monthly' THEN ub.current_amount
        WHEN 'quarterly' THEN ub.current_amount / 3
        WHEN 'annually' THEN ub.current_amount / 12
        ELSE ub.current_amount
    END as monthly_equivalent
FROM user_bills ub
WHERE ub.is_active = 1;

CREATE VIEW IF NOT EXISTS user_financial_summary AS
SELECT 
    u.id as user_id,
    u.email,
    u.name,
    COALESCE(income_total.monthly_income, 0) as total_monthly_income,
    COALESCE(bills_total.monthly_bills, 0) as total_monthly_bills,
    COALESCE(income_total.monthly_income, 0) - COALESCE(bills_total.monthly_bills, 0) as monthly_surplus,
    goals_summary.active_goals_count,
    goals_summary.total_goal_target,
    goals_summary.total_goal_current
FROM users u
LEFT JOIN (
    SELECT user_id, SUM(monthly_equivalent) as monthly_income
    FROM user_active_income
    GROUP BY user_id
) income_total ON u.id = income_total.user_id
LEFT JOIN (
    SELECT user_id, SUM(monthly_equivalent) as monthly_bills
    FROM user_active_bills
    GROUP BY user_id
) bills_total ON u.id = bills_total.user_id
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as active_goals_count,
        SUM(target_amount) as total_goal_target,
        SUM(current_amount) as total_goal_current
    FROM financial_goals
    WHERE status = 'active'
    GROUP BY user_id
) goals_summary ON u.id = goals_summary.user_id;
