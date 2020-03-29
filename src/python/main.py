import boto3
import json


from serverless_mr.static.static_variables import StaticVariables
from serverless_mr.main import init_job
# from job.map import map_function

# s3_client = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='',
#                          region_name=StaticVariables.DEFAULT_REGION,
#                          endpoint_url='http://localhost:4572')
# static_job_info = json.loads(open(StaticVariables.STATIC_JOB_INFO_PATH, 'r').read())

# Execute the job
init_job(['python3', '0'])
print("The job has finished")

# Output
# output_bin = 3
# output_prefix = static_job_info['outputPrefix']
# output_bucket = static_job_info['outputBucket']
# output_filepath = "%s%s" % (output_prefix, str(output_bin))
# response = s3_client.get_object(Bucket=output_bucket, Key=output_filepath)
# contents = response['Body'].read()
# results = json.loads(contents)


# input_pair = (1, '127.0.0.1, null, null, 10.2')
# outputs = []
# map_function.__wrapped__(outputs, input_pair)
# print(outputs)
