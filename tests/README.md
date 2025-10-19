# DataSierra Tests

This folder contains all integration tests for the DataSierra application.

## Test Files

- **`health_check.py`** - Quick health check of core systems
- **`quick_integration_tests.py`** - Core functionality tests
- **`integration_tests.py`** - Comprehensive test suite
- **`run_tests.py`** - Main test runner with clean output

## Running Tests

### From Root Directory (Recommended)
```bash
# Run all tests
python3.11 test.py

# Run health check only
python3.11 health.py
```

### From Tests Directory
```bash
cd tests

# Run all tests
python3.11 run_tests.py

# Run health check
python3.11 health_check.py

# Run quick tests
python3.11 quick_integration_tests.py

# Run comprehensive tests
python3.11 integration_tests.py
```

## Test Coverage

✅ Authentication system  
✅ File upload and processing  
✅ AI query functionality  
✅ Visualization generation  
✅ History management  
✅ Feedback system  

## Requirements

- Python 3.11+
- Firebase configuration (`.env` file)
- All DataSierra dependencies installed

## Test Results

All tests are currently passing (7/7). The test suite verifies that all major features of DataSierra are working correctly.
