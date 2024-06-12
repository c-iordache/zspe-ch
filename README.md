Zoomprop Real Estate Data Processing

Live URL
http://18.216.157.38/

Installation
- Pre-requisites
  Python: Ensure python3 (3.12) is installed.
  pip: Install with sudo apt-get install python3-pip.
  SQLite: Install with sudo apt install sqlite3 libsqlite3-dev.
  Virtual Environment: Install with sudo apt install python3-venv.
  Hypercorn: Install with sudo apt install python3-hypercorn.
- Setup
  1. Create and activate virtual environment:
cd src
python3 -m venv venv
source venv/bin/activate

  2. Install dependencies:
pip3 install -r requirements.txt
pip3 install hypercorn pysqlite3

  3. Upload CSV file:
Upload your .csv file to the data folder as zoomprop_data_engineering.csv.

  5. Create .env file:
Create a .env file in the src folder with:

DATA_FILE_PATH=../data/zoomprop_data_engineering.csv

DB_PATH=../data/properties_db.db

Running the Server

Run the server from the src folder:

hypercorn fast_api:app --reload --bind 0.0.0.0:8000


Testing

Run tests from the main folder:
python3 -m pytest test/

API Endpoints

Welcome: GET /
Displays: "Welcome to the Zoomprop demo"

Statistics: GET /properties/statistics
Returns statistics in JSON format.

Properties: GET /properties
Query parameters: price_min, price_max, bedrooms, bathrooms, city
Example: GET /properties?price_min=215000&price_max=220000&bedrooms=7&bathrooms=3&city=Miami

Graphs: GET /graphs
Displays property data visualizations.


Example CURL Requests

curl -X GET "http://18.216.157.38/properties?price_min=210000&price_max=220000&bedrooms=5&bathrooms=3&city=Miami"
curl -X GET "http://18.216.157.38/properties/statistics"



