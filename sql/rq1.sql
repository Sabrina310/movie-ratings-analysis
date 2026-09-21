SELECT
    m.title AS "title",
    m.startYear AS "startYear",
    m.averageRating AS "averageRating",
    r.audience_score AS "audience_score"
FROM Movies m
JOIN RottenTomatoes r
ON m.title = r.title
AND m.startYear = r.year
WHERE m.startYear BETWEEN 2016 AND 2025;
