"""Produce portable tables, figures, and descriptive statistics."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .data import ROOT, load_inputs, sqlite_queries, movie_documents

BIN_LABELS = ['2K-10K', '10K-100K', '100K-1M', '1M+']


def genre_summary(frame):
    frame = frame.copy()
    frame['oscar_group'] = np.where(frame.filmid.notna(), 'Oscar record', 'No matching record')
    frame['popularity_bin'] = pd.cut(frame.numVotes, [2000, 10000, 100000, 1000000, np.inf],
                                     labels=BIN_LABELS, right=False)
    frame['genre'] = frame.genres.str.split(',')
    return (frame.explode('genre').groupby(['genre', 'popularity_bin', 'oscar_group'], observed=True)
            .agg(avg_imdb_rating=('averageRating', 'mean'), movie_count=('title', 'size'))
            .reset_index())


def run(data_dir=None, output=None):
    output = Path(output) if output else ROOT / 'reports'
    figures, tables = output / 'figures', output / 'results'
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    inputs = load_inputs(data_dir)
    q1, q2, q3 = sqlite_queries(inputs)
    grouped = genre_summary(q2)
    for i, frame in enumerate([q1, q2, q3], 1):
        frame.to_csv(tables / f'rq{i}.csv', index=False)
    grouped.to_csv(tables / 'rq2_genre_popularity.csv', index=False)
    plt.rcParams.update({'figure.dpi': 130, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.titlepad': 14})

    def save(name):
        plt.tight_layout()
        plt.savefig(figures / name, bbox_inches='tight')
        plt.close()

    plt.figure(figsize=(8, 5))
    plt.boxplot([q1.audience_score, q1.averageRating], tick_labels=['RT audience', 'IMDb'])
    plt.ylabel('Score (0–10; RT percentage divided by 10)')
    plt.title(f'RQ1 · Audience score distributions · n={len(q1):,}')
    save('rq1_distributions.png')
    plt.figure(figsize=(8, 5))
    plt.hexbin(q1.averageRating, q1.audience_score, gridsize=25, mincnt=1, cmap='viridis')
    plt.colorbar(label='Number of films')
    plt.xlabel('IMDb rating (0–10)')
    plt.ylabel('RT audience score (0–10, rescaled)')
    plt.title(f'RQ1 · Ratings across platforms · n={len(q1):,}')
    save('rq1_ratings.png')
    plt.figure(figsize=(8, 5))
    for flag, label, color in [(False, 'No matching Oscar record', '#94a3b8'),
                                (True, 'Matching Oscar record', '#d97706')]:
        rows = q2[q2.filmid.notna() == flag]
        plt.scatter(rows.numVotes, rows.averageRating, s=12, alpha=.5, label=f'{label} (n={len(rows):,})', color=color)
    plt.xscale('log')
    plt.xlabel('IMDb votes (log scale)')
    plt.ylabel('IMDb rating (0–10)')
    plt.title('RQ2 · Ratings, popularity and Oscar recognition')
    plt.legend(fontsize=8)
    save('rq2_oscar.png')
    top_genres = grouped.groupby('genre').movie_count.sum().nlargest(4).index
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharey=True)
    for ax, genre in zip(axes.flat, top_genres):
        subset = grouped[grouped.genre == genre]
        for label, color in [('No matching record', '#64748b'), ('Oscar record', '#d97706')]:
            rows = subset[subset.oscar_group == label].set_index('popularity_bin').reindex(BIN_LABELS)
            ax.plot(BIN_LABELS, rows.avg_imdb_rating, marker='o', label=label, color=color)
        ax.set_title(genre)
        ax.set_ylabel('Mean IMDb rating')
        ax.set_xlabel('IMDb vote bin')
    axes[0, 0].legend(fontsize=8)
    fig.suptitle('RQ2 · Descriptive comparisons within genre and vote bins', y=1.02)
    save('rq2_genre_popularity.png')
    plt.figure(figsize=(8, 5))
    plt.scatter(q3.numVotes, q3.critics_score, s=14, alpha=.4, color='#0f766e')
    x = np.sort(q3.numVotes.to_numpy())
    trend = np.poly1d(np.polyfit(np.log10(q3.numVotes), q3.critics_score, 1))
    plt.plot(x, trend(np.log10(x)), color='#d97706', label='Trend fitted against log10(votes)')
    plt.xscale('log')
    plt.xlabel('IMDb votes (log scale)')
    plt.ylabel('RT critics score (0–10, rescaled)')
    plt.title(f'RQ3 · Popularity and critic scores · n={len(q3):,}')
    plt.legend(fontsize=8)
    save('rq3_critics.png')
    q3['popularity_group'] = pd.qcut(q3.numVotes, 5, labels=['Very low', 'Low', 'Medium', 'High', 'Very high'])
    fig, ax = plt.subplots(figsize=(8, 5))
    q3.boxplot(column='critics_score', by='popularity_group', ax=ax)
    ax.set_xlabel('IMDb vote quintile')
    ax.set_ylabel('RT critics score (0–10, rescaled)')
    ax.set_title('RQ3 · Critic score distribution by popularity')
    fig.suptitle('')
    save('rq3_quintiles.png')
    q3['vote_bin'] = pd.cut(q3.numVotes, np.logspace(3, 7, 9), right=False)
    binned = q3.groupby('vote_bin', observed=True).agg(mean_critics=('critics_score', 'mean'), movie_count=('title', 'size'))
    binned.to_csv(tables / 'rq3_vote_bins.csv')
    plt.figure(figsize=(10, 5))
    def compact_votes(value):
        divisor, suffix = (1_000_000, 'M') if value >= 1_000_000 else (1000, 'K')
        scaled = value / divisor
        return (f'{scaled:.0f}' if scaled >= 10 else f'{scaled:.1f}'.rstrip('0').rstrip('.')) + suffix
    bin_labels = [f'{compact_votes(interval.left)}–{compact_votes(interval.right)}\n(n={count})'
                  for interval, count in zip(binned.index, binned.movie_count)]
    plt.plot(bin_labels, binned.mean_critics, marker='o', color='#0f766e')
    plt.xticks(fontsize=8)
    plt.xlabel('IMDb vote bin')
    plt.ylabel('Mean RT critics score (0–10, rescaled)')
    plt.title('RQ3 · Mean critic scores by popularity bin')
    save('rq3_vote_bins.png')
    movies, oscars, rotten = inputs
    summary = {
        'input_rows': {'movies': len(movies), 'oscars': len(oscars), 'rotten_tomatoes': len(rotten)},
        'exact_matched_rt_rows': len(q1), 'matched_oscar_films': int(q2.filmid.notna().sum()),
        'unmatched_oscar_rows': int((~oscars.FilmId.isin(movies.tconst)).sum()),
        'oscar_year_range': [int(oscars.Year.min()), int(oscars.Year.max())],
        'rt_duplicate_title_year_extra_rows': int(rotten.duplicated(['title', 'year']).sum()),
        'audience_rating_pearson_r': float(q1.averageRating.corr(q1.audience_score)),
        'votes_critics_pearson_r': float(q3.numVotes.corr(q3.critics_score)),
        'log10_votes_critics_pearson_r': float(np.log10(q3.numVotes).corr(q3.critics_score)),
        'mean_imdb_with_oscar_record': float(q2.loc[q2.filmid.notna(), 'averageRating'].mean()),
        'mean_imdb_without_oscar_record': float(q2.loc[q2.filmid.isna(), 'averageRating'].mean()),
        'interpretation': 'Descriptive associations only; Oscar membership is not winner status. RT scores are rescaled percentages, not the same metric as IMDb.'
    }
    (tables / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    with (tables / 'merged_movies.jsonl').open('w', encoding='utf-8') as stream:
        for doc in movie_documents(inputs):
            stream.write(json.dumps(doc, ensure_ascii=False, allow_nan=False) + '\n')
    print(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    run(args.data_dir, args.output)


if __name__ == '__main__':
    main()
