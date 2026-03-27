import pytest
import time
from fastapi.testclient import TestClient
from app.main import app 

def test_redact_endpoint_status():
    """Task 1: Assert that the API returns a 200 OK status."""
    with TestClient(app) as client:
        payload = {
            "text": "My name is James Bond and my email is 007@mi6.gov.uk."
        }
        
        response = client.post("/redact", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "redacted" in data

@pytest.mark.parametrize(
    "test_tier, input_text, max_latency",
    [
        (
            "Short", 
            "My name is John Doe and my IP is 192.168.1.1.", 
            2.5  # Expect ~1.0 - 2.0s
        ),
        (
            "Medium", 
            "Hi support, my name is Michael Scott. Please update my billing address to 1725 Slough Avenue, Scranton, PA 18505. You can reach me at 555-0199 or mscott@dundermifflin.com to confirm.", 
            5.5  # Expect ~4.0 - 4.5s
        ),
        (
            "Long", 
            "Dear HR, I am writing to update my direct deposit information. My name is Leslie Knope. My new bank is Pawnee Credit Union. The routing number is 123456789 and my account number is 9876543210. For tax purposes, my SSN is 000-11-2222. Please mail the confirmation to 123 Parks Dept, Pawnee, IN 46112. You can also call my cell at 555-0123 or email lknope@pawnee.in.gov. Thank you!", 
            15.0 # Expect ~10.0 - 12.0s
        )
    ]
)
def test_inference_scaling(test_tier, input_text, max_latency):
    """Task 2: Assert Total Latency scales reasonably based on input size."""
    with TestClient(app) as client:
        print(f"\n[INFO] Running {test_tier} Tier Evaluation...")
        
        client.post("/redact", json={"text": "warmup"})
        
        start_time = time.time()
        
        response = client.post("/redact", json={"text": input_text})
        
        latency = time.time() - start_time
        
        assert response.status_code == 200, f"API failed: {response.text}"
        print(f"[RESULT] {test_tier} Tier Latency: {latency:.4f} seconds (Limit: {max_latency}s)")
        
        assert latency < max_latency, f"{test_tier} test failed! Took {latency:.2f}s (SLA: < {max_latency}s)"