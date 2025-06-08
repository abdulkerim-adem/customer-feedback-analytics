# Project: Customer Experience Analytics for Ethiopian Fintech Apps

[cite_start]This project is part of the 10 Academy Artificial Intelligence Mastery program (Week 2 Challenge). [cite_start]The goal is to act as a Data Analyst for Omega Consultancy, a firm advising Ethiopian banks on improving their mobile app services.

[cite_start]The project involves scraping user reviews from the Google Play Store for three major Ethiopian banks, performing in-depth analysis (sentiment and thematic), storing the data, and delivering a report with actionable recommendations.

## Task 1: Data Collection and Preprocessing

This first phase focuses on collecting raw user review data and cleaning it to prepare for analysis.

### Objective
[cite_start]The primary objective of this task is to scrape user reviews for the mobile applications of three Ethiopian banks—Commercial Bank of Ethiopia (CBE), Bank of Abyssinia (BOA), and Dashen Bank—from the Google Play Store. [cite_start]The goal was to collect a minimum of 400 reviews per bank.

### Methodology

#### 1. Scraping
- [cite_start]**Library Used**: The `google-play-scraper` Python library was used to collect the data.
- **Target Applications**:
    - Commercial Bank of Ethiopia (App ID: `com.cbe.mobile`)
    - Bank of Abyssinia (App ID: `com.boa.digital`)
    - Dashen Bank (App ID: `com.dashen.mobile`)
      _(Note: Please verify these are the correct and current app IDs)_
- **Scraping Parameters**: For each app, we scraped the most recent reviews available from the Ethiopian store (`country='et'`) in English (`lang='en'`), sorted by `Sort.NEWEST`. We aimed to fetch 450-500 reviews per app to ensure we had over 400 valid entries after cleaning.

#### 2. Preprocessing
[cite_start]After scraping, the raw data was passed through a preprocessing pipeline with the following steps:
- **Handling Missing Data**: Rows with null values in the essential `review` or `rating` columns were removed to ensure data quality.
- [cite_start]**Duplicate Removal**: Duplicate reviews were identified and removed based on a combination of `review` text, `rating`, `date`, and `bank` name to ensure each entry was unique.
- [cite_start]**Date Normalization**: The `date` column was standardized to a `YYYY-MM-DD` format for consistency and to facilitate time-series analysis later.

### Final Dataset Structure
The cleaned data was saved to `data/cleaned_play_store_reviews.csv`. [cite_start]The dataset adheres to the following structure:

| Column | Description |
|---|---|
| `review` | The full text content of the user's review. |
| `rating` | The star rating given by the user (1–5). |
| `date` | The date the review was posted, formatted as YYYY-MM-DD. |
| `bank` | The name of the bank corresponding to the app (e.g., "Commercial Bank of Ethiopia"). |
| `source` | The platform from which the data was scraped ("Google Play Store"). |

### How to Run the Script
1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```
2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Execute the notebook:**
    Open and run the cells in the `Week2_Challenge.ipynb` notebook to perform the scraping and preprocessing. The final cleaned dataset will be saved in the `/data` directory.