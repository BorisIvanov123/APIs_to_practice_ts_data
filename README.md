# Time Series Forecasting with Open Data APIs  
### Code examples and documentation on using open-source APIs to practice time series forecasting with Python.

### Open Weather 

# APIs

`Please note that most APIs are open source but still require registration to obtain an API key. Therefore, the scripts use a `.env` file to store API keys securely. You should create your own `.env` file and paste your API key there like this: `API_KEY=...`. Make sure you never publish or upload your `.env` file to the cloud or to any public repository.
`
## U.S. Energy Information Administration (EIA) Open Data API

### Documentation: https://www.eia.gov/opendata/

The API Dashboard from the U.S. Energy Information Administration (EIA) provides an interactive interface for exploring and constructing API end-points to access public energy datasets. Users can select specific routes, such as Electricity → Electric Power Operations (Daily and Hourly) → Daily Demand by Subregion, to retrieve structured time-series data directly from the EIA’s open data platform.

Through the dashboard, users can define parameters like data frequency (e.g., daily, hourly, monthly), specify date ranges, choose data types (such as electricity demand), and apply filters by facets like region or sector. Additionally, results can be sorted by time period or other variables for customized data extraction.

This tool simplifies the process of building API endpoints without requiring manual URL construction, making it ideal for students, analysts, developers, and researchers who want to access, visualize, or model large-scale time-series data on U.S. energy generation, consumption, and related metrics.

Data is retrieved using authenticated GET requests to the EIA API endpoints. Each dataset has its own endpoint, and you must include your personal API key (sent to you by email upon registration) in every request. Be sure to respect the EIA’s rate limits to avoid temporary suspension of your key.

#### Register for API: https://www.eia.gov/opendata/register.php
#### API Endpoint Documentation: https://www.eia.gov/opendata/documentation.php

***

## Federal Reserve Economic Data (FRED®) API

The Federal Reserve Economic Data (FRED®) platform, maintained by the Federal Reserve Bank of St. Louis, provides one of the largest open-access repositories of U.S. and international macroeconomic data. The FRED API allows users to programmatically retrieve these datasets for research, forecasting, and educational use.

Through the FRED API, users can access time-series data covering a wide range of economic indicators — including employment, inflation, GDP, interest rates, population, housing, and more — across multiple frequencies (daily, weekly, monthly, quarterly, and annual).

The API is built on a RESTful architecture, which means that data can be accessed directly through HTTPS requests returning structured JSON or XML responses.

#### Documentation: https://fred.stlouisfed.org/docs/api/fred/
#### Series Search Page: https://fred.stlouisfed.org/tags/series?ob=pv
#### Register for API Key: https://fredaccount.stlouisfed.org/apikeys

### Overview

The FRED API lets you search, explore, and download thousands of economic time series directly from the Federal Reserve Bank of St. Louis.

**You can use it to:**

- Search datasets by keyword (e.g., “inflation”, “GDP”, “employment”)
- Download observations as date–value pairs for analysis or forecasting
- View metadata such as frequency, units, and update history
- Explore data by category, source, or release (e.g., GDP, CPI, jobs reports)

Each dataset is identified by a unique series_id, for example:

- DGS10 → 10-Year Treasury Constant Maturity Rate (Daily)
- CPIAUCSL → Consumer Price Index for All Urban Consumers (Monthly)
- GDP → Gross Domestic Product (Quarterly)

#### Authentication and Base URL

All FRED API requests require an API key and use this base URL: https://api.stlouisfed.org/fred/

**Common Endpoints**

- /series → Get metadata for a dataset

- /series/observations → Get time-series values

- /series/search → Search for datasets by keyword

#### How to Get Started

Create a free account and request your API key here - https://fredaccount.stlouisfed.org/apikeys

After logging in, click “Request API Key” to generate your key instantly.

Add it to a local .env file (never share this publicly):

API_KEY_FRED=your_personal_api_key_here

Use the python-dotenv library to load it securely into your scripts.



