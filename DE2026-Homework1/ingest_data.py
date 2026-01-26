#!/usr/bin/env python
# coding: utf-8

import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

def ingest_data(
        url: str,
        engine,
        target_table: str,
        chunksize: int = 100000,
) -> pd.DataFrame:
    # Read the entire parquet file
    df = pd.read_parquet(url)
    
    # Create the table with empty data first
    df.head(0).to_sql(
        name=target_table,
        con=engine,
        if_exists="replace"
    )

    print(f"Table {target_table} created")

    # Insert data in chunks
    total_rows = len(df)
    for start in tqdm(range(0, total_rows, chunksize)):
        end = min(start + chunksize, total_rows)
        df_chunk = df.iloc[start:end]
        
        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append"
        )
        print(f"Inserted chunk: {len(df_chunk)} rows (from {start} to {end})")

    print(f'Done ingesting {total_rows} rows to {target_table}')

@click.command()
@click.option('--user', default='root', help='PostgreSQL username')
@click.option('--password', default='root', help='PostgreSQL password')
@click.option('--host', default='localhost', help='PostgreSQL host')
@click.option('--port', default='5432', help='PostgreSQL port')
@click.option('--db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--table', default='green_taxi_data', help='Target table name')
@click.option('--year', default=2025, help='Year of the data')
@click.option('--month', default=11, help='Month of the data')
@click.option('--chunksize', default=100000, help='Number of rows per chunk')
def main(user, password, host, port, db, table, year, month, chunksize):
    """Ingest CSV data from URL into PostgreSQL database."""
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    
    # First, ingest taxi zone lookup table
    print("Ingesting taxi zone lookup table...")
    taxi_zones = pd.read_csv('./taxi_zone_lookup.csv')
    taxi_zones.to_sql(
        name='taxi_zone_lookup',
        con=engine,
        if_exists='replace',
        index=False
    )
    print(f"Inserted {len(taxi_zones)} rows into taxi_zone_lookup table")
    
    # Then, ingest green taxi trip data
    print("\nIngesting green taxi trip data...")
    url = f'./green_tripdata_{year:04d}-{month:02d}.parquet'

    ingest_data(
        url=url,
        engine=engine,
        target_table=table,
        chunksize=chunksize
    )

if __name__ == '__main__':
    main()