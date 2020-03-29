# from serverless_mr import *
from serverless_mr.static.static_variables import StaticVariables
from serverless_mr.job.map_handler import map_handler

import subprocess
import os

print(os.getcwd())
print(subprocess.run('pwd'))
print("*********serverless_mr*********")
print(subprocess.run(['ls', 'serverless_mr']))
print("*********serverless_mr.job*********")
print(subprocess.run(['ls', 'serverless_mr/job']))
print("*********serverless_mr.job.map_handler*********")
print(subprocess.run(['cat', 'serverless_mr/job/map_handler.py']))

print(StaticVariables.SERVERLESS_MR_INIT_PATH)

@map_handler
def map_function(outputs, input_pair):
    """
    :param outputs: [(k2, v2)] where k2 and v2 are intermediate data
    which can be of any types
    :param input_pair: (k1, v1) where k1 and v1 are assumed to be of type string
    """
    try:
        _, line = input_pair
        data = line.split(',')
        src_ip = data[0]
        ad_revenue = float(data[3])
        outputs.append(tuple((src_ip, ad_revenue)))
    except Exception as e:
        print("type error: " + str(e))

