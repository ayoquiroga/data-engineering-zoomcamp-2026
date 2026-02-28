"""Pipeline to ingest NYC taxi data from REST API."""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def taxi_rest_api_source():
    """Define dlt resources from NYC Taxi REST API endpoint."""
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api",
        },
        "resources": [
            {
                "name": "taxi_trips",
                "endpoint": {
                    "path": "",
                    "params": {
                        "offset": 0,
                        "limit": 100000,
                    },
                },
            },
        ],
    }

    yield from rest_api_resources(config)


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name='taxi_pipeline',
        destination='duckdb',
        dataset_name='nyc_taxi_data',
        # `refresh="drop_sources"` ensures the data and the state is cleaned
        # on each `pipeline.run()`; remove the argument once you have a
        # working pipeline.
        refresh="drop_sources",
        # show basic progress of resources extracted, normalized files and load-jobs on stdout
        progress="log",
    )

    load_info = pipeline.run(taxi_rest_api_source())
    print(load_info)  # noqa: T201
