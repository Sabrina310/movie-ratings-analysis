# Historical coursework script; see archive/README.md before running.
# %%
import oracledb
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# %%
user = input("Enter Oracle username: ")
password = input("Enter Oracle password: ")

conn = oracledb.connect(
    user=user,
    password=password,
    dsn="localhost:1522/stu"
)

# %%
cursor = conn.cursor()

sql_statements = [

# Drop RottenTomatoes
"""
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE RottenTomatoes CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN
            RAISE;
        END IF;
END;
""",

# Drop Oscars
"""
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE Oscars CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN
            RAISE;
        END IF;
END;
""",

# Drop Movies
"""
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE Movies CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN
            RAISE;
        END IF;
END;
""",

# Purge recyclebin
"PURGE RECYCLEBIN",

# Create Movies
"""
CREATE TABLE Movies (
    tconst VARCHAR2(20) PRIMARY KEY,
    title VARCHAR2(300),
    startYear NUMBER NOT NULL,
    genres VARCHAR2(200),
    averageRating NUMBER(3,1) NOT NULL,
    numVotes NUMBER NOT NULL,
    CONSTRAINT uq_movies_title_year UNIQUE (title, startYear)
)
""",

# Create Oscars
"""
CREATE TABLE Oscars (
    filmid VARCHAR2(20) PRIMARY KEY,
    year NUMBER NOT NULL,
    film VARCHAR2(300) NOT NULL,
    CONSTRAINT fk_oscars_filmid
        FOREIGN KEY (filmid) REFERENCES Movies(tconst)
)
""",

# Create RottenTomatoes
"""
CREATE TABLE RottenTomatoes (
    title VARCHAR2(300),
    year NUMBER,
    audience_score NUMBER(3,1) NOT NULL,
    critics_score NUMBER(3,1) NOT NULL,
    CONSTRAINT pk_rottentomatoes PRIMARY KEY (title, year),
    CONSTRAINT fk_rottentomatoes_title_year
        FOREIGN KEY (title, year)
        REFERENCES Movies(title, startYear)
)
"""
]

for stmt in sql_statements:
    cursor.execute(stmt)

conn.commit()
print("Tables dropped and recreated successfully.")

# %%
df_movies = pd.read_csv('clean_movies.csv')
df_oscars = pd.read_csv('clean_oscar.csv')
df_rt = pd.read_csv('clean_rotten_tomatoes.csv')

for _, row in df_movies.iterrows():
    cursor.execute("""
        INSERT INTO Movies (tconst, title, startYear, genres, averageRating, numVotes)
        VALUES (:1, :2, :3, :4, :5, :6)
    """, (
        row["tconst"],
        row["primaryTitle"],
        int(row["startYear"]) if pd.notna(row["startYear"]) else None,
        None if pd.isna(row["genres"]) else str(row["genres"]),
        float(row["averageRating"]) if pd.notna(row["averageRating"]) else None,
        int(row["numVotes"]) if pd.notna(row["numVotes"]) else None
    ))

valid_ids = set(df_movies["tconst"])

for _, row in df_oscars.iterrows():
    if row["FilmId"] not in valid_ids:
        continue

    cursor.execute("""
        INSERT INTO Oscars (year, film, filmId)
        VALUES (:1, :2, :3)
    """, (
        int(row["Year"]) if pd.notna(row["Year"]) else None,
        row["Film"],
        row["FilmId"]
    ))

valid_movie_pairs = set(zip(df_movies["primaryTitle"], df_movies["startYear"]))

for _, row in df_rt.iterrows():

    if (row["title"], row["year"]) not in valid_movie_pairs:
        continue

    cursor.execute("""
        INSERT INTO RottenTomatoes (title, year, audience_score, critics_score)
        VALUES (:1, :2, :3, :4)
    """, (
        row["title"],
        int(row["year"]) if pd.notna(row["year"]) else None,
        float(row["audience_score"]) if pd.notna(row["audience_score"]) else None,
        float(row["critics_score"]) if pd.notna(row["critics_score"]) else None
    ))

conn.commit()
print("All data inserted successfully.")

cursor.close()

