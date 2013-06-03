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

CREATE UNIQUE INDEX idx_person_email ON Person(email);

CREATE UNIQUE INDEX idx_person_username ON Person(username);

CREATE UNIQUE INDEX idx_person_access_token ON Person(access_token);

CREATE TABLE Score(
    id              VARCHAR(36) PRIMARY KEY,
    person_id       INTEGER REFERENCES Person,
    score_count     INTEGER DEFAULT 0,
    score_time      TIMESTAMP DEFAULT now()
);

CREATE UNIQUE INDEX idx_score_id ON Score(id);

CREATE INDEX idx_score_person_id ON Score(person_id);

CREATE INDEX idx_score_score_time ON Score(score_time);

CREATE OR REPLACE FUNCTION total_score_func() RETURNS TRIGGER AS $score_added$
    BEGIN
        UPDATE person SET total_score = total_score + NEW.score_count WHERE id = NEW.person_id;
        RETURN NEW;
    END;
$score_added$ LANGUAGE plpgsql;

CREATE TRIGGER total_score_trigger
AFTER INSERT ON Score
    FOR EACH ROW
    EXECUTE PROCEDURE total_score_func();
