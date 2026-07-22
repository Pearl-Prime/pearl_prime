# Lane 03 closeout — what-runs-where policy + RAP extension

- **Status:** BLOCKED (prepared for operator integration; not merged by this bundle-building lane)
- **Base:** `7095e9e44445b1cd2944307629e019c343f71999`
- **Changes:** canonical operations framework extended in place; canonical RAP checker extended in place with a WARN-only local artifact-binary detector; two focused tests added; Program State and the existing LFS workstream updated.
- **Prerequisites:** Lane 01 BLOCKED and Lane 02 BLOCKED handoffs are present and terminal.
- **Proof:** `tests/test_check_rap_compliance.py` mutation test creates an unmediated local binary-write candidate and confirms it is detected; companion test confirms a canonical R2 marker is allowed. Targeted suite: **2 passed**. Full advisory scan: **117 non-blocking warnings**, recorded as the remediation backlog rather than folded into this lane.
- **Cleanup:** mutation data uses pytest temporary paths; no throwaway repository script, branch, remote mutation, or background job remains.
- **Next action:** apply the bundle on a clean branch from the recorded base (or rebase carefully), run the listed tests and full advisory scan, then open the PR. Remediate any pre-existing warnings in a separate lane.

Acceptance layer: authored integration candidate; merge and CI are not claimed.