# %%
query1 = """
SELECT
    m.title AS "title",
    m.startYear AS "startYear",
    m.averageRating AS "averageRating",
    r.audience_score AS "audience_score"
FROM Movies m
JOIN RottenTomatoes r
ON m.title = r.title
AND m.startYear = r.year
WHERE m.startYear BETWEEN 2016 AND 2025
"""

df1 = pd.read_sql(query1, conn)

# %%
df1["averageRating"] = pd.to_numeric(df1["averageRating"], errors="coerce")
df1["audience_score"] = pd.to_numeric(df1["audience_score"], errors="coerce")

df1 = df1.dropna(subset=["averageRating", "audience_score"])

plt.figure(figsize=(7, 6))
plt.boxplot(
    [df1["audience_score"], df1["averageRating"]],
    tick_labels=["Rotten Tomatoes", "IMDb"]
)

plt.ylabel("Score")
plt.title("Distribution of Rotten Tomatoes and IMDb Scores (2016–2025)")
plt.tight_layout()
plt.savefig("question1.png")
plt.show()

# %%
query2 = """
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
WHERE m.startYear BETWEEN 2016 AND 2025
"""

df2 = pd.read_sql(query2, conn)

# %%
df2["oscar"] = df2["filmid"].notna().astype(int)

plt.figure(figsize=(8, 6))

plt.scatter(
    df2[df2["oscar"] == 0]["numVotes"],
    df2[df2["oscar"] == 0]["averageRating"],
    label="No Oscar",
    alpha=0.6
)

plt.scatter(
    df2[df2["oscar"] == 1]["numVotes"],
    df2[df2["oscar"] == 1]["averageRating"],
    label="Oscar",
    alpha=0.6
)

plt.xlabel("Number of Votes")
plt.ylabel("Average Rating")
plt.title("Average Rating vs Number of Votes (Oscar vs Non-Oscar, 2016–2025)")
plt.legend()
plt.tight_layout()
plt.savefig("question2.png")
plt.show()

# %%
query3 = """
SELECT
    m.title AS "title",
    m.startYear AS "startYear",
    m.numVotes AS "numVotes",
    r.critics_score AS "critics_score"
FROM Movies m
JOIN RottenTomatoes r
    ON m.title = r.title
    AND m.startYear = r.year
WHERE m.startYear BETWEEN 2016 AND 2025
"""

df3 = pd.read_sql(query3, conn)

# %%
df3["numVotes"] = pd.to_numeric(df3["numVotes"], errors="coerce")
df3["critics_score"] = pd.to_numeric(df3["critics_score"], errors="coerce")

df3 = df3.dropna(subset=["numVotes", "critics_score"])
df3 = df3[(df3["numVotes"] > 0) & (df3["critics_score"] >= 0) & (df3["critics_score"] <= 100)]

print(df3.head())
print("Number of matched movies:", len(df3))

corr3 = df3["numVotes"].corr(df3["critics_score"])
print("Pearson correlation:", corr3)

plt.figure(figsize=(8, 6))
plt.scatter(df3["numVotes"], df3["critics_score"], alpha=0.6)

z = np.polyfit(np.log10(df3["numVotes"]), df3["critics_score"], 1)
p = np.poly1d(z)

x_sorted = np.sort(df3["numVotes"])
plt.plot(x_sorted, p(np.log10(x_sorted)), linewidth=2)

plt.xscale("log")
plt.xlabel("IMDb Popularity (Number of User Votes, log scale)")
plt.ylabel("Rotten Tomatoes Critics Score")
plt.title("IMDb Popularity vs Rotten Tomatoes Critics Score (2016–2025)")
plt.tight_layout()
plt.savefig("question3_scatter.png")
plt.show()

# %%
df3["popularity_group"] = pd.qcut(df3["numVotes"], 5, labels=[
    "Very Low", "Low", "Medium", "High", "Very High"
])

plt.figure(figsize=(8,6))
df3.boxplot(column="critics_score", by="popularity_group")

plt.xlabel("IMDb Popularity Group (by numVotes quantiles)")
plt.ylabel("Rotten Tomatoes Critics Score")
plt.title("Critics Score Distribution by IMDb Popularity Level")
plt.suptitle("")

plt.tight_layout()
plt.savefig("question3_boxplot.png")
plt.show()