from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_get_program_versions_missing_program():
    response = client.get("/programs/9999/versions")
    assert response.status_code == 404

def test_create_program_version():
    # First, create a program
    prog_response = client.post("/programs", json={
        "name": "Test Program",
        "goal": "Test Goal",
        "duration_weeks": 4
    })
    prog_id = prog_response.json()["id"]

    # Now create a version
    response = client.post(f"/programs/{prog_id}/versions", json={
        "version_label": "Test Version",
        "version_type": "manual"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["version_label"] == "Test Version"
    assert data["version_type"] == "manual"
    assert data["is_active"] is False

def test_activate_program_version_deactivates_others():
    prog_response = client.post("/programs", json={
        "name": "Activation Test",
        "goal": "Test Goal",
        "duration_weeks": 4
    })
    prog_id = prog_response.json()["id"]

    v1_response = client.post(f"/programs/{prog_id}/versions", json={
        "version_label": "V1",
        "version_type": "manual",
        "is_active": True
    })
    v1_id = v1_response.json()["id"]

    v2_response = client.post(f"/programs/{prog_id}/versions", json={
        "version_label": "V2",
        "version_type": "manual",
        "is_active": False
    })
    v2_id = v2_response.json()["id"]

    # Activating v2 should deactivate v1
    activate_response = client.post(f"/programs/{prog_id}/versions/{v2_id}/activate")
    assert activate_response.status_code == 200

    versions_response = client.get(f"/programs/{prog_id}/versions")
    versions = versions_response.json()
    
    active_versions = [v for v in versions if v["is_active"]]
    assert len(active_versions) == 1
    assert active_versions[0]["id"] == v2_id

def test_put_program_version_deactivates_others():
    prog_response = client.post("/programs", json={
        "name": "PUT Test",
        "goal": "Test Goal",
        "duration_weeks": 4
    })
    prog_id = prog_response.json()["id"]

    v1_response = client.post(f"/programs/{prog_id}/versions", json={
        "version_label": "V1",
        "version_type": "manual",
        "is_active": True
    })
    v1_id = v1_response.json()["id"]

    v2_response = client.post(f"/programs/{prog_id}/versions", json={
        "version_label": "V2",
        "version_type": "manual",
        "is_active": False
    })
    v2_id = v2_response.json()["id"]

    put_response = client.put(f"/programs/{prog_id}/versions/{v2_id}", json={
        "is_active": True
    })
    assert put_response.status_code == 200

    versions_response = client.get(f"/programs/{prog_id}/versions")
    versions = versions_response.json()
    
    active_versions = [v for v in versions if v["is_active"]]
    assert len(active_versions) == 1
    assert active_versions[0]["id"] == v2_id

def test_import_save_creates_active_version():
    import_payload = {
        "parsed_plan": {
            "program": {
                "name": "Imported Plan",
                "goal": "Gain muscle",
                "duration_weeks": 4
            },
            "workout_days": []
        },
        "approval_status": "original_extracted"
    }

    response = client.post("/imports/workout-plan/save", json=import_payload)
    assert response.status_code == 201
    prog_id = response.json()["program"]["id"]

    versions_response = client.get(f"/programs/{prog_id}/versions")
    versions = versions_response.json()

    assert len(versions) == 1
    v = versions[0]
    assert v["version_label"] == "Original imported plan"
    assert v["version_type"] == "imported_original"
    assert v["is_active"] is True
