# Data used in this folder

## synthetic_msme_assessments.csv  -  SYNTHETIC, NOT REAL
300 made-up businesses (60 for each of 5 profiles) produced by
`tools/generate_synthetic_dataset.py` with a fixed random seed (2026).
The profiles and their typical answers are assumptions made for testing.
Use it ONLY to test that the code works. Do not use it to train a model, to
claim accuracy, or as a research dataset.

## real_survey_template.csv
Empty file with the exact column names the pipeline expects (the 25 question
ids plus record_id, enterprise_size, sector, language). Fill it with answers
collected from real businesses and run `python tools/run_batch.py data/your_file.csv`.

## Real public sources found (NOT downloaded, NOT in this repo)
None of these contain this project's 25 questions, so they cannot be scored directly.
They are useful for citing context and sanity-checking the assumptions behind the
synthetic profiles (for example, how many micro firms use the internet at all).

* World Bank Enterprise Surveys, India - firm-level microdata with internet / website
  variables. Catalog: https://microdata.worldbank.org  (search "India" under Enterprise
  Surveys; e.g. "Enterprise Survey of Micro Firms 2022", ref IND_2022_ESM_v01_M).
  Download: https://www.enterprisesurveys.org/en/data  (free registration and
  acceptance of the terms of use is required - check them before use).
* RIS, "MSME Digitalisation in India" (field-survey report, adoption rates by sector,
  size and owner education): https://ris.org.in/sites/default/files/Publication/MSME_Digitalisation_Report.pdf
* "State of India's Informal Sector: A Deep Dive into Enterprises, Statistics, and Segments"
  (2024, FinDev Gateway) - report based on a 10,000+ enterprise survey.
* PayNearby "MSME Digital Index 2023" - published summary statistics only (press coverage on YourStory).
