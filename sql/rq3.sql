SELECT
    m.title AS "title",
    m.startYear AS "startYear",
    m.numVotes AS "numVotes",
    r.critics_score AS "critics_score"
FROM Movies m
JOIN RottenTomatoes r
    ON m.title = r.title
    AND m.startYear = r.year
WHERE m.startYear BETWEEN 2016 AND 2025;
