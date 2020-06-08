# Serverless-MR-Test

This project is a data processing example job that uses the library ServerlessMR and it aims to demonstrate 
how one could use this library to quickly set up any data processing job. ServerlessMR is a big data MapReduce 
framework that leverages serverless functions to allow processing of large data sets in a completely serverless architecture. 
Currently it supports AWS serverless functions (AWS Lambda).


## Quickstart::Step by Step
### Executing a job
1. Create a python project and then create a directory with the name ```src``` at the root-level directory of the project. 
In ```src/```, create a python module with name ```python```. Note that the name `python` can be replaced by any other names. 
Then in this module, create a module called ```configuration```. Remember that a module in Python is 
a directory that contains the file ```__init__.py```.
2. Run the command: ```pip install -i https://test.pypi.org/simple/ serverless-mr``` to install the `serverless_mr` library.
3. Write map, reduce, combine and partition functions anywhere inside your project directory (```src/python/```).
4. In ```configuration/```, create the job configuration file `static-job-info.json`. Note that another 
configuration file `driver.json` can be added to this module if you want to specify configuration parameters for AWS 
resources such as memory limit of Lambda. 
    - `static-job-info.json`: records information of a job. You can adapt `static-job-info.json` of
    this project to your own job. For information on the fields of this configuration files, check out 
    the section of Job Configuration Fields below. 
    - `driver.json` (optional): records properties of provisioned AWS Lambda. For information on the 
    fields of this configuration files, check out: https://github.com/hanglili/Serverless-MapReduce/blob/master/src/python/notes
5. Create a main python script under `src/python/` which sets up
the job (This is ServerlessMR equivalent of Hadoop driver class).
6. (Optional) If you want to execute your job locally before deploying and executing it on AWS, you can do so as follows:
    1. Setting `true` to the field `localTesting` in `static-job-info.json`.
    2. Install the library `localstack` by running the command `pip install localstack`.
    3. Start docker and pull the docker container for `localstack` by running the command `docker pull localstack/localstack`.
    4. To run localstack (which simulates different AWS services behaviours) using the command: 
    ```TMPDIR=/private$TMPDIR SERVICES=serverless LAMBDA_EXECUTOR=docker LAMBDA_REMOVE_CONTAINERS=false DOCKER_HOST=unix:///var/run/docker.sock  DEBUG=1 localstack start --docker```
    5. To run AWS Lambda on a docker container, pull the docker image lambci by running the command: `docker pull lambci/lambda`.
    6. Set any value (for example, `dummy-role`) to environmental variable `serverless_mapreduce_role`.
    7. Run the main script that you have created in step 5, with `src/python/` configured as the working directory.
7. To deploy and execute this job on the cloud (AWS), follow this series of steps:
    1. Set your AWS credentials by storing your credentials under the file `credentials ` in `~/.aws/` directory.
    2. Adapt `policy.json` in the library module to using your AWS Account ID. 
    3. To create an AWS IAM role, run the script `create-biglambda-role.py` in the library module. 
    4. Set the environment variable `serverless_mapreduce_role` to the name of the created role.
    5. Run the main function that you have created in step 5, with `src/python/` configured as the working directory.

### Spin up the Web Application
1. Make sure to have your `serverless_mapreduce_role` set to the name of the created AWS IAM role.
2. Do `npm install` to install node dependencies for the tool serverless. 
3. On the library directory where `serverless.yml` is defined, run the following command: `sls deploy`. This step
will take a few minutes (2 mins usually) and upon termination, it will output the URL of the web app. 
4. To kill the web app, run: `sls remove` on the same directory as step 3. 

### Clean up
1. To delete the role created, run the script `delete-biglambda-role.py` in the library module. 

### Tests
Apart from manually executing your code locally as described in the previous section, you can also write tests.
These include unit tests and end-to-end tests. Unit tests can be used to test whether your provided
functions behave as expected. End-to-end tests automate the manual process of testing your code locally in an end-to-end manner
using localstack. 

The module `tests` which contains the test files should be in the module `src/python`. When running end-to-end tests, 
remember to start docker and localstack. Apart from that, make sure to run these test scripts with the working directory
configured as `src/python`.

To understand how these unit tests and end-to-end tests are written, look at the directory `src/python/tests` in this project.

The directory path of the input data is provided in the field `localTestingInputPath` of `static-job-info.json` and 
has to be relative to `src/python/`.

## Job:
This example job tries to aggregate the revenue generated by each ip address, given the input data. The output format is 
[ip, revenue] and each input line is of the form:
```
sourceIP VARCHAR(116), destURL VARCHAR(100), visitDate DATE, adRevenue FLOAT, userAgent VARCHAR(256), 
countryCode CHAR(3), languageCode CHAR(6), searchWord VARCHAR(32), duration INT
```
for example: 
```
0.0.0.0,djecvwmjzejguvrqaryffwwzdasozsslizligyozikvhdeodyvsnotlkldsuvtbcmzajlfdqoopeiqrpfhqhneqrpzdzrgshthe,1974-12-17,10,Xegqzir/8.7,PRT,PRT-PT,Portugalism,7
```

