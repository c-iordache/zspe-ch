import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys

def calculate_statistics(db_path):
    try:
        conn = sqlite3.connect(db_path)
        query = 'SELECT * FROM listings'
        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty:
            print("No data found in the database.")
            return None

        # Calculate basic statistics
        stats = {
            'average_property_price': int(df['price'].mean()),
            'median_property_price': int(df['price'].median()),
            'average_price_per_sqft': round(df['price'].sum() / df['squarefeet'].sum(), 2),
            'total_properties': df.shape[0]
        }

        df.replace([pd.NaT, float('inf'), float('-inf')], pd.NA, inplace=True)
        df.fillna(value=0, inplace=True)           

        # Convert price, bedrooms, bathrooms, and squarefeet to int
        df['price'] = df['price'].astype(int)
        df['bedrooms'] = df['bedrooms'].astype(int)
        df['bathrooms'] = df['bathrooms'].astype(int)
        df['squarefeet'] = df['squarefeet'].astype(int)

        # Ensure datelisted is a non-empty string
        df['datelisted'] = df['datelisted'].apply(lambda x: x if x else "")        

        # Detect outliers using IQR
        Q1 = df['price'].quantile(0.25)
        Q3 = df['price'].quantile(0.75)
        IQR = Q3 - Q1
        threshold = 1.5

        lower_outliers = df[df['price'] < (Q1 - threshold * IQR)]
        higher_outliers = df[df['price'] > (Q3 + threshold * IQR)]

        stats['lower_outliers_count'] = lower_outliers.shape[0]
        stats['higher_outliers_count'] = higher_outliers.shape[0]

        stats['lower_outliers'] = lower_outliers.to_dict(orient='records')
        stats['higher_outliers'] = higher_outliers.to_dict(orient='records')

        print("Lower priced outliers:", lower_outliers.shape[0])
        print("Higher priced outliers:", higher_outliers.shape[0])

        #outliers = df[(df['price'] < (Q1 - threshold * IQR)) | (df['price'] > (Q3 + threshold * IQR))]

        #stats['outliers_count'] = outliers.shape[0]
        #print("outliers ", outliers.shape[0])
        #stats['outliers'] = outliers.to_dict(orient='records')
        #print("outl ",outliers.to_dict(orient='records'))
        return stats

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def filter_properties(db_path, price_range=None, bedrooms=None, bathrooms=None, city=None):
    try:
        conn = sqlite3.connect(db_path)
        query = 'SELECT * FROM listings WHERE 1=1'

        if price_range:
            query += f' AND price BETWEEN {price_range[0]} AND {price_range[1]}'
        if bedrooms:
            query += f' AND bedrooms >= {bedrooms}'
        if bathrooms:
            query += f' AND bathrooms >= {bathrooms}'
        if city:
            query += f' AND city = "{city}"'

        df = pd.read_sql(query, conn)

        # Replace NaN and infinite values
        df.replace([pd.NaT, float('inf'), float('-inf')], pd.NA, inplace=True)
        df.fillna(value=0, inplace=True)   

        # Convert price, bedrooms, bathrooms, and squarefeet to int
        df['price'] = df['price'].astype(int)
        df['bedrooms'] = df['bedrooms'].astype(int)
        df['bathrooms'] = df['bathrooms'].astype(int)
        df['squarefeet'] = df['squarefeet'].astype(int)

        # Ensure DateListed is a non-empty string
        df['datelisted'] = df['datelisted'].apply(lambda x: x if x else "")

        conn.close()

        if df.empty:
            print("No matching properties found.")
        return df

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return pd.DataFrame()
    
def create_graphs(db_path):
    try:
        conn = sqlite3.connect(db_path)
        query = 'SELECT * FROM listings'
        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty:
            print("No data found in the database.")
            return None

        sns.set(style="whitegrid")

        # Logarithmic binning for property prices
        df['price'] = df['price'].replace([np.inf, -np.inf], np.nan).fillna(0)
        price_log_bins = np.logspace(np.log10(df['price'][df['price'] > 0].min()), np.log10(df['price'].max()), 20)

        plt.figure(figsize=(10, 6))
        sns.histplot(df['price'], bins=price_log_bins, kde=True, color='skyblue')
        plt.xscale('log')
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

        plt.figure(figsize=(10, 6))
        sns.countplot(x='price_binned', data=df, palette='muted')
        plt.title('Distribution of Property Prices')
        plt.xlabel('Price Range')
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout(pad=2.0)
        plt.savefig('../data/price_distribution_custom.png')
        plt.close()

        # Distribution of properties by number of bedrooms (0 to 10+)
        df['bedrooms_limited'] = df['bedrooms'].apply(lambda x: '10+' if x > 10 else str(int(x) if not pd.isna(x) else 0))
        df['bedrooms_limited'] = pd.Categorical(df['bedrooms_limited'], categories=[str(i) for i in range(11)] + ['10+'])

        plt.figure(figsize=(10, 6))
        sns.countplot(x='bedrooms_limited', data=df, palette='muted', order=[str(i) for i in range(11)] + ['10+'])
        plt.title('Distribution of Properties by Number of Bedrooms')
        plt.xlabel('Number of Bedrooms')
        plt.ylabel('Count')
        plt.savefig('../data/bedrooms_distribution.png')
        plt.close()

    except Exception as e:
        print(f"Error creating graphs: {e}")
    
if __name__ == "__main__":
    try:
        db_path = '../data/properties_db.db'
        stats = calculate_statistics(db_path)
        if stats:
            print(stats)
        else:
            print("Statistics could not be calculated.")

    except Exception as e:
        print(f"Error in main execution: {e}")
        sys.exit(1)
