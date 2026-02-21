"""@bruin

name: ingestion.trips
type: python
connection: duckdb-default

materialization:
  type: table
  strategy: append
image: python:3.11

columns:
  - name: pickup_datetime
    type: timestamp
    description: When the meter was engaged
  - name: dropoff_datetime
    type: timestamp
    description: When the meter was disengaged

@bruin"""

import os
import json
import pandas as pd

def materialize():
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]
    taxi_types = json.loads(os.environ["BRUIN_VARS"]).get("taxi_types", ["yellow"])

    # Generate list of months between start and end dates
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import requests
    from io import BytesIO
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/"
    all_dataframes = []
    
    current = start
    while current <= end:
        year_month = current.strftime("%Y-%m")
        
        for taxi_type in taxi_types:
            filename = f"{taxi_type}_tripdata_{year_month}.parquet"
            url = f"{base_url}{filename}"
            
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    df = pd.read_parquet(BytesIO(response.content))
                    
                    # Normalize datetime column names and select important columns
                    if taxi_type == "yellow":
                        if "tpep_pickup_datetime" in df.columns:
                            df = df.rename(columns={"tpep_pickup_datetime": "pickup_datetime"})
                        if "tpep_dropoff_datetime" in df.columns:
                            df = df.rename(columns={"tpep_dropoff_datetime": "dropoff_datetime"})
                    elif taxi_type == "green":
                        if "lpep_pickup_datetime" in df.columns:
                            df = df.rename(columns={"lpep_pickup_datetime": "pickup_datetime"})
                        if "lpep_dropoff_datetime" in df.columns:
                            df = df.rename(columns={"lpep_dropoff_datetime": "dropoff_datetime"})
                    
                    # Add taxi_type column
                    df["taxi_type"] = taxi_type
                    
                    # Ensure common columns exist (fill with None if missing)
                    common_columns = ["pickup_datetime", "dropoff_datetime", "taxi_type", 
                                     "payment_type", "trip_distance", "fare_amount", "total_amount"]
                    for col in common_columns:
                        if col not in df.columns:
                            df[col] = None
                    
                    all_dataframes.append(df)
            except Exception as e:
                # Skip files that don't exist or fail to download
                pass
        
        # Move to next month
        current += relativedelta(months=1)
    
    if all_dataframes:
        # Ensure all DataFrames have the same columns before concatenating
        all_columns = set()
        for df in all_dataframes:
            all_columns.update(df.columns)
        
        # Add missing columns to each DataFrame
        for df in all_dataframes:
            for col in all_columns:
                if col not in df.columns:
                    df[col] = None
        
        final_dataframe = pd.concat(all_dataframes, ignore_index=True)
        
        # Select only the columns we need for staging
        required_columns = ["pickup_datetime", "dropoff_datetime", "taxi_type"]
        optional_columns = ["payment_type", "trip_distance", "fare_amount", "total_amount"]
        
        # Keep required columns and any optional columns that exist
        columns_to_keep = [col for col in required_columns if col in final_dataframe.columns]
        columns_to_keep.extend([col for col in optional_columns if col in final_dataframe.columns])
        
        # Keep all other columns too (in case there are more)
        final_dataframe = final_dataframe[final_dataframe.columns]
        
        return final_dataframe
    else:
        # Return empty DataFrame with expected columns if no data found
        return pd.DataFrame(columns=["pickup_datetime", "dropoff_datetime", "taxi_type", 
                                    "payment_type", "trip_distance", "fare_amount", "total_amount"])
