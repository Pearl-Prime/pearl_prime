#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8790"
OUT = Path(__file__).resolve().parent


def req(method, path, data=None, headers=None):
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    body = None if data is None else json.dumps(data).encode()
    r = urllib.request.Request(BASE + path, data=body, headers=h, method=method)
    with urllib.request.urlopen(r, timeout=8) as resp:
        return resp.status, json.loads(resp.read().decode())


def main():
    _, health = req("GET", "/health")
    print("health", health.get("ok"), health.get("store"))
    _, draft = req(
        "POST",
        "/api/teacher-onboarding/drafts",
        {
            "teacher_name": "Browser Smoke",
            "teacher_id": "browser_smoke",
            "ui_state": {
                "identity": {
                    "teacherName": "Browser Smoke",
                    "teacherId": "browser_smoke",
                    "contactEmail": "b@example.com",
                },
                "teachingsText": "Doctrine paragraph one.\n\nDoctrine paragraph two for count.",
                "rights": {
                    "ownsMaterial": True,
                    "processingConsent": True,
                    "consent": True,
                    "noUnauthorizedCopyright": True,
                },
                "stories": [{"title": "t", "context": "c", "point": "p"}],
                "practices": [{"name": "n", "guidance": "g"}],
                "quotes": [{"text": "q"}],
                "urls": [],
                "files": [],
            },
        },
    )
    token, did = draft["edit_token"], draft["draft_id"]
    print("create", did)
    _, resumed = req("GET", f"/api/teacher-onboarding/drafts?edit_token={token}")
    print("resume", resumed["ui_state"]["identity"]["teacherName"])
    ui = resumed["ui_state"]
    ui["identity"]["teacherName"] = "Browser Smoke Edited"
    ui["teachingsText"] = "Edited doctrine paragraph one.\n\nEdited doctrine paragraph two."
    _, edited = req(
        "PUT",
        f"/api/teacher-onboarding/drafts/{did}",
        {"edit_token": token, "teacher_name": "Browser Smoke Edited", "ui_state": ui},
        {"X-Edit-Token": token},
    )
    print("edit", edited["draft"]["teacher_name"])
    _, sub = req(
        "POST",
        "/api/teacher-onboarding/submit",
        {
            "schema_version": "teacher_onboarding_intake_v1",
            "teacher_id": "browser_smoke",
            "teacher_name": "Browser Smoke Edited",
            "draft_id": did,
            "edit_token": token,
            "identity": {
                "public_teacher_name": "Browser Smoke Edited",
                "teacher_id": "browser_smoke",
                "contact_email": "b@example.com",
            },
            "rights": {
                "own_voice_or_original_material": True,
                "permission_to_process_into_atoms": True,
                "no_unauthorized_copyrighted_material": True,
                "final_consent_to_submit_intake": True,
            },
            "materials": {
                "teachings": {
                    "doctrine_text": "Edited doctrine paragraph one.\n\nEdited doctrine paragraph two."
                },
                "stories": [{"title": "t", "context": "c", "point": "p"}],
                "practices": [{"name": "n", "guidance": "g"}],
                "quotes": [{"text": "q"}],
                "links": ["https://example.com"],
                "files": [],
            },
        },
    )
    print("submit", sub.get("key"), "atoms", sub.get("production_atoms_created"))
    _, queue = req("GET", "/api/teacher-onboarding/queue")
    print("queue", queue["counts"])
    evidence = {
        "health_store": health.get("store"),
        "draft_id": did,
        "resume_ok": resumed.get("ok"),
        "edit_name": edited["draft"]["teacher_name"],
        "submit_key": sub.get("key"),
        "production_atoms_created": sub.get("production_atoms_created"),
        "queue_counts": queue["counts"],
    }
    (OUT / "api_smoke.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("wrote", OUT / "api_smoke.json")


if __name__ == "__main__":
    main()
