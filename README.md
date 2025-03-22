deploy commands:

echo "416403043851.dkr.ecr.eu-west-3.amazonaws.com/resume-analyzer-lambda:latest"

aws ecr describe-repositories --repository-names resume-analyzer-lambda --region eu-west-3

docker images resume-analyzer-lambda

docker tag resume-analyzer-lambda:latest 416403043851.dkr.ecr.eu-west-3.amazonaws.com/resume-analyzer-lambda:latest

docker push 416403043851.dkr.ecr.eu-west-3.amazonaws.com/resume-analyzer-lambda:latest
