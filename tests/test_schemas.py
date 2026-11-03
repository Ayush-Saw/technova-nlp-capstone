from serving.schemas import TriageResponse
def test_schema_accepts_valid_triage():
    TriageResponse.model_validate({"category":"Bug","priority":"High","product_area":"API","summary":"API returns errors","model_version":"v1"})
