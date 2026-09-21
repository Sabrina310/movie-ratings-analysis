from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "processed"
OUTPUT.mkdir(parents=True, exist_ok=True)
import pandas as pd
import re
from rapidfuzz import process, fuzz

# =========================
# File paths
# =========================
imdb_path = ROOT / "data" / "input" / "clean_movies.csv"
rt_input_path = OUTPUT / "clean_rotten_tomatoes_with_imdb_id_round3.csv"

output_path = OUTPUT / "clean_rotten_tomatoes_with_imdb_id_round4.csv"
review_output_path = OUTPUT / "rotten_tomatoes_review_candidates_round4.csv"
unmatched_output_path = OUTPUT / "rotten_tomatoes_unmatched_round4.csv"


AUTO_ACCEPT_THRESHOLD = 95
REVIEW_THRESHOLD = 90


def simplify_title(title):
    if pd.isna(title):
        return None

    title = str(title).strip().lower()
    title = re.sub(r"\(.*?\)", "", title)
    title = title.replace("&", "and")
    title = title.split(":")[0]
    title = re.sub(r"^(the|a|an)\s+", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


# =========================
# Read files
# =========================
imdb = pd.read_csv(imdb_path)
rt = pd.read_csv(rt_input_path)

# =========================
# Required columns check
# =========================
required_imdb = {"tconst", "primaryTitle", "startYear"}
required_rt = {"title", "year", "imdb_id"}

missing_imdb = required_imdb - set(imdb.columns)
missing_rt = required_rt - set(rt.columns)

if missing_imdb:
    raise ValueError(f"IMDb file is missing columns: {missing_imdb}")
if missing_rt:
    raise ValueError(f"RT file is missing columns: {missing_rt}")

# =========================
# Clean types
# =========================
imdb["startYear"] = pd.to_numeric(imdb["startYear"], errors="coerce")
rt["year"] = pd.to_numeric(rt["year"], errors="coerce")

imdb["primaryTitle"] = imdb["primaryTitle"].astype(str).str.strip()
rt["title"] = rt["title"].astype(str).str.strip()

imdb["relaxed_title"] = imdb["primaryTitle"].apply(simplify_title)
rt["relaxed_title"] = rt["title"].apply(simplify_title)

imdb_match = imdb[["tconst", "primaryTitle", "startYear", "relaxed_title"]].copy()

# =========================
# Round 4 fuzzy matching
# Only process unmatched rows
# =========================
unmatched_mask = rt["imdb_id"].isna()
unmatched_rt = rt[unmatched_mask].copy()

auto_matched_count = 0
review_rows = []

for idx, row in unmatched_rt.iterrows():
    rt_title = row["title"]
    rt_relaxed_title = row["relaxed_title"]
    rt_year = row["year"]

    if pd.isna(rt_relaxed_title) or pd.isna(rt_year):
        continue

    # candidate pool limited to year ±1
    candidates = imdb_match[
        imdb_match["startYear"].between(rt_year - 1, rt_year + 1)
    ].copy()

    if candidates.empty:
        continue

    candidate_titles = candidates["relaxed_title"].fillna("").tolist()

    # best fuzzy match from relaxed titles
    best_match = process.extractOne(
        rt_relaxed_title,
        candidate_titles,
        scorer=fuzz.token_sort_ratio
    )

    if best_match is None:
        continue

    matched_title, score, match_pos = best_match
    candidate_row = candidates.iloc[match_pos]

    if score >= AUTO_ACCEPT_THRESHOLD:
        rt.at[idx, "imdb_id"] = candidate_row["tconst"]
        auto_matched_count += 1

    elif score >= REVIEW_THRESHOLD:
        review_rows.append({
            "rt_row_index": idx,
            "rt_title": rt_title,
            "rt_relaxed_title": rt_relaxed_title,
            "rt_year": rt_year,
            "candidate_imdb_id": candidate_row["tconst"],
            "candidate_title": candidate_row["primaryTitle"],
            "candidate_relaxed_title": candidate_row["relaxed_title"],
            "candidate_year": candidate_row["startYear"],
            "score": score
        })

# =========================
# Save outputs
# =========================
rt.to_csv(output_path, index=False, encoding="utf-8-sig")
pd.DataFrame(review_rows).to_csv(review_output_path, index=False, encoding="utf-8-sig")
rt[rt["imdb_id"].isna()].to_csv(unmatched_output_path, index=False, encoding="utf-8-sig")

# =========================
# Stats
# =========================
total_rows = len(rt)
matched_rows = rt["imdb_id"].notna().sum()
unmatched_rows = rt["imdb_id"].isna().sum()
unmatched_rate = unmatched_rows / total_rows * 100 if total_rows > 0 else 0

print(f"Additional auto matches found in Round 4: {auto_matched_count}")
print(f"Review candidates generated: {len(review_rows)}")
print(f"Total rows: {total_rows}")
print(f"Matched rows after Round 4: {matched_rows}")
print(f"Unmatched rows after Round 4: {unmatched_rows}")
print(f"Unmatched rate: {unmatched_rate:.2f}%")
print(f"New file saved to: {output_path}")
print(f"Review candidates file saved to: {review_output_path}")
print(f"Unmatched file saved to: {unmatched_output_path}")