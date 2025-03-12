import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from ResumeTrigger.main import boost_resume_to_json
    from ResumeTrigger.file_check import PDFValidationError
    from ResumeTrigger.test_result import FileTestResult
except ImportError:
    print("Error importing ResumeTrigger modules. Make sure the path is correct.")
    sys.exit(1)

class TestMain(unittest.TestCase):
    
    def setUp(self):
        # Create sample PDF content for testing
        self.valid_pdf_content = b'%PDF-1.5\nsome pdf content'
        self.invalid_content = b'not a pdf'
        
        # Create sample test results
        self.valid_test_result = FileTestResult(True, FileTestResult.DEFAULT, "")
        self.invalid_test_result = FileTestResult(False, FileTestResult.TYPE, "The content is not a valid PDF file.")
        
        # Create sample booster
        self.mock_booster = MagicMock()
        self.mock_booster.make_json.return_value = '{"result": "success"}'
    
    @patch('ResumeTrigger.main.detect_language_from_content')
    @patch('ResumeTrigger.main.is_valid_resume')
    @patch('ResumeTrigger.main.ResumeParser')
    @patch('ResumeTrigger.main.Booster')
    def test_boost_resume_to_json_success(self, mock_booster_class, mock_parser_class, mock_is_valid_resume, mock_detect_language):
        """Test that boost_resume_to_json returns a successful response when all validations pass"""
        # Set up mocks
        mock_detect_language.return_value = "en"
        mock_is_valid_resume.return_value = self.valid_test_result
        
        mock_parser = MagicMock()
        mock_parser.resume_text = "Sample resume text"
        mock_parser_class.return_value = mock_parser
        
        mock_booster = self.mock_booster
        mock_booster_class.return_value = mock_booster
        
        # Call the function
        result = boost_resume_to_json(self.valid_pdf_content, "test-user")
        
        # Check the result
        self.assertEqual(result, (True, 200, '{"result": "success"}', "en"))
        
        # Verify the mocks were called correctly
        mock_detect_language.assert_called_once_with(self.valid_pdf_content)
        mock_is_valid_resume.assert_called_once_with(self.valid_pdf_content, "en")
        mock_parser_class.assert_called_once_with(self.valid_pdf_content)
        mock_booster_class.assert_called_once_with("test-user", "Sample resume text", language="en")
    
    @patch('ResumeTrigger.main.detect_language_from_content')
    @patch('ResumeTrigger.main.is_valid_resume')
    def test_boost_resume_to_json_validation_failure(self, mock_is_valid_resume, mock_detect_language):
        """Test that boost_resume_to_json returns a validation error when validation fails"""
        # Set up mocks
        mock_detect_language.return_value = "en"
        mock_is_valid_resume.return_value = self.invalid_test_result
        
        # Call the function
        result = boost_resume_to_json(self.invalid_content, "test-user")
        
        # Check the result
        self.assertEqual(result, (False, 400, "The content is not a valid PDF file.", "en"))
        
        # Verify the mocks were called correctly
        mock_detect_language.assert_called_once_with(self.invalid_content)
        mock_is_valid_resume.assert_called_once_with(self.invalid_content, "en")
    
    @patch('ResumeTrigger.main.detect_language_from_content')
    @patch('ResumeTrigger.main.is_valid_resume')
    @patch('ResumeTrigger.main.ResumeParser')
    @patch('ResumeTrigger.main.Booster')
    def test_boost_resume_to_json_processing_exception(self, mock_booster_class, mock_parser_class, mock_is_valid_resume, mock_detect_language):
        """Test that boost_resume_to_json returns a server error when processing fails"""
        # Set up mocks
        mock_detect_language.return_value = "en"
        mock_is_valid_resume.return_value = self.valid_test_result
        
        mock_parser = MagicMock()
        mock_parser.resume_text = "Sample resume text"
        mock_parser_class.return_value = mock_parser
        
        mock_booster = MagicMock()
        mock_booster.make_json.side_effect = Exception("Processing error")
        mock_booster_class.return_value = mock_booster
        
        # Call the function
        result = boost_resume_to_json(self.valid_pdf_content, "test-user")
        
        # Check the result
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], 500)
        self.assertEqual(result[3], "en")
        
        # Verify the mocks were called correctly
        mock_detect_language.assert_called_once_with(self.valid_pdf_content)
        mock_is_valid_resume.assert_called_once_with(self.valid_pdf_content, "en")
        mock_parser_class.assert_called_once_with(self.valid_pdf_content)
        mock_booster_class.assert_called_once_with("test-user", "Sample resume text", language="en")
    
    @patch('ResumeTrigger.main.detect_language_from_content')
    @patch('ResumeTrigger.main.is_valid_resume')
    @patch('ResumeTrigger.main.ResumeParser')
    @patch('ResumeTrigger.main.Booster')
    def test_boost_resume_to_json_explicit_language(self, mock_booster_class, mock_parser_class, mock_is_valid_resume, mock_detect_language):
        """Test that boost_resume_to_json uses the explicit language when provided"""
        # Set up mocks
        mock_detect_language.return_value = "en"
        mock_is_valid_resume.return_value = self.valid_test_result
        
        mock_parser = MagicMock()
        mock_parser.resume_text = "Sample resume text"
        mock_parser_class.return_value = mock_parser
        
        mock_booster = self.mock_booster
        mock_booster_class.return_value = mock_booster
        
        # Call the function with explicit language
        result = boost_resume_to_json(self.valid_pdf_content, "test-user", "fr")
        
        # Check the result
        self.assertEqual(result, (True, 200, '{"result": "success"}', "fr"))
        
        # Verify the mocks were called correctly
        mock_detect_language.assert_called_once_with(self.valid_pdf_content)
        mock_is_valid_resume.assert_called_once_with(self.valid_pdf_content, "fr")
        mock_parser_class.assert_called_once_with(self.valid_pdf_content)
        mock_booster_class.assert_called_once_with("test-user", "Sample resume text", language="fr")
    
    @patch('ResumeTrigger.main.detect_language_from_content')
    def test_boost_resume_to_json_language_detection_error(self, mock_detect_language):
        """Test that boost_resume_to_json handles language detection errors"""
        # Set up mocks
        mock_detect_language.side_effect = PDFValidationError("Error detecting language")
        
        # Call the function
        result = boost_resume_to_json(self.invalid_content, "test-user")
        
        # Check the result
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], 400)
        self.assertEqual(result[3], "en")
        
        # Verify the mocks were called correctly
        mock_detect_language.assert_called_once_with(self.invalid_content)

if __name__ == '__main__':
    unittest.main() 