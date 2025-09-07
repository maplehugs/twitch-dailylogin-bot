CREATE TABLE IF NOT EXISTS checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    username TEXT,
    image TEXT DEFAULT '/images/mel/image.png',
    checkin_date TEXT,
    checkin_count INTEGER DEFAULT 0,
    UNIQUE(user_id, checkin_date)
);
