# zspe-ch

Installation

Pre-requisite:
- python3 (3.12 used for demo)
- pip3 (if not installed, install with "sudo apt-get install python3-pip)
- pip3 install -r requirements.txt

Run server:
- cd src
- hypercorn fast_api:app --reload --bind 0.0.0.0:8000

Server will be accessible on
http://<YOUR_IP>:8000

Endpoint usage:
http://<YOUR_IP>:8000/properties/statistics - will display statistics about the data in JSON format
http://<YOUR_IP>:8000/properties?bedrooms=450&bathrooms=12 - will display a JSON of properties with more than 450 bedrooms and more than 12 bathrooms
http://<YOUR_IP>:8000/graphs - will generate and display graphs for data visualization
