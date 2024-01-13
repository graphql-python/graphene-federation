import re


def clean_schema(schema):
    schema = re.sub(r"\s+", "", str(schema))
    return schema.strip()
