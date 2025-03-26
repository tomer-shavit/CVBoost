# Create a unique tag based on the current timestamp

tag=$(date +%s)

# Set ECR repo URI

repo_uri=416403043851.dkr.ecr.eu-west-3.amazonaws.com/resume-analyzer-lambda

# Confirm ECR repo exists (no error if it already does)

aws ecr describe-repositories --repository-names resume-analyzer-lambda --region eu-west-3 || \
aws ecr create-repository --repository-name resume-analyzer-lambda --region eu-west-3

# Build the production image

docker build -f Dockerfile.prod -t resume-analyzer-lambda-prod .

# Tag the image for ECR

docker tag resume-analyzer-lambda-prod:latest $repo_uri:$tag

# Authenticate Docker with ECR

aws ecr get-login-password --region eu-west-3 | docker login --username AWS --password-stdin $repo_uri

# Push the image to ECR

docker push $repo_uri:$tag

# Output final image URI

echo "Pushed image to: $repo_uri:$tag"
