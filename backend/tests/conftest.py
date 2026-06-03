import pytest

# 1. Register a custom command line option '--target-url'
def pytest_addoption(parser):
    parser.addoption(
        "--target-url", 
        action="store", 
        default="http://localhost:8000", 
        help="The base URL of the ECU API service under test"
    )

@pytest.fixture
def base_url(request):
    return request.config.getoption("--target-url")
