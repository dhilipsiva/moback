CREATE TABLE Person(
    id                  SERIAL PRIMARY KEY,
    email               VARCHAR(100) UNIQUE,
    firstname           VARCHAR(35),
    lastname            VARCHAR(35),
    username            VARCHAR(30) UNIQUE,
    pw_hash             VARCHAR(100),
    access_token        VARCHAR(36) UNIQUE,
    start_date          TIMESTAMP DEFAULT now(),
    total_score         INTEGER DEFAULT 0
);

CREATE TYPE DIFFICULTY_TYPE AS ENUM('easy', 'medium', 'hard');

CREATE TABLE Point(
    id          VARCHAR(36) PRIMARY KEY,
    person_id   INTEGER REFERENCES Person,
    score       INTEGER DEFAULT 0,
    score_time  TIMESTAMP DEFAULT now()
);

CREATE TABLE Friend(
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES Person,
    friend_id INTEGER REFERENCES Person,
    UNIQUE(person_id, friend_id)
);
