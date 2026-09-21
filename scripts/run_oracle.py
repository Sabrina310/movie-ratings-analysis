"""Optional Oracle loader and SQL analysis in a dedicated empty schema."""
import argparse
import getpass
import os
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from movie_analysis.data import ROOT, load_inputs, relational_inputs


def main():
    import oracledb
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--load', action='store_true', help='Create and populate tables; refuses existing project tables')
    args = parser.parse_args()
    username = os.environ.get('ORACLE_USER') or input('Oracle username: ')
    password = os.environ.get('ORACLE_PASSWORD') or getpass.getpass('Oracle password: ')
    with oracledb.connect(user=username, password=password, dsn=os.environ.get('ORACLE_DSN', 'localhost:1522/stu')) as conn:
        with conn.cursor() as cursor:
            if args.load:
                movies, oscars, rotten = relational_inputs(*load_inputs())
                cursor.execute("SELECT table_name FROM user_tables WHERE table_name IN ('MOVIES','OSCARS','ROTTENTOMATOES')")
                if cursor.fetchall():
                    raise RuntimeError('Project tables already exist. Use a fresh schema or omit --load.')
                for statement in (ROOT / 'sql/oracle_schema.sql').read_text(encoding='utf-8').split(';'):
                    if statement.strip():
                        cursor.execute(statement)
                cursor.executemany('INSERT INTO Movies VALUES (:1,:2,:3,:4,:5,:6)',
                                   list(movies[['tconst','primaryTitle','startYear','genres','averageRating','numVotes']].itertuples(index=False, name=None)))
                cursor.executemany('INSERT INTO Oscars VALUES (:1,:2,:3)',
                                   list(oscars[['FilmId','Year','Film']].itertuples(index=False, name=None)))
                cursor.executemany('INSERT INTO RottenTomatoes VALUES (:1,:2,:3,:4)',
                                   list(rotten[['title','year','audience_score','critics_score']].itertuples(index=False, name=None)))
                conn.commit()
            output = ROOT / 'reports/results/oracle'
            output.mkdir(parents=True, exist_ok=True)
            for i in range(1, 4):
                cursor.execute((ROOT / f'sql/rq{i}.sql').read_text(encoding='utf-8').strip().rstrip(';'))
                frame = pd.DataFrame(cursor.fetchall(), columns=[c[0] for c in cursor.description])
                frame.to_csv(output / f'rq{i}.csv', index=False)
                print(f'RQ{i}: {len(frame)} records')


if __name__ == '__main__':
    main()
