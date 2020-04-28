# Serverless-MR-Test

This project is a data processing example job that uses the Serverless-MR library and it aims to show how one could use 
this library to quickly set up any data processing job.
[Serverless-MR](https://github.com/hanglili/Serverless-MapReduce) is a MapReduce framework that is deployed 
and run on a serverless platform. 


## Quickstart::Step by Step
### Executing a job
1. Create a python project and then create a directory with the name ```src``` at the root-level directory of the project. 
Inside ```src```, create a python module with any name. Then inside this module, create two modules called 
```configuration``` and ```user_job``` (for this module, any name works, but using ```user_job``` for easier referencing). 
Remember that a module in python is a directory that contains ```__init__.py```.
2. Run the command: ```pip install -i https://test.pypi.org/simple/ serverless-mr``` to install the `serverless_mr` library.
3. Inside the module ```configuration```, specify two configuration files: `driver.json` and `static-job-info.json`:
    - `driver.json`: records properties of provisioned AWS Lambda and information on where the provided map and reduce functions 
    are located. Currently, for any job, use the `driver.json` configuration file of this project. 
    - `static-job-info.json`: records information of a job. You can tailor the `static-job-info.json` configuration file of
    this project, to your own job.
   
   For more information on the fields of these configuration files, check out: 
   https://github.com/hanglili/Serverless-MapReduce/blob/master/src/python/notes
4. Inside the module ```user_job```, you can specify the map function, reduce function and partition function of 
shuffling for your job:
    - Map function: create a python script with the name `map.py`. Inside this script, write the map function 
    with any name that follows the function signature defined in the example map function in this project. 
    - Reduce function: create a python script with the name `reduce.py`. Inside this script, write the reduce function 
    with any name that follows the function signature defined in the example reduce function in this project. 
    - Partition function for the shuffling stage: create a python script with the name `partition.py`. Inside this script, write the partition function 
    with any name that follows the function signature defined in the example partition function in this project.  
5. Set your working directory to be `src/#python/` where `#python` is replaced by the name of the python module you 
created in step 1. Then, create a main python script under `src/#python/`, that declares a `ServerlessMR` instance and
set the map, reduce and partition functions and then calls `run()` to start executing your job.
6. (Optional) If you want to test your job locally before deploying and executing it on AWS, you can do so by following
this series of steps:
    1. Setting `true` to the field `localTesting` in `static-job-info.json`.
    2. Install the library `localstack` by running the command `pip install localstack`.
    3. Run docker and pull the docker container for `localstack` by running the command `docker pull localstack/localstack`.
    4. To run localstack (which simulates different AWS service behaviours with docker containers), run the command: 
    ```TMPDIR=/private$TMPDIR SERVICES=serverless LAMBDA_EXECUTOR=docker LAMBDA_REMOVE_CONTAINERS=false DOCKER_HOST=unix:///var/run/docker.sock  DEBUG=1 localstack start --docker```
    5. Apart from that, in order to run AWS Lambda, pull the lambci docker image by running the command `docker pull lambci/lambda`.
    6. Set any value (for example, `dummy-role`) to environmental variable `serverless_mapreduce_role`.
    7. Run the main function that you have created in step 5.
7. To deploy and run this job on AWS, download the following scripts: `create-biglambda-role.py`, `delete-biglambda-role.py`, 
`setup.sh`, `policy.json` on the root-level directory of the project.
8. Set your AWS credentials by storing your credentials under the file `credentials ` in `~/.aws/` directory.
9. Run the command: ```./setup.sh <S3 shuffling bucket name> <your AWS Account ID>```. Note that there is no need to 
create this shuffling bucket before running this bash script. In fact, this is one of steps in the script. Make sure to 
tailor `policy.json` to your own AWS Account Id and shuffling bucket name. 
10. Run the main function that you have created in step 5, setting the working directory to `src/python` and the 
environmental variable `serverless-mapreduce-role` to the output of executing `setup.sh`.

### Clean up
1. On the root-level directory of the project, run: `python3 delete-biglambda-role.py` 

### Writing tests
Apart from manually testing your code locally using localstack as described in the previous section, you can also write tests.
These include unit tests and end-to-end tests. Unit tests can be used to test whether your map, reduce and partition 
functions behave as expected. End-to-end tests automate the manual process of testing your code locally in an end-to-end manner
using localstack. 

The tests folder which contains all the test files should be inside the module `src/#python` and remember to set your working 
directory to be `src/#python` when running these test scripts. Also when running end-to-end tests, remember to start 
docker and localstack.

To understand how these unit tests and end-to-end tests are written, look at the directory `src/python/tests` in this project.

The location of the input data path provided in the field `localTestingInputPath` of `static-job-info.json` file needs
to be relative to `src/python/`.

## Example job:
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
input pair is of form (S3 file key, S3 file contents). This map function splits the input document into lines which are further 
split using `,`. Afterwards, it generates the intermediate data from each of these lines. The intermediate data is a list of shape 
(src_ip, ad_revenue). The code is shown below:
```
def map_function(outputs, input_pair):
    """
    :param outputs: [(k2, v2)] where k2 and v2 are intermediate data
    which can be of any types
    :param input_pair: (k1, v1) where k1 and v1 are assumed to be of type string
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

The partition function hashes a key using sha256 and then changes this hashed key to the a value between 0 and 
(num_bins - 1) by performing modulus operation on the hashed key with the number of bins. The code is shown below:
```
def partition(key, num_bins):
    """
    :param key: key of intermediate data which can be of any type
    :param num_bins: number of bins that a key could be partitioned to (this is equal to number of reducers)
    :returns an integer that denotes the bin assigned to this key
    """
    key_hashed = int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16) % 10**8
    return key_hashed % num_bins
```

The reduce function receives a intermediate pair of (src_ip, [ad_revenues]) and aggregates the ad_revenues for 
this source ip by summing them up. The code is shown below:
```
def reduce_function(outputs, intermediate_data):
    """
    :param outputs: (k2, [v2]) where k2 and v2 are output data
    which can be of any types
    :param intermediate_data: (k2, [v2]) where k2 and v2 are of type string.
    Users need to convert them to their respective types explicitly.
    NOTE: intermediate data type is the same as the output data type
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

## Job information
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

## Map function's input pair types
In the map function, the type of input pair is different depending on the input storage medium. 

For S3, the input key is always a S3 object path and the input value is the contents of that object. The data is assummed
to be partitioned across different S3 objects on the input bucket. One mapper will work across several S3 objects.

For DynamoDB, the input key is the input table's primary key (either just the partition key or composite key which
consists of partition and sort keys) and the input value is a map that contains all the fields specified in the 
configuration field: `inputProcessingColumnsDynamoDB`. The data processing is performed only on the specified input 
table as it is assumed that the table is not partitioned. 

These design choices were made based on the conventions of using these different data storage mediums, which have 
different properties. Hence bear in mind these different input pair types that you should expect in your map function. 

As you will see in the example map functions of this project, the map function for S3 input type is different to the map 
function used for DynamoDB input type. 
