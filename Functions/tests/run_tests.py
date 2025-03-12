#!/usr/bin/env python3
import unittest
import os
import sys
import importlib
import inspect

def discover_and_run_tests():
    """Discover and run all test cases in the tests directory"""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the parent directory to the path so we can import the modules
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    
    print(f"Added {parent_dir} to sys.path")
    print(f"Current sys.path: {sys.path}")
    
    # Try to import a ResumeTrigger module to check if the path is correct
    try:
        import ResumeTrigger.file_check
        print("Successfully imported ResumeTrigger.file_check")
    except ImportError as e:
        print(f"Error importing ResumeTrigger.file_check: {e}")
        print("Make sure the ResumeTrigger module is in the correct location.")
        return None
    
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Walk through the tests directory and find all test files
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                # Convert file path to module path
                rel_path = os.path.relpath(os.path.join(root, file), os.path.dirname(current_dir))
                module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
                
                try:
                    # Import the module
                    module = importlib.import_module(module_path)
                    
                    # Find all test classes in the module
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, unittest.TestCase) and name.startswith('Test'):
                            # Add the test class to the suite
                            test_suite.addTest(unittest.makeSuite(obj))
                            print(f"Added test class: {name} from {module_path}")
                except ImportError as e:
                    print(f"Error importing {module_path}: {e}")
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result

if __name__ == '__main__':
    print("Running all tests for the Resume Trigger function...")
    result = discover_and_run_tests()
    
    if result is None:
        print("Failed to run tests due to import errors.")
        sys.exit(1)
    
    # Print summary
    print("\nTest Summary:")
    print(f"Ran {result.testsRun} tests")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Exit with appropriate code
    if result.wasSuccessful():
        print("\nAll tests passed successfully!")
        sys.exit(0)
    else:
        print("\nSome tests failed. See details above.")
        sys.exit(1) 