deploy commands:

$tag = [int](Get-Date -UFormat %s)

echo "416403043851.dkr.ecr.eu-west-3.amazonaws.com/resume-analyzer-lambda:$tag"

# Confirm repo exists (no error if it does)

aws ecr describe-repositories --repository-names resume-analyzer-lambda --region eu-west-3

# Tag local image with unique tag

docker tag resume-analyzer-lambda:latest 416403043851.dkr.ecr.eu-west-3.amazonaws.com/resume-analyzer-lambda:$tag

# Push to ECR

docker push 416403043851.dkr.ecr.eu-west-3.amazonaws.com/resume-analyzer-lambda:$tag
