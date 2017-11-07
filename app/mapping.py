from functools import reduce
from itertools import groupby
from operator import or_

from flask import json


SERVICES_MAPPING_FILE_SPEC = "mappings/services.json"

_services = None


class Mapping(object):
    filter_field_prefix = "dmfilter"
    text_search_field_prefix = "dmtext"
    sort_only_field_prefix = "dmsortonly"
    aggregatable_field_prefix = "dmagg"

    # for now, these definitions are identical
    response_field_prefix = "dmtext"

    def __init__(self, mapping_definition, mapping_type):
        self.definition = mapping_definition
        properties = self.definition['mappings'][mapping_type]['properties']

        # build a dict of {prefix: frozenset(unprefixed_field_names)}
        self.fields_by_prefix = {
            prefix: frozenset(name for _, name in pairs)
            for prefix, pairs in groupby(
                (
                    (prefix, maybe_name[0])
                    for prefix, *maybe_name in (
                        full_field_name.split("_", 1)
                        for full_field_name in sorted(properties.keys())
                    )
                    if maybe_name  # maybe_name would be an empty sequence if no underscores were found, discard these
                ),
                key=lambda x: x[0],  # (the prefix)
            )
        }
        # now generate the inverse, {field_name: frozenset(prefixes)}
        self.prefixes_by_field = {
            name: frozenset(prefix for prefix, names in self.fields_by_prefix.items() if name in names)
            for name in reduce(or_, self.fields_by_prefix.values() or frozenset())
        }

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
