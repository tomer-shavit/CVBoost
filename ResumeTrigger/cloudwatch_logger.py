import logging
import watchtower
import boto3
from datetime import datetime
import os

# Constants for logging configuration
LOG_GROUP = "/aws/lambda/resume-analyzer-lambda"  # The CloudWatch log group
APP_NAME = "CVBoost"  # Application name for log stream identification
AWS_REGION = "eu-west-3"  # AWS region

# Check if CloudWatch logging should be enabled
ENABLE_CLOUDWATCH = os.environ.get('ENABLE_CLOUDWATCH', 'FALSE').upper() == 'TRUE'

def setup_logging(logger_name=None, level=logging.INFO, user_id=None):
    """
    Set up basic logging with optional CloudWatch integration for critical areas.
    """
    # Get the logger
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()  # Root logger
    
    # Set the log level
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers = []
    
    # Create log formatter - simple format for readability
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    # Create a stream handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Only set up CloudWatch logging if explicitly enabled and in AWS environment
    if ENABLE_CLOUDWATCH and (os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or os.environ.get('AWS_EXECUTION_ENV')):
        try:
            # Create a unique log stream name with timestamp and user ID
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            log_stream_name = f"{APP_NAME}-{timestamp}"
            if user_id:
                log_stream_name = f"{log_stream_name}-{user_id}"
            
            # Create CloudWatch handler
            cw_handler = watchtower.CloudWatchLogHandler(
                log_group=LOG_GROUP,
                stream_name=log_stream_name,
                boto3_client=boto3.client('logs', region_name=AWS_REGION)
            )
            cw_handler.setFormatter(formatter)
            logger.addHandler(cw_handler)
        except Exception as e:
            logger.error(f"Failed to set up CloudWatch logging: {str(e)}")
    
    return logger

def get_logger(module_name, user_id=None):
    """
    Get a logger for a specific module with optional CloudWatch integration.
    """
    return setup_logging(module_name, user_id=user_id) 