import os
from fastapi import FastAPI, Query, HTTPException, status
from pydantic import ValidationError, conint, constr, conlist
from processing import calculate_statistics, filter_properties, create_graphs
import sqlite3
from fastapi.responses import HTMLResponse, FileResponse

app = FastAPI()

@app.get("/properties")
def get_properties(
    price_min: float = Query(None, ge=0.0, description="Minimum price filter"),
    price_max: float = Query(None, ge=0.0, description="Maximum price filter"),
    bedrooms: conint(ge=0) = Query(None, description="Minimum number of bedrooms"),
    bathrooms: conint(ge=0) = Query(None, description="Minimum number of bathrooms"),
    city: constr(min_length=1, max_length=100) = Query(None, description="City name")
):
    filters = {
        "price_range": (price_min, price_max) if price_min is not None and price_max is not None else None,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "city": city
    }
    try:
        properties = filter_properties('../data/properties_db.db', **filters)
        return properties.to_dict(orient='records')
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/properties/statistics")
def get_statistics():
    try:
        stats = calculate_statistics('../data/properties_db.db')
        return stats
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@app.get("/graphs", response_class=HTMLResponse)
def get_graphs():
    try:
        create_graphs('../data/properties_db.db')
        
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
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating graphs: {str(e)}")
    
@app.get("/static/{filename}")
def static_files(filename: str):
    file_path = f'../data/{filename}'
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
