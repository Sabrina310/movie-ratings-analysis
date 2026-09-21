# Historical course materials

These files document the original implementation. Use `scripts/reproduce.py` for the maintained local entry point.

- Notebooks have cleared outputs/execution counts and anonymized MongoDB URIs/database names. The original analysis outputs remain visible in `reports/original/` and historical Oracle figures in this folder.
- `scripts/phase3.py`, `scripts/original-schema.sql` and the original MongoDB connection notebook contain destructive table/collection operations. They are retained as historical source, not part of the default reproduction workflow. Do not run them against an existing database you want to preserve.
- Historical scripts assume CSV files in the working directory and may still assume the original database service. Portable replacements are in the top-level `scripts/` directory.
- `phase-3-draft.tex` is an incomplete source draft with placeholders and inaccurate sections. The final PDF in `reports/original/` is the historical final submission.
- The original matching scripts now live in `scripts/match_01.py` through `match_04.py`; their algorithm is preserved with portable paths.
