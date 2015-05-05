import six

from .query_builder import FILTER_FIELDS, TEXT_FIELDS
from .conversions import strip_and_lowercase


def process_values_for_matching(request_json, key):
    values = request_json[key]

    if isinstance(values, list):
        return [strip_and_lowercase(value) for value in values]
    elif isinstance(values, six.string_types):
        return strip_and_lowercase(values)

    return values


def convert_request_json_into_index_json(request_json):
    filter_fields = [field for field in request_json if field in FILTER_FIELDS]

    for field in filter_fields:
        request_json["filter_" + field] = \
            process_values_for_matching(request_json, field)
        if field not in TEXT_FIELDS:
            del request_json[field]

    return request_json
