# zspe-ch

Installation

Pre-requisite:
- python3 (3.12 used for demo)
- pip3 (if not installed, install with "sudo apt-get install python3-pip")
- install sqlite: sudo apt install sqlite3 libsqlite3-dev
- virtualenv setup: sudo apt install python3.12-venv
- virtualenv: sudo apt install python3-virtualenv
- install hypercorn: sudo apt install python3-hypercorn
- change to src folder: cd src
- set up virtualenv: python3 -m venv venv
- activate virtual env: source venv/bin/activate
- pip3 install -r requirements.txt
- pip3 install hypercorn
- pip3 install pysqlite3
- upload your .csv file to the data folder. its name should be zoomprop_data_engineering.csv
- create a .env file in the src folder (by default it is:
  
DATA_FILE_PATH=../data/zoomprop_data_engineering.csv

DB_PATH=../data/properties_db.db


Run server (from the src folder):
- hypercorn fast_api:app --reload --bind 0.0.0.0:8000

Testing
- run python3 -m pytest test/ from the main folder

Live URL: http://18.216.157.38/

Server will be accessible on
http://<YOUR_IP>

Endpoint usage:

http://18.216.157.38/properties/statistics - will display statistics about the data in JSON format

http://18.216.157.38/properties?price_min=215000&price_max=220000&bedrooms=7&bathrooms=3&city=Miami - will display a JSON of properties with the price between 215000$ and 220000$ in Miami, that have at least 7 bedrooms and at least 3 bathrooms

http://18.216.157.38/graphs - will generate and display graphs for data visualization

Example CURL request: curl -X GET "http://18.216.157.38/properties?price_min=210000&price_max=220000&bedrooms=5&bathrooms=3&city=Miami"

curl -X GET "http://18.216.157.38/properties/statistics"
