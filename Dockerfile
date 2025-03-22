FROM public.ecr.aws/lambda/python:3.11

# Copy dependencies and the entire project
WORKDIR ${LAMBDA_TASK_ROOT}
COPY . .

# Install requirements and the package itself
RUN pip install -r ResumeTrigger/requirements.txt
RUN pip install -e .

# Explicitly set Lambda handler
ENTRYPOINT ["python", "-m", "awslambdaric"]
CMD ["ResumeTrigger.lambda_function.lambda_handler"]