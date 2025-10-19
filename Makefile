# DataSierra Test Makefile
# Easy commands to run tests

.PHONY: test health test-quick test-full clean

# Run all tests (default)
test:
	python3.11 test.py

# Run health check only
health:
	python3.11 health.py

# Run quick tests directly
test-quick:
	python3.11 tests/quick_integration_tests.py

# Run comprehensive tests directly
test-full:
	python3.11 tests/integration_tests.py

# Run health check directly
health-check:
	python3.11 tests/health_check.py

# Clean up any test artifacts
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	find . -name "*.pyo" -delete

# Help
help:
	@echo "DataSierra Test Commands:"
	@echo "  make test        - Run all integration tests"
	@echo "  make health      - Run health check only"
	@echo "  make test-quick  - Run quick tests directly"
	@echo "  make test-full   - Run comprehensive tests"
	@echo "  make health-check - Run health check directly"
	@echo "  make clean       - Clean up test artifacts"
	@echo "  make help        - Show this help"
