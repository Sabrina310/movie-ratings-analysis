from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "processed"
OUTPUT.mkdir(parents=True, exist_ok=True)
import pandas as pd
import re

# =========================
# File paths
# =========================
imdb_path = ROOT / "data" / "input" / "clean_movies.csv"
rt_input_path = OUTPUT / "clean_rotten_tomatoes_with_imdb_id_year_pm1.csv"

output_path = OUTPUT / "clean_rotten_tomatoes_with_imdb_id_round3.csv"
unmatched_output_path = OUTPUT / "rotten_tomatoes_unmatched_round3.csv"


def simplify_title(title):
    """
    Build a looser title version for matching.
    Assumes the original title has already been standardized to some extent.
    """
    if pd.isna(title):
        return None

    title = str(title).strip().lower()

    # remove content inside parentheses
    title = re.sub(r"\(.*?\)", "", title)

    # replace & with and
    title = title.replace("&", "and")

    # keep only main title before colon
    title = title.split(":")[0]

    # remove leading articles
    title = re.sub(r"^(the|a|an)\s+", "", title)

    # remove extra spaces
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

# =========================
# Build relaxed titles
# =========================
imdb["relaxed_title"] = imdb["primaryTitle"].apply(simplify_title)
rt["relaxed_title"] = rt["title"].apply(simplify_title)

# keep only useful columns
imdb_match = imdb[["tconst", "primaryTitle", "startYear", "relaxed_title"]].copy()

# =========================
# Round 3 matching
# Only process unmatched rows
# =========================
unmatched_mask = rt["imdb_id"].isna()
unmatched_rt = rt[unmatched_mask].copy()

matched_count_round3 = 0

for idx, row in unmatched_rt.iterrows():
    relaxed_title = row["relaxed_title"]
    year = row["year"]

    if pd.isna(relaxed_title) or pd.isna(year):
        continue

    candidates = imdb_match[
        (imdb_match["relaxed_title"] == relaxed_title) &
        (imdb_match["startYear"].between(year - 1, year + 1))
    ].copy()

    if len(candidates) == 1:
        rt.at[idx, "imdb_id"] = candidates.iloc[0]["tconst"]
        matched_count_round3 += 1

    elif len(candidates) > 1:
        # choose closest year first
        candidates["year_diff"] = (candidates["startYear"] - year).abs()
        best_match = candidates.sort_values(
            by=["year_diff", "startYear", "primaryTitle"]
        ).iloc[0]
        rt.at[idx, "imdb_id"] = best_match["tconst"]
        matched_count_round3 += 1

# =========================
# Save outputs
# =========================
rt.to_csv(output_path, index=False, encoding="utf-8-sig")
rt[rt["imdb_id"].isna()].to_csv(unmatched_output_path, index=False, encoding="utf-8-sig")

# =========================
# Stats
# =========================
total_rows = len(rt)
matched_rows = rt["imdb_id"].notna().sum()
unmatched_rows = rt["imdb_id"].isna().sum()
unmatched_rate = unmatched_rows / total_rows * 100 if total_rows > 0 else 0

print(f"Additional matches found in Round 3: {matched_count_round3}")
print(f"Total rows: {total_rows}")
print(f"Matched rows after Round 3: {matched_rows}")
print(f"Unmatched rows after Round 3: {unmatched_rows}")
print(f"Unmatched rate: {unmatched_rate:.2f}%")
print(f"New file saved to: {output_path}")
print(f"Unmatched file saved to: {unmatched_output_path}")