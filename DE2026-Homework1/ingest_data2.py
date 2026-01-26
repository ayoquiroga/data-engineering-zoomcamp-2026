#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd


# In[5]:


get_ipython().system('wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet')


# In[10]:


# Read the data
df = pd.read_parquet("green_tripdata_2025-11.parquet")

# Display first rows
df.head()


# In[11]:


# Check data types
df.dtypes


# In[12]:


# Check data shape
df.shape


# In[13]:


pd.__file__


# In[14]:


len(df)


# In[15]:


get_ipython().system('wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv')


# In[16]:


df_zones = pd.read_csv("taxi_zone_lookup.csv")


# In[18]:


df_zones


# In[20]:


df["lpep_pickup_datetime"], df["lpep_pickup_datetime"], df["VendorID"]


# In[21]:


df


# In[23]:


get_ipython().system('uv add sqlalchemy psycopg2-binary')


# In[24]:


from sqlalchemy import create_engine
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')


# In[37]:


print(pd.io.sql.get_schema(df, name='green_taxi_data_nb', con=engine))


# In[38]:


df.head(n=0)


# In[39]:


df.head(n=0).to_sql(name='green_taxi_data_nb', con=engine, if_exists='replace')


# In[40]:


get_ipython().system('uv add tqdm')


# In[41]:


from tqdm.auto import tqdm


# In[42]:


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


# In[44]:


# Then, ingest green taxi trip data
print("\nIngesting green taxi trip data...")
url = f'./green_tripdata_2025-11.parquet'

ingest_data(
    url=url,
    engine=engine,
    target_table=table,
    chunksize=chunksize
)


# In[50]:


get_ipython().system('uv run jupyter nbconvert --to=script notebook.ipynb')
get_ipython().system('mv notebook.py ingest_data2.py')


# In[ ]:




