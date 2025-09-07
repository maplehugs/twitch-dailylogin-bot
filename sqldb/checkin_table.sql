CREATE TABLE IF NOT EXISTS checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    image TEXT DEFAULT '/static/images/mel/image.png',
    checkin_date TEXT,
    checkin_count INTEGER DEFAULT 1,
    UNIQUE(username)
);
