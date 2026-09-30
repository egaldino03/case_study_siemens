from src.card_kpis import (
    get_connected_not_srs,
    get_srs_ready_pct,
    total_equipment,
)
from src.helpers import format_title_with_srs


def test_total_equipment():
    filter_dict = {
        "service_region": ["SÃO PAULO INTERIOR"],
        "business_line": ["AXA"],
        "level_of_connection": ["SRS READY"],
    }
    assert total_equipment(filter_dict) == 38
    filter_dict = {
        "business_line": ["AXA"],
    }
    assert total_equipment(filter_dict) == 183


def test_get_srs_ready_pct():
    filters = {
        "service_region": ["SÃO PAULO INTERIOR"],
        "business_line": ["AXA"],
    }

    assert get_srs_ready_pct(filters) == 1.66

    filters = {}

    assert get_srs_ready_pct(filters) == 72.0

    filters = {
        "service_region": ["RIO DE JANEIRO"],
        "business_line": ["AXA"],
        "level_of_connection": ["NOT CONNECTED"],
    }

    assert get_srs_ready_pct(filters) == 0.0


def test_get_connected_not_srs():
    filters = {
        "service_region": ["SÃO PAULO INTERIOR"],
        "business_line": ["AXA"],
    }

    assert get_connected_not_srs(filters) == 1

    filters = {}

    assert get_connected_not_srs(filters) == 68

    filters = {
        "service_region": ["RIO DE JANEIRO"],
        "business_line": ["AXA"],
        "level_of_connection": ["NOT CONNECTED"],
    }

    assert get_connected_not_srs(filters) == 0
