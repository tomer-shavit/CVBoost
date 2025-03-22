FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY ResumeTrigger/requirements.txt .
RUN pip install -r requirements.txt

# Copy the entire package preserving structure
COPY ResumeTrigger/ /var/task/ResumeTrigger

# Download RIE
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/local/bin/aws-lambda-rie
RUN chmod +x /usr/local/bin/aws-lambda-rie

# Set RIE as entrypoint for local runs
ENTRYPOINT ["/usr/local/bin/aws-lambda-rie", "/var/runtime/bootstrap"]

CMD ["ResumeTrigger.lambda_function.lambda_handler"]