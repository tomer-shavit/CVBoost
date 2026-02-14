# CVBoost

AI-powered resume analyzer that scores your resume across key dimensions and suggests line-by-line improvements using GPT-4o.

## What It Does

Upload a PDF resume and get back:

- **Scores (0-100)** on clarity, relevance, achievements, and keywords
- **Line-by-line rewrites** — concrete suggestions for stronger phrasing
- **General feedback** — overall pros, cons, and a summary
- **Bilingual support** — auto-detects French and English

## Architecture

```
Client → API Gateway → AWS Lambda (Docker)
                            │
                    ┌───────┴───────┐
                    ▼               ▼
              OpenAI GPT-4o    AWS SSM
              (analysis)     (API key)
                    │
                    ▼
             CloudWatch Logs
```

The Lambda runs two GPT-4o calls concurrently — one for scoring/feedback, one for line rephrasing — then merges the results into a single response.

## Tech Stack

- **Python 3.11** on AWS Lambda (containerized)
- **OpenAI GPT-4o** with function calling for structured output
- **PyMuPDF** for PDF text extraction
- **langdetect** for language detection
- **AWS SSM** for secrets, **CloudWatch** for logging

## Project Structure

```
ResumeTrigger/
├── lambda_function.py    # Lambda entry point, request parsing
├── main.py               # Orchestration — validation, concurrent processing
├── booster.py            # Core AI logic — feedback + rephrase
├── resume_parser.py      # PDF text extraction (PyMuPDF)
├── file_check.py         # PDF validation, language detection
├── gpt_api_caller.py     # OpenAI API wrapper
├── prompt_factory.py     # Multilingual prompt generation
├── cloudwatch_logger.py  # CloudWatch logging setup
├── constants.py          # Enums
├── internal_types/       # TypedDict definitions
│   ├── feedback_dict.py
│   ├── feedback_function.py
│   ├── edited_lines.py
│   └── rephrase_functions.py
└── requirements.txt
```

## Local Development

### Prerequisites

- Docker
- OpenAI API key

### Run locally

```bash
# Build the local image (includes Lambda Runtime Interface Emulator)
docker build -f Dockerfile.local -t cvboost-local .

# Run it
docker run -p 9000:8080 -e GPT_API_KEY1=sk-... cvboost-local
```

### Test with a PDF

```bash
# Direct invocation
python test_lambda_locally.py path/to/resume.pdf

# With options: user_id, language, method (1=direct, 2=API Gateway style)
python test_lambda_locally.py resume.pdf user-123 fr 2
```

Or call the endpoint directly:

```bash
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "body": "{\"resume\": \"<base64-encoded-pdf>\", \"userId\": \"user-123\"}"
  }'
```

## API

### Request

**POST** with JSON body or multipart/form-data:

| Field      | Type   | Required | Description                              |
|------------|--------|----------|------------------------------------------|
| `resume`   | string | Yes      | Base64-encoded PDF                       |
| `userId`   | string | Yes      | User identifier                          |
| `language` | string | No       | `fr` or `en` — auto-detected if omitted  |

### Response

```json
{
  "statusCode": 200,
  "body": {
    "edited_lines": [
      {
        "feedback_type": 1,
        "data": {
          "old_line": "Worked on projects",
          "new_line": "Led 3 cross-functional projects delivering 20% efficiency gains"
        }
      }
    ],
    "clarity":     { "feedback_type": 2, "data": { "feedback": "...", "score": 78 } },
    "relevance":   { "feedback_type": 3, "data": { "feedback": "...", "score": 85 } },
    "achievements": { "feedback_type": 4, "data": { "feedback": "...", "score": 62 } },
    "keywords":    { "feedback_type": 5, "data": { "feedback": "...", "score": 71 } },
    "general_feedback": { "feedback_type": 6, "data": { "feedback": "..." } },
    "resume_text": "Full extracted text..."
  }
}
```

### Validation rules

- PDF format only (checks `%PDF-` header)
- Max 2 pages
- Must contain extractable text (no image-only PDFs)

## Deploy to AWS

### Prerequisites

- AWS CLI configured with access to ECR, Lambda, and SSM
- OpenAI API key stored in SSM Parameter Store as `GPT_API_KEY1` (region: `eu-west-3`)

### Deploy

```bash
./deploy.sh
```

This builds the production Docker image, pushes it to ECR, and outputs the image URI. Update your Lambda function to point to the new image:

```bash
aws lambda update-function-code \
  --function-name resume-analyzer-lambda \
  --image-uri <image-uri-from-deploy-output> \
  --region eu-west-3
```

## License

MIT
