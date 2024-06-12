# zspe-ch

Installation

Pre-requisite:
- python3 (3.12 used for demo)
- pip3 (if not installed, install with "sudo apt-get install python3-pip")
- virtualenv: sudo pip3 install virtualenv
- set up virtualenv: python3 -m venv venv
- run virtualenv: source venv/bin/activate
- pip3 install -r requirements.txt
- pip3 install hypercorn

Run server:
- cd src
- hypercorn fast_api:app --reload --bind 0.0.0.0:8000

Testing
- run python3 -m pytest test/ from the main folder

Live URL: http://18.216.157.38:8000/

Server will be accessible on
http://<YOUR_IP>:8000

Endpoint usage:

http://<YOUR_IP>:8000/properties/statistics - will display statistics about the data in JSON format

http://<YOUR_IP>:8000/properties?price_min=215000&price_max=220000&bedrooms=7&bathrooms=3&city=Miami - will display a JSON of properties with the price between 215000$ and 220000$ in Miami, that have at least 7 bedrooms and at least 3 bathrooms

http://<YOUR_IP>:8000/graphs - will generate and display graphs for data visualization
