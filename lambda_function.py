# lambda_function.py
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    AWS Lambda handler that prints all request information.
    Compatible with Lambda base image public.ecr.aws/lambda/python:3.12
    """

    # Log the raw incoming event and context
    logger.info("=== Incoming Event ===")
    logger.info(json.dumps(event, indent=2))

    logger.info("=== Context Information ===")
    logger.info(
        json.dumps(
            {
                "aws_request_id": context.aws_request_id,
                "function_name": context.function_name,
                "function_version": context.function_version,
                "invoked_function_arn": context.invoked_function_arn,
                "memory_limit_in_mb": context.memory_limit_in_mb,
                "log_group_name": context.log_group_name,
                "log_stream_name": context.log_stream_name,
            },
            indent=2,
        )
    )

    # Compose response
    response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "message": "Request received by Lambda container",
                "event": event,
                "context": {
                    "request_id": context.aws_request_id,
                    "function_name": context.function_name,
                },
            },
            indent=2,
        ),
    }

    return response
