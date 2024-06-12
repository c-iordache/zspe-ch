import os
import asyncio
import sqlite3
import logging
from fastapi import FastAPI, Query, HTTPException
from pydantic import ValidationError, conint, constr
from processing import calculate_statistics, filter_properties, create_graphs
from ingest import ingest_csv_real_estate_data_to_db
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read paths from environment variables
DATA_FILE_PATH = os.getenv('DATA_FILE_PATH')
DB_PATH = os.getenv('DB_PATH')

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
def root():
    """
    Root endpoint that shows a welcome message.
    """
    return "Welcome to the Zoomprop demo"

@app.get("/properties")
def get_properties(
    price_min: float = Query(None, ge=0.0, description="Minimum price filter"),
    price_max: float = Query(None, ge=0.0, description="Maximum price filter"),
    bedrooms: conint(ge=0) = Query(None, description="Minimum number of bedrooms"),
    bathrooms: conint(ge=0) = Query(None, description="Minimum number of bathrooms"),
    city: constr(min_length=1, max_length=100) = Query(None, description="City name")
):
    """
    Endpoint to get properties based on filters.
    """
    filters = {
        "price_range": (price_min, price_max) if price_min is not None and price_max is not None else None,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "city": city
    }
    try:
        properties = filter_properties(DB_PATH, **filters)
        return properties.to_dict(orient='records')
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/properties/statistics")
def get_statistics():
    """
    Endpoint to get statistics of properties.
    """
    try:
        stats = calculate_statistics(DB_PATH)
        return stats
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/graphs", response_class=HTMLResponse)
def get_graphs():
    """
    Endpoint to generate and display graphs.
    """
    try:
        create_graphs(DB_PATH)
        
        # HTML response with styled image embedding
        html_content = """
        <html>
        <head>
            <title>Property Data Graphs</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    background-color: #f4f4f9;
                    color: #333;
                }
                h1 {
                    margin-top: 20px;
                    color: #0056b3;
                }
                .container {
                    width: 80%;
                    max-width: 1000px;
                    margin: 20px auto;
                    padding: 20px;
                    background: white;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                    text-align: center;
                }
                img {
                    max-width: 100%;
                    height: auto;
                    margin: 20px 0;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Distribution of Property Prices</h1>
                <img src="/static/price_distribution_custom.png" alt="Price Distribution">
                <h1>Distribution of Properties by Number of Bedrooms</h1>
                <img src="/static/bedrooms_distribution.png" alt="Bedrooms Distribution">
                <h1>Average Property Price Over Years</h1>
                <img src="/static/price_trend_over_years.png" alt="Price Trend Over Years">
                <h1>Average Property Size Over Years</h1>
                <img src="/static/size_trend_over_years.png" alt="Size Trend Over Years">                                
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating graphs: {str(e)}")

@app.get("/static/{filename}")
def static_files(filename: str):
    """
    Endpoint to serve static files.
    """
    file_path = f'../data/{filename}'
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

async def periodically_run_ingest():
    """
    Periodically runs the ingestion process every 10 minutes.
    """
    while True:
        try:
            logging.info("Running ingestion script...")
            ingest_csv_real_estate_data_to_db(DATA_FILE_PATH, DB_PATH)
            logging.info("Ingestion completed.")
        except Exception as e:
            logging.error(f"Error during ingestion: {e}")
        await asyncio.sleep(600)  # Wait for 10 minutes

@app.on_event("startup")
async def startup_event():
    """
    Schedules periodic ingestion on startup.
    """
    logging.info("Scheduling periodic ingestion on startup...")
    asyncio.create_task(periodically_run_ingest())
