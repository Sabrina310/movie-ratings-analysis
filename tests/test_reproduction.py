"""Check join semantics, loss reporting, document shape and historical matching."""
from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from movie_analysis.data import ROOT, load_inputs, relational_inputs, sqlite_queries, movie_documents
from movie_analysis.analysis import genre_summary


class ReproductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_inputs()
        cls.queries = sqlite_queries(cls.inputs)

    def test_sql_joins_agree_with_independent_dataframe_join(self):
        movies, oscars, rotten = self.inputs
        q1, q2, q3 = self.queries
        expected = movies.merge(rotten, left_on=['primaryTitle', 'startYear'], right_on=['title', 'year'])
        columns = ['title', 'startYear', 'averageRating', 'audience_score']
        pd.testing.assert_frame_equal(q1.sort_values('title').reset_index(drop=True),
                                      expected[columns].sort_values('title').reset_index(drop=True), check_dtype=False)
        self.assertEqual(len(q1), 787)
        self.assertEqual(len(q2), 10147)
        self.assertEqual(q2.filmid.notna().sum(), 348)
        self.assertAlmostEqual(q3.numVotes.corr(q3.critics_score), 0.14248524162571796)

    def test_documents_preserve_unmatched_movies_and_nested_scores(self):
        docs = list(movie_documents(self.inputs))
        self.assertEqual(len({d['_id'] for d in docs}), 10147)
        self.assertEqual(sum('rotten' in d for d in docs), 787)
        self.assertEqual(sum(d['oscar'] for d in docs), 348)
        self.assertTrue(all(isinstance(d['genres'], list) for d in docs))

    def test_genre_counts_include_each_movie_once_per_genre(self):
        q2 = self.queries[1]
        grouped = genre_summary(q2)
        self.assertEqual(grouped.movie_count.sum(), q2.genres.str.split(',').str.len().sum())
        self.assertEqual(len(grouped), 125)

    def test_ambiguous_matched_rt_rows_are_rejected(self):
        movies, oscars, rotten = self.inputs
        matched = relational_inputs(*self.inputs)[2]
        duplicated = pd.concat([rotten, matched.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            relational_inputs(movies, oscars, duplicated)

    def test_unscaled_rt_percentages_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            for name, frame in zip(['movies', 'oscar', 'rotten_tomatoes'], self.inputs):
                frame = frame.copy()
                if name == 'rotten_tomatoes':
                    frame.loc[0, 'audience_score'] = 80
                frame.to_csv(Path(temporary) / f'clean_{name}.csv', index=False)
            with self.assertRaisesRegex(ValueError, 'normalized'):
                load_inputs(temporary)

    def test_four_round_matches_equal_saved_reference(self):
        generated = ROOT / 'data/processed'
        if not generated.exists():
            self.fail('Run python scripts/run_matching.py before the regression tests.')
        rounds = [('clean_rotten_tomatoes_with_imdb_id.csv', 787),
                  ('clean_rotten_tomatoes_with_imdb_id_year_pm1.csv', 798),
                  ('clean_rotten_tomatoes_with_imdb_id_round3.csv', 800),
                  ('clean_rotten_tomatoes_with_imdb_id_round4.csv', 802)]
        for name, count in rounds:
            self.assertEqual(pd.read_csv(generated / name).imdb_id.notna().sum(), count)
        for reference in (ROOT / 'data/reference').glob('*.csv'):
            pd.testing.assert_frame_equal(pd.read_csv(generated / reference.name), pd.read_csv(reference))


if __name__ == '__main__':
    unittest.main()
