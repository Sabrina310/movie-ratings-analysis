-- Drop Movies table if it exists
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE Movies CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN
            RAISE;
        END IF;
END;
/

-- Purge recyclebin
PURGE RECYCLEBIN;

-- Create Movies table
CREATE TABLE Movies (
    tconst VARCHAR2(20) PRIMARY KEY,
    title VARCHAR2(300),
    startYear NUMBER NOT NULL,
    genres VARCHAR2(200),
    averageRating NUMBER(3,1) NOT NULL,
    numVotes NUMBER NOT NULL,
    CONSTRAINT uq_movies_title_year UNIQUE (title, startYear)
);

-- Create Oscars table
CREATE TABLE Oscars (
    filmid VARCHAR2(20) PRIMARY KEY,
    year NUMBER NOT NULL,
    film VARCHAR2(300) NOT NULL,
    CONSTRAINT fk_oscars_filmid
        FOREIGN KEY (filmid) REFERENCES Movies(tconst)
);

-- Create RottenTomatoes table
CREATE TABLE RottenTomatoes (
    title VARCHAR2(300),
    year NUMBER,
    audience_score NUMBER(3,1) NOT NULL,
    critics_score NUMBER(3,1) NOT NULL,
    CONSTRAINT pk_rottentomatoes PRIMARY KEY (title, year),
    CONSTRAINT fk_rottentomatoes_title_year
        FOREIGN KEY (title, year)
        REFERENCES Movies(title, startYear)
);