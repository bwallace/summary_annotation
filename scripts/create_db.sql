CREATE TABLE target_summaries (
    uuid INTEGER PRIMARY KEY, 
    cochrane_id TEXT NOT NULL UNIQUE, 
    title TEXT NOT NULL, 
    summary TEXT NOT NULL
);


CREATE TABLE generated_summaries (
    uuid INTEGER PRIMARY KEY AUTOINCREMENT, 
    cochrane_id TEXT NOT NULL, 
    system_id TEXT NOT NULL, 
    summary TEXT NOT NULL
);


CREATE TABLE source_abstract (
    uuid INTEGER PRIMARY KEY AUTOINCREMENT, 
    cochrane_id TEXT NOT NULL,
    title TEXT,
    abstract TEXT
);


CREATE TABLE label (
    uuid INTEGER PRIMARY KEY AUTOINCREMENT, 
    generated_summary_id INTEGER NOT NULL,
    label_type TEXT NOT NULL,
    score INTEGER NOT NULL
);