The map function takes an input pair of (input key, input value). In this case, since the input data comes from S3, the
input pair is of form (S3 object key, S3 object contents). This map function splits the input document into lines which are further 
split using `,`. Afterwards, it generates the intermediate data from each of these lines. The intermediate data is a list of type 
(src_ip, ad_revenue). The code is shown below:
```
def map_function(outputs, input_pair):
    """
    :param outputs: [(k2, v2)] where k2 and v2 are intermediate data which can be of any type.
    :param input_pair: (k1, v1) where k1 and v1 are assumed to be of type string.
    """

    try:
        _, input_value = input_pair
        lines = input_value.split('\n')[:-1]

        for line in lines:
            data = line.split(',')
            src_ip = data[0]
            ad_revenue = float(data[3])
            outputs.append(tuple((src_ip, ad_revenue)))

    except Exception as e:
        print("type error: " + str(e))

``` 

The partition function hashes a key using sha256 and then changes this hashed key to a value between 0 and 
(num_bins - 1) by performing modulus operation on the hashed key with the number of bins. The code is shown below:
```
def partition(key, num_bins):
    """
    :param key: key of intermediate data which can be of any type.
    :param num_bins: number of bins that a key could be partitioned to (this is equal to number of reducers).
    :returns an integer that denotes the bin assigned to this key.
    """

    key_hashed = int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16) % 10**8
    return key_hashed % num_bins
```

The reduce function receives an intermediate pair of (src_ip, [ad_revenues]) and aggregates the ad_revenues for 
this source ip by summing them up. The code is shown below:
```
def reduce_function(outputs, intermediate_data):
    """
    :param outputs: [(k3, v3)] where k3 and v3 are output data which can be of any type.
    :param intermediate_data: (k2, [v2]) where k2 and v2 are intermediate data which can be of any type.
    """

    key, values = intermediate_data

    revenue_sum = 0
    try:
        for value in values:
            revenue_sum += float(value)

        outputs.append((key, [revenue_sum]))
    except Exception as e:
        print("type error: " + str(e))

``` 
The job's main file and its `static-job-info.json` can be found in `src/python` of this project. 

## Job Configuration Fields
All job-related information is specified in the configuration file `configuration/static-job-info.json`. Note that
depending on the input and output storage types, different configuration fields needed to be provided. Below are all
the configuration fields with their expected types:

| Field Names                    | Requirement                                               | Example                                                                        |
|--------------------------------|-----------------------------------------------------------|--------------------------------------------------------------------------------|
| jobName                        | Required                                                  | "bl-release"                                                                   |
| lambdaNamePrefix               | Required                                                  | "BL"                                                                           |
| shufflingBucket                | Required                                                  | "serverless-mapreduce-storage"                                                 |
| inputSourceType                | Required                                                  | "s3"                                                                           |
| inputSource                    | Required                                                  | "serverless-mapreduce-storage-input"                                           |
| inputPrefix                    | S3 specific                                               | "testing_partitioned"                                                          |
| inputPartitionKeyDynamoDB      | DynamoDB specific                                         | ["recordId", "N"]                                                              |
| inputSortKeyDynamoDB           | DynamoDB specific - optional                              | ["timeProcessed", "N"]                                                         |
| inputProcessingColumnsDynamoDB | DynamoDB specific                                         | [["sourceIP", "S"], ["adRevenue", "N"]]                                        |
| inputColumnsDynamoDB           | DynamoDB specific - required only in local testing mode   | [["sourceIP", "S"], ["destURL", "S"],  ["visitDate", "S"], ["adRevenue", "N"]] |
| outputSourceType               | Required                                                  | "s3"                                                                           |
| outputSource                   | Required                                                  | "serverless-mapreduce-storage-output"                                          |
| outputPrefix                   | S3 specific                                               | "output"                                                                       |
| outputPartitionKeyDynamoDB     | DynamoDB specific                                         | ["ip", "S"]                                                                    |
| outputColumnDynamoDB           | DynamoDB specific                                         | ["revenue", "S"]                                                               |
| useCombine                     | Required                                                  | true                                                                           |
| numReducers     | Required                                         | 4                                               |
| localTesting     | Required                                        | true                                            |
| localTestingInputPath | Required only used in local testing mode     | "../../input_data/testing_partitioned/s3/"    |
| serverlessDriver | Required                                          | false                                         |
| optimisation | Optional (default to false)                                          | false                                         |

## Map function's input pair types
In the map function, the type of input pair is different depending on the input storage medium. 

For S3, the input key is always a S3 object path and the input value is the contents of that object. The data is assumed
to be partitioned across different S3 objects on the input bucket. One mapper will work across several S3 objects.

For DynamoDB, the input key is the input table's primary key (either just the partition key or composite key which
consists of partition and sort keys) and the input value is a map that contains all the fields specified in the 
configuration field: `inputProcessingColumnsDynamoDB`. The data processing is performed only on the specified input 
table as it is assumed that the table is not partitioned. 

These design choices were made based on the conventions of using these different data storage, which have 
different properties. Hence bear in mind these different input pair types that you should expect in your map function. 

As you will see in the example map functions of this project, the map function for S3 input type is different to the map 
function used for DynamoDB input type. 
