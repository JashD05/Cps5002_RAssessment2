# Cps5002_RAssessment2/run_tests.py
import unittest
import sys
import os

def run_all_tests():
    """
    Discovers and runs all tests from the 'Techburg/test' directory.
    """
    # Add the 'Techburg' directory to the path so tests can import from it
    project_root = os.path.dirname(os.path.abspath(__file__))
    techburg_path = os.path.join(project_root, 'Techburg')
    sys.path.insert(0, techburg_path)

    # Create a Test Loader to find the tests
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='Techburg/test', pattern='test_*.py')
    
    # Create a Test Runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    print("--- Starting Full Test Suite ---")
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        print("--- TEST SUITE FAILED ---")
        sys.exit(1)

    print("--- Test Suite Completed Successfully ---")

if __name__ == '__main__':
    run_all_tests()