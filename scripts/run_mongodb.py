"""Optional MongoDB loader and original aggregation queries; never clears collections."""
import argparse
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from movie_analysis.data import ROOT, load_inputs, movie_documents


def main():
    from pymongo import MongoClient
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--load', action='store_true', help='Insert into an empty collection only')
    args = parser.parse_args()
    with MongoClient(os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/'), serverSelectionTimeoutMS=5000) as client:
        client.admin.command('ping')
        db = client[os.environ.get('MONGODB_DATABASE', 'movie_analysis')]
        collection = db[os.environ.get('MONGODB_COLLECTION', 'merged_movies')]
        if args.load:
            if collection.find_one() is not None:
                raise RuntimeError('Collection is not empty. Choose a new MONGODB_COLLECTION or omit --load.')
            collection.insert_many(list(movie_documents(load_inputs())))
        if collection.find_one() is None:
            raise RuntimeError('Collection is empty. Run with --load first.')
        pipelines = json.loads((ROOT / 'src/movie_analysis/mongo_pipelines.json').read_text(encoding='utf-8'))
        output = ROOT / 'reports/results/mongodb'
        output.mkdir(parents=True, exist_ok=True)
        for name, pipeline in pipelines.items():
            rows = list(collection.aggregate(pipeline))
            (output / f'{name}.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
            print(f'{name}: {len(rows)} records')


if __name__ == '__main__':
    main()
