from src.card_kpis import format_title_with_srs
from src.sidebar import get_filters


def test_get_filters():

    assert get_filters("service_region") == [
        format_title_with_srs(i)
        for i in [
            "SUL",
            "RIO DE JANEIRO",
            "CENTRO",
            "NORDESTE",
            "SÃO PAULO",
            "SÃO PAULO INTERIOR",
        ]
    ]
    assert get_filters("business_line") == [
        "XP SU",
        "AXA SU",
        "MR",
        "MI PET",
        "US",
        "CT",
        "XP WH",
        "SY",
        "MI SPECT",
        "AXA",
        "XP RF",
    ]

    assert get_filters("level_of_connection") == [
        format_title_with_srs(i)
        for i in [
            "CONNECTED BUT NOT SRS READY",
            "NOT CONNECTED",
            "SRS READY",
        ]
    ]
