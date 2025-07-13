import os

def get_aws_region():
    """
    Get the AWS region from environment variables with a fallback to a default value.
    
    Returns:
        str: The AWS region to use for AWS services.
    """
    return os.environ.get('AWS_REGION', 'us-west-2')
