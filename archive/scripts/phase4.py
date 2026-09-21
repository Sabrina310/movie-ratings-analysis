# Historical coursework script; see archive/README.md before running.
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pymongo import MongoClient

client = MongoClient(
    "mongodb://localhost:27017/"
)

db = client["movie_analysis"]

collection = db["merged_movies"]

print("Connected and inserted!")

## Query 1: Retrieve movies released between 2016 and 2025 with both IMDb ratings and Rotten Tomatoes audience scores
pipeline1 = [
    {
        "$match": {
            "year": {"$gte": 2016, "$lte": 2025},
            "imdb.rating": {"$exists": True},
            "rotten.ratings.audience": {"$exists": True}
        }
    },
    {
        "$project": {
            "_id": 0,
            "title": 1,
            "year": 1,
            "averageRating": "$imdb.rating",
            "audience_score": "$rotten.ratings.audience"
        }
    }
]

## Execute the aggregation pipeline and convert the results to a DataFrame
df1 = pd.DataFrame(list(collection.aggregate(pipeline1)))

print(df1.head())
print("Number of records:", len(df1))

## Create a hexbin plot to visualize the density of movies based on their IMDb ratings and Rotten Tomatoes audience scores
plt.figure(figsize=(8, 6))
hb = plt.hexbin(df1["averageRating"], df1["audience_score"], gridsize=25, mincnt=1)
plt.colorbar(hb, label="Number of movies")
plt.xlabel("IMDb Rating")
plt.ylabel("Rotten Tomatoes Audience Score")
plt.title("RQ1: Density of IMDb Ratings vs Rotten Tomatoes Audience Scores (2016–2025)")
plt.tight_layout()
plt.show()

## Query 2: Group movies by genre, popularity (based on IMDb votes), and Oscar recognition, then calculate the average IMDb rating for each group

pipeline2 = [
    {
        "$match": {
            "year": {"$gte": 2016, "$lte": 2025},
            "imdb.rating": {"$exists": True},
            "imdb.votes": {"$exists": True},
            "genres": {"$exists": True},
            "oscar": {"$exists": True}
        }
    },
    {
        "$unwind": "$genres"
    },
    {
        "$addFields": {
            "popularity_bin": {
                "$switch": {
                    "branches": [
                        {
                            "case": {"$lt": ["$imdb.votes", 10000]},
                            "then": "1K-10K"
                        },
                        {
                            "case": {"$lt": ["$imdb.votes", 100000]},
                            "then": "10K-100K"
                        },
                        {
                            "case": {"$lt": ["$imdb.votes", 1000000]},
                            "then": "100K-1M"
                        }
                    ],
                    "default": "1M+"
                }
            },
            "oscar_group": {
                "$cond": {
                    "if": "$oscar",
                    "then": "Oscar",
                    "else": "No Oscar"
                }
            }
        }
    },
    {
        "$group": {
            "_id": {
                "genre": "$genres",
                "popularity_bin": "$popularity_bin",
                "oscar_group": "$oscar_group"
            },
            "avg_imdb_rating": {"$avg": "$imdb.rating"},
            "movie_count": {"$sum": 1}
        }
    },
    {
        "$project": {
            "_id": 0,
            "genre": "$_id.genre",
            "popularity_bin": "$_id.popularity_bin",
            "oscar_group": "$_id.oscar_group",
            "avg_imdb_rating": 1,
            "movie_count": 1
        }
    },
    {
        "$sort": {
            "genre": 1,
            "popularity_bin": 1,
            "oscar_group": 1
        }
    }
]

## Execute the aggregation pipeline and convert the results to a DataFrame
df2 = pd.DataFrame(list(collection.aggregate(pipeline2)))
print(df2.head())
print("Number of records:", len(df2))

## Create line plots to show the average IMDb rating for Oscar-winning vs non-Oscar-winning movies across different popularity bins for the top 4 genres
top_genres = (
    df2.groupby("genre")["movie_count"]
    .sum()
    .sort_values(ascending=False)
    .head(4)
    .index
)

for genre_to_plot in top_genres:
    plot_df = df2[df2["genre"] == genre_to_plot].copy()

    bin_order = ["1K-10K", "10K-100K", "100K-1M", "1M+"]
    plot_df["popularity_bin"] = pd.Categorical(
        plot_df["popularity_bin"],
        categories=bin_order,
        ordered=True
    )
    plot_df = plot_df.sort_values("popularity_bin")

    pivot_df = plot_df.pivot(
        index="popularity_bin",
        columns="oscar_group",
        values="avg_imdb_rating"
    )

    plt.figure(figsize=(8, 6))
    if "No Oscar" in pivot_df.columns:
        plt.plot(pivot_df.index.astype(str), pivot_df["No Oscar"], marker="o", label="No Oscar")
    if "Oscar" in pivot_df.columns:
        plt.plot(pivot_df.index.astype(str), pivot_df["Oscar"], marker="o", label="Oscar")

    plt.xlabel("Popularity Bin")
    plt.ylabel("Average IMDb Rating")
    plt.title(f"RQ2: Average IMDb Rating by Popularity Bin ({genre_to_plot})")
    plt.legend()
    plt.tight_layout()
    plt.show()

    ## Query 3: Retrieve movies released between 2016 and 2025 with number of votes and Rotten Tomatoes critics scores
pipeline3 = [
    {
        "$match": {
            "year": {"$gte": 2016, "$lte": 2025},
            "imdb.votes": {"$exists": True},
            "rotten.ratings.critics": {"$exists": True}
        }
    },
    {
        "$project": {
            "_id": 0,
            "title": 1,
            "year": 1,
            "numVotes": "$imdb.votes",
            "critics_score": "$rotten.ratings.critics"
        }
    }
]

## Execute the aggregation pipeline and convert the results to a DataFrame
df3 = pd.DataFrame(list(collection.aggregate(pipeline3)))
print(df3.head())
print("Number of records:", len(df3))

## Create a line plot to show the average Rotten Tomatoes critics score for movies in different bins of IMDb popularity (number of votes)
bins = np.logspace(3, 7, 9)
labels = ["10^3-10^3.5", "10^3.5-10^4", "10^4-10^4.5", "10^4.5+10^5", "10^5-10^5.5", "10^5.5-10^6", "10^6-10^6.5", "10^6.5+10^7"]

df3["vote_bin"] = pd.cut(df3["numVotes"], bins=bins, labels=labels, right=False)

mean_scores = df3.groupby("vote_bin")["critics_score"].mean()

plt.figure(figsize=(8, 6))
plt.plot(mean_scores.index.astype(str), mean_scores.values, marker="o")
plt.xlabel("IMDb Vote Bin")
plt.ylabel("Average Rotten Tomatoes Critics Score")
plt.title("RQ3: Average Critics Score by IMDb Popularity Bin (2016–2025)")
plt.tight_layout()
plt.xticks(rotation=30, ha='right', fontsize=10)
plt.show()