# CVBoost - Resume Trigger Function

A serverless function that analyzes and enhances resumes using AI, with automatic language detection from content.

## Features

- **Automatic Language Detection**: Detects if the resume is in French or English and responds accordingly
- **Resume Enhancement**: Provides feedback and suggestions to improve the resume
- **Strict Validation**: Enforces PDF format, page limits, and language requirements with clear error messages
- **Multipart Form Support**: Properly handles multipart/form-data uploads
- **Binary Content Support**: Configured to handle PDF files correctly

## Deployment to AWS Lambda

### Prerequisites

1. Install the Serverless Framework:

   ```
   npm install -g serverless
   ```

2. Configure AWS credentials:

   ```
   serverless config credentials --provider aws --key YOUR_ACCESS_KEY --secret YOUR_SECRET_KEY
   ```

3. Install Python dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory with your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```

### Deployment

1. Use the deployment script:

   ```
   ./deploy.sh
   ```

   Or deploy manually:

   ```
   serverless deploy
   ```

2. After deployment, you'll receive an API endpoint URL that you can use to trigger the function.

### Local Testing

1. Install the Serverless Offline plugin:

   ```
   serverless plugin install -n serverless-offline
   ```

2. Run the function locally:

   ```
   serverless offline
   ```

3. Test the function with a sample request:

   ```
   # The language will be automatically detected from the resume content
   curl -X POST -F "resume=@./path/to/resume.pdf" -F "userId=test-user" http://localhost:3000/resume/boost

   # You can also explicitly specify a language
   curl -X POST -F "resume=@./path/to/resume.pdf" -F "userId=test-user" -F "language=fr" http://localhost:3000/resume/boost
   ```

## Function Structure

- `lambda_function.py`: AWS Lambda handler
- `main.py`: Core function logic
- `booster.py`: Resume enhancement logic
- `resume_parser.py`: PDF parsing functionality
- `file_check.py`: File validation and language detection

## API Endpoint

POST `/resume/boost`

### Request

- Content-Type: `multipart/form-data`
- Body:
  - `resume`: PDF file
  - `userId`: User identifier
  - `language`: Language code (optional, defaults to auto-detected language from resume content)

### Response

- Status: 200 OK
- Body: JSON with enhanced resume content
- Headers:
  - `Content-Language`: The language of the response (fr/en)

### Error Responses

- Status: 400 Bad Request
- Body: JSON with error details
  ```json
  {
    "error": "Detailed error message explaining the validation failure"
  }
  ```

## Validation Rules

The function enforces the following validation rules:

1. **PDF Format**: The uploaded file must be a valid PDF
2. **Page Limit**: The resume must not exceed 2 pages
3. **Text Content**: The PDF must contain extractable text
4. **Language Validation**: If a specific language is requested, the content must match that language

## Automatic Language Detection

The function automatically detects the language of the resume content:

1. If the content is in French, the function will respond in French
2. For all other languages, the function will respond in English

You can override this by explicitly setting the 'language' parameter in your request.

## Error Messages

All error messages are in English regardless of the detected or specified language. Error messages are specific and descriptive to help troubleshoot issues.

## Troubleshooting

If you encounter issues:

1. Check that your PDF is valid and has at most 2 pages
2. Ensure your OpenAI API key is correctly set in the .env file
3. Verify that the multipart/form-data request is properly formatted
4. Check the CloudWatch logs for detailed error information

## Testing

The application includes comprehensive test coverage for all components:

### Test Files

- `test_validation.py`: Tests for PDF validation functionality
- `test_lambda_handler.py`: Tests for the AWS Lambda handler
- `test_main.py`: Tests for the core processing logic
- `test_file_check.py`: Tests for file validation and language detection

### Running Tests

To run all tests:

```
cd Functions/ResumeTrigger
python run_tests.py
```

To run individual test files:

```
python -m unittest ResumeTrigger.test_validation
python -m unittest ResumeTrigger.test_lambda_handler
python -m unittest ResumeTrigger.test_main
python -m unittest ResumeTrigger.test_file_check
```

The tests use mocking to simulate PDF processing and API interactions, ensuring that all validation logic and error handling are properly tested.
