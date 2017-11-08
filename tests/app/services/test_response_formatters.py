from nose.tools import assert_equal
from flask import json

import pytest

from app.main.services.response_formatters import \
    convert_es_status, convert_es_results


pytestmark = pytest.mark.usefixtures("services_mapping")


with open("example_es_responses/stats.json") as services:
    STATS_JSON = json.load(services)

with open("example_es_responses/index_info.json") as services:
    INDEX_INFO_JSON = json.load(services)

with open("example_es_responses/search_results.json") as search_results:
    SEARCH_RESULTS_JSON = json.load(search_results)


def test_should_build_query_block_in_response(services_mapping):
    res = convert_es_results(services_mapping, SEARCH_RESULTS_JSON,
                             {"q": "keywords", "category": "some catergory"})
    assert_equal(res["meta"]["query"]["q"], "keywords")
    assert_equal(res["meta"]["query"]["category"], "some catergory")


def test_should_build_search_response_from_es_response(services_mapping):
    res = convert_es_results(services_mapping, SEARCH_RESULTS_JSON, {"q": "keywords"})
    assert_equal(res["meta"]["query"]["q"], "keywords")
    assert_equal(res["meta"]["total"], 628)
    assert_equal(res["meta"]["took"], 69)
    assert_equal(len(res["services"]), 10)

    assert_equal(res["services"][0]["id"], "5390159512076288")
    assert_equal(res["services"][0]["lot"], "SaaS")
    assert_equal(res["services"][0]["frameworkName"], "G-Cloud 6")
    assert_equal(res["services"][0]["supplierName"], "Supplier Name")
    assert_equal(res["services"][0]["serviceName"], "Email Verification")
    assert_equal(res["services"][0]["serviceTypes"], [
        "Data management"
    ])


def test_should_build_highlights_es_response(services_mapping):
    res = convert_es_results(services_mapping, SEARCH_RESULTS_JSON, {"q": "keywords"})
    assert_equal(
        res["services"][0]["highlight"]["serviceName"],
        ["Email Verification"])
    assert_equal(res["services"][0]["highlight"]["serviceFeatures"], [
        "Verify email addresses at the point of entry",
        "Validate email address format",
        "Live email account",
        "Safe to email"
    ])
    assert_equal(res["services"][0]["highlight"]["serviceBenefits"], [
        "Increase email deliverability"
    ])


def test_should_not_include_highlights_if_not_in_es_results(services_mapping):
    copy = SEARCH_RESULTS_JSON
    del copy["hits"]["hits"][0]["highlight"]
    res = convert_es_results(services_mapping, copy, {"category": "some catergory"})
    assert_equal("highlight" in res["services"][0], False)


def test_should_build_status_response_from_es_response():
    res = convert_es_status("g-cloud-9", STATS_JSON, INDEX_INFO_JSON)
    assert_equal(res, {
        "num_docs": 19676,
        "primary_size": "52mb",
        "mapping_version": "9.0.0",
        "aliases": ["galias"],
    })


def test_should_build_status_response_from_es_response_with_empty_index():
    stats_json_with_no_docs = dict(STATS_JSON)
    del stats_json_with_no_docs["indices"]["g-cloud-9"]["primaries"]["docs"]
    res = convert_es_status("g-cloud-9", stats_json_with_no_docs)
    assert_equal(res, {
        "aliases": [],
        "mapping_version": None,
        "num_docs": None,
        "primary_size": "52mb",
    })
