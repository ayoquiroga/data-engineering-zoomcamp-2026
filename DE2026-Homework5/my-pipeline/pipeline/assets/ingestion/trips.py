"""@bruin

name: ingestion.trips

type: python

image: python:3.11

connection: duckdb-default

depends:
  - ingestion.payment_lookup

materialization:
  type: table
  strategy: append

columns:
  - name: pickup_datetime
    type: timestamp
    description: When the meter was engaged
  - name: dropoff_datetime
    type: timestamp
    description: When the meter was disengaged
  - name: taxi_type
    type: string
    description: Type of taxi (yellow or green)
  - name: extracted_at
    type: timestamp
    description: Timestamp when the data was extracted (for lineage/debugging)

@bruin"""

import os
import json
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from io import BytesIO

def materialize():
    """
    Implement ingestion using Bruin runtime context.
    
    Uses BRUIN_START_DATE/BRUIN_END_DATE and taxi_types variable to fetch
    NYC Taxi parquet files from TLC endpoint.
    """
    # Read Bruin runtime context variables
    start_date = os.environ["BRUIN_START_DATE"]  # YYYY-MM-DD format
    end_date = os.environ["BRUIN_END_DATE"]      # YYYY-MM-DD format
    taxi_types = json.loads(os.environ["BRUIN_VARS"]).get("taxi_types", ["yellow"])
    
    # Extract timestamp for lineage/debugging (timezone-naive to avoid PyArrow issues)
    extracted_at = datetime.now().replace(tzinfo=None)
    
    # Generate list of months between start and end dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/"
    all_dataframes = []
    
    # Iterate through each month in the date range
    current = start
    while current <= end:
        year_month = current.strftime("%Y-%m")
        
        # Fetch data for each taxi type
        for taxi_type in taxi_types:
            filename = f"{taxi_type}_tripdata_{year_month}.parquet"
            url = f"{base_url}{filename}"
            
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    df = pd.read_parquet(BytesIO(response.content))
                    
                    # Convert ALL timezone-aware datetime columns to timezone-naive immediately
                    # This prevents PyArrow from needing the tzdata database
                    for col in df.columns:
                        if pd.api.types.is_datetime64_any_dtype(df[col]):
                            if hasattr(df[col].dtype, 'tz') and df[col].dtype.tz is not None:
                                df[col] = df[col].dt.tz_localize(None)
                            # Also ensure it's pure datetime64[ns] with no timezone
                            df[col] = pd.to_datetime(df[col]).dt.tz_localize(None) if df[col].dt.tz else df[col]
                    
                    # Normalize datetime column names (yellow vs green use different prefixes)
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
                    
                    # Add taxi_type and extracted_at columns for lineage/debugging
                    df["taxi_type"] = taxi_type
                    df["extracted_at"] = extracted_at
                    
                    # Ensure required columns exist
                    required_columns = ["pickup_datetime", "dropoff_datetime", "taxi_type", "extracted_at"]
                    for col in required_columns:
                        if col not in df.columns:
                            df[col] = None
                    
                    all_dataframes.append(df)
            except Exception as e:
                # Skip files that don't exist or fail to download
                # (e.g., future dates, network errors)
                pass
        
        # Move to next month
        current += relativedelta(months=1)
    
    # Concatenate all DataFrames
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
        
        # Convert ALL datetime columns to timezone-naive strings to completely avoid PyArrow timezone issues
        # This is necessary because DLT/PyArrow tries to normalize timestamps
        for col in final_dataframe.columns:
            if pd.api.types.is_datetime64_any_dtype(final_dataframe[col]):
                # Convert to string format to avoid any timezone processing
                final_dataframe[col] = final_dataframe[col].astype(str)
        
        # Select only the columns we need (keep all columns from source for staging layer)
        # The staging layer will handle cleaning and selecting specific columns
        return final_dataframe
    else:
        # Return empty DataFrame with expected columns if no data found
        return pd.DataFrame(columns=["pickup_datetime", "dropoff_datetime", "taxi_type", "extracted_at"])


