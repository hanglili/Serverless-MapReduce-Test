from serverless_mr.main import ServerlessMR

from user_job_3.map import map_function
from user_job_3.reduce import reduce_function
from user_job_3.partition import partition

serverless_mr = ServerlessMR()
serverless_mr.map(map_function).set_partition_function(partition).reduce(reduce_function).run()
