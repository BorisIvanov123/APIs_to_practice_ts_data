# Time Series Forecasting with Open Data APIs  
### Code examples and documentation on using open-source APIs to practice time series forecasting with Python.

## APIs

`Please note that most APIs are open source but still require registration to obtain an API key. Therefore, the scripts use a `.env` file to store API keys securely. You should create your own `.env` file and paste your API key there like this: `API_KEY=...`. Make sure you never publish or upload your `.env` file to the cloud or to any public repository.
`
### U.S. Energy Information Administration (EIA) Open Data API

#### Documentation: https://www.eia.gov/opendata/

The API Dashboard from the U.S. Energy Information Administration (EIA) provides an interactive interface for exploring and constructing API end-points to access public energy datasets. Users can select specific routes, such as Electricity → Electric Power Operations (Daily and Hourly) → Daily Demand by Subregion, to retrieve structured time-series data directly from the EIA’s open data platform.

Through the dashboard, users can define parameters like data frequency (e.g., daily, hourly, monthly), specify date ranges, choose data types (such as electricity demand), and apply filters by facets like region or sector. Additionally, results can be sorted by time period or other variables for customized data extraction.

This tool simplifies the process of building API endpoints without requiring manual URL construction, making it ideal for students, analysts, developers, and researchers who want to access, visualize, or model large-scale time-series data on U.S. energy generation, consumption, and related metrics.

Data is retrieved using authenticated GET requests to the EIA API endpoints. Each dataset has its own endpoint, and you must include your personal API key (sent to you by email upon registration) in every request. Be sure to respect the EIA’s rate limits to avoid temporary suspension of your key.

#### Register for API: https://www.eia.gov/opendata/register.php
#### API Endpoint Documentation: https://www.eia.gov/opendata/documentation.php

For more details on the underlying protocols, see:  https://datatracker.ietf.org/doc/html/rfc7231

