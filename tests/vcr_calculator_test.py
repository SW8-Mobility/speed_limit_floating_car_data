import pytest
from geo_json_metrics.vcr_calculator import map_vcr, vcr


@pytest.mark.parametrize("test_input, expected_vcrs", [
    ("map_vcr([1,2,3,4,5,6,7])", [0.5, 0.3333333333333333, 0.25, 0.2, 0.16666666666666666, 0.14285714285714285]),
    ("map_vcr([3, 2])", [-0.5])
    #("map_vcr([])", []) adds new test
])
def test_map_vcr(test_input, expected_vcrs: list[float]) -> None:
    assert eval(test_input) == expected_vcrs


@pytest.mark.parametrize("test_input, expected_vcr", [
    ("vcr(55.78, 45.0)", -0.23955555555555558),
    #("vcr()", ) adds new test
])
def test_vcr(test_input, expected_vcr) -> None:
    assert eval(test_input) == expected_vcr
    assert eval(test_input) < 0
