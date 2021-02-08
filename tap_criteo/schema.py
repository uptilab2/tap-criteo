import os
import json
import singer

logger = singer.get_logger()

DIMENSIONS = {
    # "analytics": ["AdvertiserId", "AdsetId", "CategoryId", "Advertiser", "Adset", "Category", "Device"],
    "analytics": ["AdvertiserId", "CategoryId", "Advertiser", "Category"],
}


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def get_schemas():
    schemas = {}
    metadata = {}
    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schema_data = json.load(file)
            dimensions = {
                "date": {"type": ["null", "string"], "format": "date-time"},
                **{
                    d: {"type": ["null", "string"]}
                    for d in DIMENSIONS[file_raw]
                }
            }
            schema_data["properties"].update(dimensions)
            schemas[file_raw] = schema_data
            metadata[file_raw] = {
                "dimensions": [d for d in dimensions if d != "date"]
            }
    return schemas, metadata
