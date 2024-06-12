# Zoomprop Real Estate Data Processing

## Table of Contents
- [Overview](#overview)
- [Live URL](#live-url)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Endpoints](#endpoints)
- [Example Requests](#example-requests)


## Overview

This is a real estate data processing application that ingests data from a CSV file, calculates statistics, filters properties based on criteria, and provides data visualizations. The application is built with FastAPI, and it utilizes SQLite for data storage.

## Live URL
- [http://18.216.157.38/](http://18.216.157.38/)

## Installation

### Pre-requisites

- **Python**: Ensure `python3` (version used: 3.12) is installed.
- **pip**: Install with `sudo apt-get install python3-pip`.
- **SQLite**: Install with `sudo apt install sqlite3 libsqlite3-dev`.
- **Virtual Environment**: Install with `sudo apt install python3-venv`.
- **Hypercorn**: Install with `pip install hypercorn`.

### Setup

1. **Create and activate virtual environment**:
   ```bash
   cd src
   python3 -m venv venv
   source venv/bin/activate

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

3. **Upload CSV file**: Place your .csv file in the data folder named zoomprop_data_engineering.csv

4. **Create .env file in the src folder**:
   ```bash
   DATA_FILE_PATH=../data/zoomprop_data_engineering.csv
   DB_PATH=../data/properties_db.db
   ```
## Usage

### Run the server
  Run the server from the src folder:
  ```bash
  hypercorn fast_api:app --reload --bind 0.0.0.0:8000
  ```
  Access the server at http://<YOUR_IP>.

  Make sure to replace <YOUR_IP> with your server's actual IP address.

## Testing
  Run tests from the main folder:
  ```bash
  python3 -m pytest test/
  ```
## Endpoints
- Statistics: GET /properties/statistics
  -- Returns statistics in JSON format.
- Properties: GET /properties
  -- Query parameters: price_min, price_max, bedrooms, bathrooms, city
  
  -- Example: GET /properties?price_min=215000&price_max=220000&bedrooms=7&bathrooms=3&city=Miami
- Graphs: GET /graphs
  -- Displays property data visualizations

## Example Requests
  ```bash
  curl -X GET "http://18.216.157.38/properties?price_min=210000&price_max=220000&bedrooms=5&bathrooms=3&city=Miami"

  curl -X GET "http://18.216.157.38/properties/statistics"
   ```

In a browser, go to [http://18.216.157.38/graphs](http://18.216.157.38/graphs)



