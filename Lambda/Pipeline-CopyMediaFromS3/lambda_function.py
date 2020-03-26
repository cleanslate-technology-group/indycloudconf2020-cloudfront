import boto3
import json

code_pipeline = boto3.client('codepipeline')

def copy_s3_buckets(source_bucket,destination_bucket):
    
    s3_client = boto3.client("s3")
    s3_resource = boto3.resource("s3")
    
    print("In the copy function now")
    
    for item in s3_client.list_objects(Bucket=source_bucket).get("Contents"):
        items = item.get("Key")
        print(items)
        copy_source = {'Bucket': source_bucket, 'Key':items}
        s3_resource.meta.client.copy(copy_source,destination_bucket,items)

def lambda_handler(event, context):
    
    # Get the CodePipeline ID
    job_id = event['CodePipeline.job']['id']
    
    user_parameters = json.loads(event['CodePipeline.job']['data']['actionConfiguration']['configuration']['UserParameters'])
    source_bucket = user_parameters.get("sourceBucket")
    destination_bucket = user_parameters.get("destinationBucket")
    print("JobId: " + job_id)
    print("Source: " + source_bucket)
    print("Destination: " + destination_bucket) 
    
    
    # Attempt to invalidate CloudFront Cache and notify the pipeline when done
    try:
        # Invalidate Website files in CloudFront
        print("About to start the copy")
        copy_s3_buckets(source_bucket,destination_bucket)

        # Notify CodePipeline of Success
        print("S3 Files Copied")
        code_pipeline.put_job_success_result(jobId=job_id)
        print("Printed Job Sucess")
        
    except Exception:

        # Create and print error message
        failure_message = f"An error occured when trying to copy files between {source_bucket} to the {destination_bucket}"
        print(failure_message)

        # Notify CodePipeline of Failure
        code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={'message': failure_message, 'type': 'JobFailed'})

    finally:
        return "Done"

