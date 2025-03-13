# Resume Parser Lambda - Container-Based

This project deploys a Resume Parser as an AWS Lambda function using container-based deployment. This approach ensures that all dependencies, including those with native extensions like PyMuPDF, work correctly in the Lambda environment.

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed and running
- [AWS CLI](https://aws.amazon.com/cli/) installed and configured with appropriate permissions
- PowerShell (for Windows users)

## Setup

1. Make sure you have the prerequisites installed
2. Ensure your AWS CLI is configured with credentials that have permissions to:
   - Create and push to ECR repositories
   - Create and update Lambda functions
   - Assume the Lambda execution role

## Deployment

Run the deployment script:

```powershell
./deploy-lambda-container.ps1
```

### Optional Parameters

You can customize the deployment with the following parameters:

```powershell
./deploy-lambda-container.ps1 -Region "us-west-2" -RepositoryName "my-repo" -FunctionName "MyFunction"
```

- `-Region`: AWS region (default: "us-east-1")
- `-RepositoryName`: ECR repository name (default: "resume-parser-lambda")
- `-FunctionName`: Lambda function name (default: "ResumeParserFunction")

## Lambda Configuration

After deployment, you may need to:

1. Configure an API Gateway trigger if you want to invoke the function via HTTP
2. Set up environment variables in the Lambda console
3. Configure the Lambda function's memory and timeout in the Lambda console:
   - Recommended memory: 512 MB or higher
   - Recommended timeout: 30-90 seconds (for PDF processing)

## IAM Role

Your Lambda function needs an execution role with at least these permissions:

- `AWSLambdaBasicExecutionRole`: For CloudWatch Logs
- S3 permissions if your function interacts with S3 buckets

## Local Testing

To test the container locally before deployment:

```bash
docker build -t resume-parser-lambda .
docker run -p 9000:8080 resume-parser-lambda
```

Then invoke it with:

```bash
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

## Troubleshooting

- **Build errors**: Check Docker logs and ensure all dependencies are available
- **Runtime errors**: Check CloudWatch logs for the Lambda function
- **Permission errors**: Verify IAM roles have the necessary permissions
- **Memory/timeout issues**: Increase Lambda memory allocation and timeout

## Benefits of Container-Based Approach

- Native extensions work correctly without complex packaging
- Consistent environment between development and production
- No need for complex fallback implementations
- Easier dependency management
