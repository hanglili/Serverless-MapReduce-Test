from serverless_mr.main import ServerlessMR


from multi_pipeline.map import extract_data_dynamo_db
from multi_pipeline.map_2 import extract_data_s3
from multi_pipeline.reduce import reduce_function
from multi_pipeline.partition import partition
from multi_pipeline.map_3 import identity_function

serverless_mr = ServerlessMR()

# serverless_mr.map(extract_data_s3).map(identity_function).reduce(reduce_function, 4).\
#     map(identity_function).reduce(reduce_function, 5).run()

config_pipeline_1 = {
    "inputSourceType": "s3",
    "inputSource": "serverless-mapreduce-input-storage",
    "inputPrefix": "testing_partitioned"
}

config_pipeline_2 = {
    "inputSourceType": "dynamodb",
    "inputSource": "serverless-mapreduce-storage-input",
    "inputPartitionKeyDynamoDB": ["recordId", "N"],
    "inputProcessingColumnsDynamoDB": [["sourceIP", "S"], ["adRevenue", "N"]]
}

pipeline1 = serverless_mr.config(config_pipeline_1).map(extract_data_s3).combine(reduce_function)\
    .reduce(reduce_function, 4).finish()

pipeline2 = serverless_mr.config(config_pipeline_2).map(extract_data_dynamo_db)\
    .reduce(reduce_function, 2).finish()

pipeline3 = serverless_mr.merge([pipeline1, pipeline2]).map(identity_function)\
    .shuffle(partition).reduce(reduce_function, 5).run()
