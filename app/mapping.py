from flask import json


SERVICES_MAPPING_FILE_SPEC = "mappings/services.json"
SERVICE_ID_HASH_FIELD_NAME = "service_id_hash"

_services = None


class Mapping(object):
    def __init__(self, mapping_definition, mapping_type):
        self.definition = mapping_definition
        properties = self.definition['mappings'][mapping_type]['properties']
        meta_properties = self.definition['mappings'][mapping_type].get("_meta", {}).get("properties", {})

        self._filter_fields = tuple(sorted(
            field.replace('filter_', '')
            for field in properties.keys()
            if field.startswith('filter_')
        ))
        self.filter_fields_set = frozenset(self._filter_fields)

        self.non_filter_fields_set = frozenset(
            field
            for field in properties.keys()
            if not field.startswith('filter_')
        )

        self.text_search_fields = tuple(sorted(
            field
            for field in properties.keys()
            if meta_properties.get(field, {}).get("include_in_text_search", not field.startswith('filter_'))
        ))
        self.text_search_fields_set = frozenset(self.text_search_fields)

        self.response_fields = tuple(sorted(
            field
            for field in properties.keys()
            if meta_properties.get(field, {}).get("include_in_response", not field.startswith('filter_'))
        ))

        self.aggregatable_fields = tuple(sorted(
            k
            for k, v in properties.items()
            if v.get('fields', {}).get('raw', False)
        ))
        self.transform_fields = tuple(
            self.definition['mappings'][mapping_type].get('_meta', {}).get('transformations', {})
        )


def get_services_mapping():
    # mockable singleton - see conftest.py
    global _services
    if _services is None:
        with open(SERVICES_MAPPING_FILE_SPEC) as services_file:
            _services = Mapping(json.load(services_file), 'services')
    return _services
