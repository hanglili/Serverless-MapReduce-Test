from serverless_mr.main import ServerlessMR

from user_job.map import map_function
from user_job.reduce import reduce_function
from user_job.partition import partition

serverless_mr = ServerlessMR()
serverless_mr.set_map_function(map_function)
serverless_mr.set_reduce_function(reduce_function)
serverless_mr.set_partition_function(partition)

serverless_mr.run_job()
