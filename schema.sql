-- search-laboratory: 大学×授業内容×研究テーマの横断比較データ基盤
-- JSON 列（keywords, instructor_names, research_keywords）は JSON 文字列として保存する。
-- AI 抽出列（Course.keywords 等）は原文列（Course.summary 等）と分離し、混ぜない。

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS University (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    type        TEXT NOT NULL,              -- '国立' / '公立' / '私立'
    prefecture  TEXT,
    url         TEXT
);

CREATE TABLE IF NOT EXISTS Department (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id  INTEGER NOT NULL REFERENCES University(id),
    faculty        TEXT,                    -- 学部・学群など上位組織名
    name           TEXT NOT NULL,           -- 学科・学類など
    url            TEXT
);

CREATE TABLE IF NOT EXISTS Course (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id     INTEGER NOT NULL REFERENCES Department(id),
    name              TEXT NOT NULL,
    year              INTEGER,              -- 開講年度
    required          INTEGER,              -- 必修=1 / 選択=0 / 不明=NULL
    summary           TEXT,                 -- 原文（シラバスの科目概要をそのまま）
    keywords          TEXT,                 -- AI抽出（JSON配列）。原文とは別列
    instructor_names  TEXT,                 -- JSON配列
    source_url        TEXT NOT NULL,
    fetched_at        TEXT NOT NULL         -- ISO 8601
);

CREATE TABLE IF NOT EXISTS Faculty (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id      INTEGER NOT NULL REFERENCES Department(id),
    name               TEXT NOT NULL,
    title              TEXT,                -- 職位（教授・准教授など）
    research_keywords  TEXT,                -- JSON配列（公開情報由来。出典は source_url）
    researchmap_url    TEXT,
    lab_url            TEXT,
    source_url         TEXT NOT NULL,
    fetched_at         TEXT NOT NULL        -- ISO 8601
);

CREATE INDEX IF NOT EXISTS idx_department_university ON Department(university_id);
CREATE INDEX IF NOT EXISTS idx_course_department     ON Course(department_id);
CREATE INDEX IF NOT EXISTS idx_faculty_department    ON Faculty(department_id);
CREATE INDEX IF NOT EXISTS idx_course_name           ON Course(name);
CREATE INDEX IF NOT EXISTS idx_faculty_name          ON Faculty(name);
