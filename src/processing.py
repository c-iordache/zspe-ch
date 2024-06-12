import sqlite3
import logging
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_statistics(db):
    try:
        conn = db if isinstance(db, sqlite3.Connection) else sqlite3.connect(os.path.abspath(db))
        df = pd.read_sql('SELECT * FROM listings', conn)
        
        if df.empty:
            logging.info("No data found in the database.")
            return {}

        stats = {
            'average_property_price': int(df['price'].mean()),
            'median_property_price': int(df['price'].median()),
            'average_price_per_sqft': round(df['price'].sum() / df['squarefeet'].sum(), 2),
            'total_properties': df.shape[0]
        }

        df.replace([pd.NaT, float('inf'), float('-inf')], pd.NA, inplace=True)
        df.fillna(value=0, inplace=True)

        df['price'] = df['price'].astype(int)
        df['bedrooms'] = df['bedrooms'].astype(int)
        df['bathrooms'] = df['bathrooms'].astype(int)
        df['squarefeet'] = df['squarefeet'].astype(int)

        Q1, Q3 = df['price'].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        threshold = 1.5

        lower_outliers = df[df['price'] < (Q1 - threshold * IQR)]
        higher_outliers = df[df['price'] > (Q3 + threshold * IQR)]
        outliers = pd.concat([lower_outliers, higher_outliers])

        stats['outliers_count'] = outliers.shape[0]
        stats['outliers'] = outliers.to_dict(orient='records')
        logging.info("Total outliers: %d", outliers.shape[0])

        return stats
    except sqlite3.Error as e:
        logging.error("Database error: %s", e)
        raise
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        raise
    finally:
        if not isinstance(db, sqlite3.Connection):
            conn.close()

def filter_properties(db, price_range=None, bedrooms=None, bathrooms=None, city=None):
    try:
        conn = db if isinstance(db, sqlite3.Connection) else sqlite3.connect(os.path.abspath(db))
        query = 'SELECT * FROM listings WHERE 1=1'
        params = []

        if price_range:
            query += ' AND price BETWEEN ? AND ?'
            params.extend(price_range)
        if bedrooms:
            query += ' AND bedrooms >= ?'
            params.append(bedrooms)
        if bathrooms:
            query += ' AND bathrooms >= ?'
            params.append(bathrooms)
        if city:
            query += ' AND city = ?'
            params.append(city)

        df = pd.read_sql(query, conn, params=params)
        
        if not isinstance(db, sqlite3.Connection):
            conn.close()

        df.replace([pd.NaT, float('inf'), float('-inf')], pd.NA, inplace=True)
        df.fillna(value=0, inplace=True)
        df = df.infer_objects(copy=False)
        df['price'] = df['price'].astype(int)
        df['bedrooms'] = df['bedrooms'].astype(int)
        df['bathrooms'] = df['bathrooms'].astype(int)
        df['squarefeet'] = df['squarefeet'].astype(int)
        df['datelisted'] = df['datelisted'].apply(lambda x: x if x else "")

        if df.empty:
            logging.info("No matching properties found.")
        return df
    except sqlite3.Error as e:
        logging.error("Database error: %s", e)
        return pd.DataFrame()
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        return pd.DataFrame()

def create_graphs(db):
    """
    Creates and saves graphs for property data.

    Parameters:
    db (str or sqlite3.Connection): Path to the SQLite database file or an SQLite connection object.
    """
    try:
        # Use provided connection or create a new one
        if isinstance(db, sqlite3.Connection):
            conn = db
        else:
            conn = sqlite3.connect(os.path.abspath(db))
        
        query = 'SELECT * FROM listings'
        df = pd.read_sql(query, conn)
        
        if not isinstance(db, sqlite3.Connection):
            conn.close()

        if df.empty:
            logging.info("No data found in the database.")
            return

        sns.set(style="whitegrid")

        # Logarithmic binning for property prices
        df['price'] = df['price'].replace([np.inf, -np.inf], np.nan).fillna(0)
        price_log_bins = np.logspace(np.log10(df['price'][df['price'] > 0].min()), np.log10(df['price'].max()), 20)

        os.makedirs('../data', exist_ok=True)

        # Distribution of Property Prices (Log Scale)
        plt.figure(figsize=(10, 6))
        sns.histplot(df['price'], bins=price_log_bins, kde=True, color='skyblue')
        plt.xscale('log')
        plt.gca().get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: '{:,.0f}'.format(x)))
        plt.title('Distribution of Property Prices (Log Scale)')
        plt.xlabel('Price')
        plt.ylabel('Frequency')
        plt.savefig('../data/price_distribution_log.png')
        plt.close()

        # Custom binning for property prices
        price_bins = [0, 50000, 100000, 200000, 300000, 500000, 1000000, 5000000, 10000000, np.inf]
        df['price_binned'] = pd.cut(df['price'], bins=price_bins, labels=[
            '0-50k$', '50k-100k$', '100k-200k$', '200k-300k$', '300k-500k$', 
            '500k-1M$', '1M-5M$', '5M-10M$', '10M+$'
        ], include_lowest=True)

        # Distribution of Property Prices
        plt.figure(figsize=(10, 6))
        sns.countplot(x='price_binned', data=df, palette='muted', hue='price_binned', dodge=False)
        plt.title('Distribution of Property Prices')
        plt.xlabel('Price Range')
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.legend([], [], frameon=False)  # Hide the legend
        plt.tight_layout(pad=2.0)
        plt.savefig('../data/price_distribution_custom.png')
        plt.close()

        # Distribution of properties by number of bedrooms (0 to 10+)
        df['bedrooms_limited'] = df['bedrooms'].apply(lambda x: '10+' if x > 10 else str(int(x) if not pd.isna(x) else 0))
        df['bedrooms_limited'] = pd.Categorical(df['bedrooms_limited'], categories=[str(i) for i in range(11)] + ['10+'])

        # Distribution of Properties by Number of Bedrooms
        plt.figure(figsize=(10, 6))
        sns.countplot(x='bedrooms_limited', data=df, palette='muted', hue='bedrooms_limited', dodge=False, order=[str(i) for i in range(11)] + ['10+'])
        plt.title('Distribution of Properties by Number of Bedrooms')
        plt.xlabel('Number of Bedrooms')
        plt.ylabel('Count')
        plt.legend([], [], frameon=False)  # Hide the legend
        plt.savefig('../data/bedrooms_distribution.png')
        plt.close()

        # Trend analysis based on datelisted
        df['datelisted'] = pd.to_datetime(df['datelisted'], errors='coerce')
        df = df.dropna(subset=['datelisted'])
        df['year'] = df['datelisted'].dt.year

        # Average Property Price Over Years
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x='year', y='price', estimator='mean', ci=None, marker='o', color='skyblue')
        plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: '${:,.0f}'.format(x).replace('1000', '1k')))
        plt.title('Average Property Price Over Years')
        plt.xlabel('Year')
        plt.ylabel('Average Price')
        plt.grid(True)
        plt.savefig('../data/price_trend_over_years.png')
        plt.close()

        # Average Property Size Over Years
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x='year', y='squarefeet', estimator='mean', ci=None, marker='o', color='skyblue')
        plt.title('Average Property Size Over Years')
        plt.xlabel('Year')
        plt.ylabel('Average Square Feet')
        plt.grid(True)
        plt.savefig('../data/size_trend_over_years.png')
        plt.close()

    except Exception as e:
        logging.error("Error creating graphs: %s", e)
