import os
import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

def test_redact_endpoint_status():
    with TestClient(app) as client:
        payload = {"text": "My name is James Bond and my email is 007@mi6.gov.uk."}
        response = client.post("/redact", json=payload)
        assert response.status_code == 200

@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Hardware is too slow in CI/CD for performance testing.")
@pytest.mark.parametrize(
    "test_tier, input_text, max_latency",
    [
        ("Short", "My name is John Doe.", 2.5),
        ("Medium", "Hi support, my name is Michael Scott. Update my address to 1725 Slough Ave.", 5.5),
        ("Long", "Dear HR, my name is Leslie Knope. My SSN is 000-11-2222. Call me at 555-0123.", 15.0)
    ]
)
def test_inference_scaling(test_tier, input_text, max_latency):
    with TestClient(app) as client:
        print(f"\n[INFO] Running {test_tier} Tier Evaluation...")
        
        client.post("/redact", json={"text": "warmup"})
        
        start_time = time.time()
        response = client.post("/redact", json={"text": input_text})
        latency = time.time() - start_time
        
        assert response.status_code == 200
        print(f"[RESULT] {test_tier} Tier Latency: {latency:.4f} seconds (Limit: {max_latency}s)")
        assert latency < max_latency