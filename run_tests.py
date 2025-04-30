import unittest
import sys
import os

def run_tests():
    # Create tests directory if it doesn't exist
    if not os.path.exists('tests'):
        os.makedirs('tests')
        # Create an __init__.py file to make the directory a package
        with open('tests/__init__.py', 'w') as f:
            pass
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    print("\n===== Running OpenRouter Chat API Tests =====\n")
    
    # Check if server is running
    import requests
    try:
        response = requests.get("http://127.0.0.1:8000/docs")
        if response.status_code != 200:
            print("\nWARNING: API server might not be running. Start the server with 'uvicorn app.main:app --reload'\n")
    except requests.exceptions.ConnectionError:
        print("\nWARNING: API server is not running. Start the server with 'uvicorn app.main:app --reload'\n")
    
    # Run the tests
    sys.exit(run_tests())
