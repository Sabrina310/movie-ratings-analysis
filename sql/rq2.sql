SELECT
    m.title AS "title",
    m.startYear AS "startYear",
    m.averageRating AS "averageRating",
    m.numVotes AS "numVotes",
    m.genres AS "genres",
    o.filmid AS "filmid"
FROM Movies m
LEFT JOIN Oscars o
ON m.tconst = o.filmid
WHERE m.startYear BETWEEN 2016 AND 2025;
