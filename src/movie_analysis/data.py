"""Validate the saved cleaned snapshots and reproduce the original join rules."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def load_inputs(directory=None):
    directory = Path(directory) if directory else ROOT / 'data/input'
    frames = [pd.read_csv(directory / f'clean_{name}.csv')
              for name in ['movies', 'oscar', 'rotten_tomatoes']]
    required = [
        ['tconst', 'primaryTitle', 'startYear', 'genres', 'averageRating', 'numVotes'],
        ['Category', 'Year', 'Film', 'FilmId'],
        ['title', 'year', 'audience_score', 'critics_score'],
    ]
    for frame, columns in zip(frames, required):
        missing = set(columns) - set(frame.columns)
        if missing:
            raise ValueError(f'Missing columns: {sorted(missing)}')
        if frame[columns].isna().any().any():
            raise ValueError('Required input fields contain missing values.')
    movies, oscars, rotten = frames
    for frame, column in [(movies, 'startYear'), (movies, 'numVotes'), (movies, 'averageRating'),
                          (oscars, 'Year'), (rotten, 'year'), (rotten, 'audience_score'),
                          (rotten, 'critics_score')]:
        frame[column] = pd.to_numeric(frame[column], errors='raise')
    for frame, column in [(movies, 'startYear'), (movies, 'numVotes'),
                          (oscars, 'Year'), (rotten, 'year')]:
        if not (frame[column] % 1 == 0).all():
            raise ValueError(f'{column} must contain integers.')
    if movies.tconst.duplicated().any() or movies.duplicated(['primaryTitle', 'startYear']).any():
        raise ValueError('Movie keys must be unique.')
    if oscars.FilmId.duplicated().any():
        raise ValueError('Oscar FilmId must be unique in this film-level snapshot.')
    if not movies.startYear.between(2016, 2025).all() or not rotten.year.between(2016, 2025).all():
        raise ValueError('Movie years must be in 2016–2025.')
    if not (movies.numVotes >= 2000).all():
        raise ValueError('The source snapshot requires at least 2,000 votes.')
    for values in [movies.averageRating, rotten.audience_score, rotten.critics_score]:
        if not values.between(0, 10).all():
            raise ValueError('Scores must already be normalized to 0–10; do not divide again.')
    return movies, oscars, rotten


def relational_inputs(movies, oscars, rotten):
    """Keep all IMDb films; retain only valid foreign keys in dependent tables."""
    valid_oscars = oscars[oscars.FilmId.isin(movies.tconst)].copy()
    valid_rotten = rotten.merge(movies[['primaryTitle', 'startYear']],
                               left_on=['title', 'year'], right_on=['primaryTitle', 'startYear'],
                               validate='many_to_one')[rotten.columns]
    if valid_rotten.duplicated(['title', 'year']).any():
        raise ValueError('Matched RT keys are ambiguous; resolve duplicate title/year rows first.')
    return movies, valid_oscars, valid_rotten


def sqlite_queries(inputs):
    """Use an in-memory database so reruns never delete a user database."""
    movies, oscars, rotten = relational_inputs(*inputs)
    with sqlite3.connect(':memory:') as conn:
        movies.rename(columns={'primaryTitle': 'title'}).to_sql('Movies', conn, index=False)
        oscars[['FilmId', 'Year', 'Film']].to_sql('Oscars', conn, index=False)
        rotten.to_sql('RottenTomatoes', conn, index=False)
        return [pd.read_sql_query((ROOT / f'sql/rq{i}.sql').read_text(encoding='utf-8'), conn)
                for i in range(1, 4)]


def movie_documents(inputs):
    movies, oscars, rotten = relational_inputs(*inputs)
    recognized = set(oscars.FilmId)
    scores = {(r.title, r.year): r for r in rotten.itertuples()}
    for row in movies.itertuples():
        doc = {'_id': row.tconst, 'tconst': row.tconst, 'title': row.primaryTitle,
               'year': int(row.startYear), 'genres': row.genres.split(','),
               'imdb': {'rating': float(row.averageRating), 'votes': int(row.numVotes)},
               'oscar': row.tconst in recognized}
        score = scores.get((row.primaryTitle, row.startYear))
        if score is not None:
            doc['rotten'] = {'title': score.title, 'year': int(score.year),
                             'ratings': {'audience': float(score.audience_score),
                                         'critics': float(score.critics_score)}}
        yield doc
