import json
import boto3
import traceback
from time import time

code_pipeline = boto3.client('codepipeline')

def lambda_handler(event, context):

    # Get the CodePipeline ID
    job_id = event['CodePipeline.job']['id']
    
    # Get the user parameters from the pipeline
    items = event['CodePipeline.job']['data']['actionConfiguration']['configuration']['UserParameters']
    user_parameters = json.loads(items)
    cloudfrontId = user_parameters.get("distributionId")
    invalidation_paths = user_parameters.get("invalidationPaths").split(',')
    print("CloudFrontId: " + cloudfrontId)
    print("InvalidationPaths")
    
    for item in invalidation_paths:
        print(item)
    
    # Attempt to invalidate CloudFront Cache and notify the pipeline when done
    try:
        # Invalidate Website files in CloudFront
        invalidate_cloudfront(cloudfrontId,invalidation_paths)

        # Notify CodePipeline of Success
        print("Site Updated")
        code_pipeline.put_job_success_result(jobId=job_id)
        
    except Exception:

        # Create and print error message
        failure_message = "An error occured when trying to invalidate objects in CloudFront"
        print(failure_message)

        # Print the traceback
        traceback.print_exc()

        # Notify CodePipeline of Failure
        code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={'message': failure_message, 'type': 'JobFailed'})

    finally:
        return "Done"


def invalidate_cloudfront(cloudfront_id,invalidation_paths):
    # Invalidate CloudFront Objects
    client = boto3.client("cloudfront")
    
    response = client.create_invalidation(
        DistributionId = cloudfront_id,
        InvalidationBatch = {
            'Paths': {
                'Quantity': len(invalidation_paths),
                'Items': invalidation_paths
            },
        'CallerReference': str(time()).replace(".", "")
        })
        
    print(response)