import math
from tools.data_processor import process_engineering_data
from tools.engineering_analysis import perform_engineering_analysis
from tools.constraint_checker import check_engineering_constraints

def test_data_processor():
    case = {
        "case_id": "T1", "material": "steel", "load_n": 1000,
        "length_m": 2.0, "width_m": 0.05, "height_m": 0.1,
        "allowable_stress_pa": 250e6,
    }
    result = process_engineering_data.invoke({"case": case})
    assert result["status"] == "PASS"

def test_engineering_analysis():
    data = {
        "status": "PASS", "load_n": 1000, "length_m": 2.0,
        "width_m": 0.05, "height_m": 0.1, "allowable_stress_pa": 250e6,
    }
    result = perform_engineering_analysis.invoke({"data": data})
    expected = 6 * (1000 * 2 / 4) / (0.05 * 0.1**2)
    assert math.isclose(result["stress_pa"], expected, rel_tol=1e-10)

def test_constraint_failure():
    data = {
        "status": "PASS", "load_n": 10000, "length_m": 2.0,
        "width_m": 0.05, "height_m": 0.05, "allowable_stress_pa": 1e6,
    }
    analysis = perform_engineering_analysis.invoke({"data": data})
    result = check_engineering_constraints.invoke({"analysis": analysis, "data": data})
    assert result["status"] == "FAIL"
