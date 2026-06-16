.PHONY: test-integration

# Expensive full-stack Book 3 render (~5–10 min). Not run in fast CI.
test-integration:
	PYTHONPATH=. python3 -m pytest tests/integration/ -v --tb=short -m integration
