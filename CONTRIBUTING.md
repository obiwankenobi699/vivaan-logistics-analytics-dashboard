# Contributing

Suggestions and fixes are welcome.

1. Fork the repository and create a branch: `git checkout -b feature/my-change`.
2. Keep the code simple and readable. Follow PEP 8 and add short comments where the logic is not obvious.
3. Run the dashboard (`streamlit run app.py`) and check every section before you open a pull request.
4. If you change the data rules in `src/data_prep.py` or the generator in `src/generate_data.py`, regenerate the CSV with `python src/generate_data.py` and mention the change in `CHANGELOG.md`.
5. Open a pull request that says what changed and why.

Use the issue templates in `.github/ISSUE_TEMPLATE` to report a bug or ask for a feature.
