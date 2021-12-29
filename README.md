## Wrapper script for Prefect administration 

This script is a wrapper for some Prefect operations

All operations are implemented either with [Prefect cli](https://docs.prefect.io/orchestration/concepts/cli.html) or [Prefect Interactive API](https://docs.prefect.io/orchestration/ui/interactive-api.html)

The motivations for this script were: to explore Prefect API, learn about Prefect and GraphQL, and to have a [command line program to execute operations](#executing-api) available in Prefect API


I included some operations while preparing a [POC](https://github.com/ktxo/prefect-poc.git) with Prefect 

Script usage:
```
$ prefect_wrapper --help

usage: prefect_wrapper [-h] [-f FORMAT] [-l LOG] [-L {I,D,W,E}] [-v] {secret,flow,flow_run,agent,api,project} ...

Wrapper for Prefect (agent, admin)

optional arguments:
  -h, --help            show this help message and exit
  -f FORMAT, --format FORMAT
                        Output format
  -l LOG, --log LOG     Logging configuration file
  -L {I,D,W,E}, --log_level {I,D,W,E}
                        Log level. Valid options: I(info), D(debug), W(warning), E(error)
  -v, --version         Show script version

Commands:
  {secret,flow,flow_run,agent,api,project}
                        Valid commands

Examples:
- List flows 
prefect_wrapper flow -l

- Set parameter 'A=1' to flow_group_id=a4846d5b-5371-4cf8-8251-a33d30497300, log level DEBUG
prefect_wrapper -LD flow -p A=1 -g a4846d5b-5371-4cf8-8251-a33d30497300

- Get details from flow DUMMY_FLOW
prefect_wrapper flow -q DUMMY_FLOW 

- List Agents 
prefect_wrapper agent -l

- Execute GraphQL from class 'GQLLog' include in 'dummy.gql_example.py' with args from json file '/tmp/gql_log.json'
prefect_wrapper  api --execute dummy.gql_example.GQLLog -p /tmp/gql_log.json

- Get flow runs for flow 'DUMMY_FLOW'
prefect_wrapper  flow_run -l DUMMY_FLOW
```
```
$ prefect_wrapper secret -h
usage: prefect_wrapper secret [-h] [-s SECRET_NAME] [-q SECRET_NAME] [-l]

optional arguments:
  -h, --help            show this help message and exit
  -s SECRET_NAME, --set SECRET_NAME
                        Create a secret on Prefect Cloud
  -q SECRET_NAME, --query SECRET_NAME
                        Query secret value. Use 'all' to get all
  -l, --list            List secrets
```

```
$ prefect_wrapper flow -h
usage: prefect_wrapper flow [-h] [-q FLOW_NAME] [-l] [-se FLOW_ID] [-sd FLOW_ID] [-p PARAMETER [PARAMETER ...]] [-g FLOW_GROUP_ID] [-a]

optional arguments:
  -h, --help            show this help message and exit
  -q FLOW_NAME, --query FLOW_NAME
                        Get flow details
  -l, --list            List flows
  -se FLOW_ID, --schedule_enable FLOW_ID
                        Enable schedule flows
  -sd FLOW_ID, --schedule_disable FLOW_ID
                        Disable schedule flows
  -p PARAMETER [PARAMETER ...], --parameter PARAMETER [PARAMETER ...]
                        Set parameters flow
  -g FLOW_GROUP_ID, --group FLOW_GROUP_ID
                        Flow group id
  -a, --archived        Include archived flows
```

```
prefect_wrapper flow_run -h
usage: prefect_wrapper flow_run [-h] [-l FLOW_NAME]

optional arguments:
  -h, --help            show this help message and exit
  -l FLOW_NAME, --list FLOW_NAME
                        List flow runs
```

```
$ prefect_wrapper agent -h
usage: prefect_wrapper agent [-h] [-l]

optional arguments:
  -h, --help  show this help message and exit
  -l, --list  List agents
```

```
$ prefect_wrapper api -h
usage: prefect_wrapper api [-h] [-e PACKAGE.CLASS] [-p [VARIABLES [VARIABLES ...]]]

optional arguments:
  -h, --help            show this help message and exit
  -e PACKAGE.CLASS, --execute PACKAGE.CLASS
                        Allow to execute GraphQL against Prefect API
  -p [VARIABLES [VARIABLES ...]], --variables [VARIABLES [VARIABLES ...]]
                        Set variables for class that implement GraphQL
```

```
prefect_wrapper project -h
usage: prefect_wrapper project [-h] [-l]

optional arguments:
  -h, --help  show this help message and exit
  -l, --list  Query projects
```

## Links y references:
- [Prefect - Arquitecture](https://docs.prefect.io/orchestration/#architecture-overview)
- [Prefect cli](https://docs.prefect.io/orchestration/concepts/cli.html)
- [Prefect Interactive API](https://docs.prefect.io/orchestration/ui/interactive-api.html)
- [GraphQL](https://graphql.org/)

# Requirements and installation

   
- [Prefect](https://docs.prefect.io/core/getting_started/install.html)
  ```
  pip install prefect
  
  # To check
  pip list | grep prefect
  prefect                 0.15.5  
  
  # or run 
  prefect version
  0.15.5
  ```

- Clone repo from https://github.com/ktxo/prefect-poc.git
## Executing API
```
git clone https://github.com/ktxo/prefect-admin-wrapper.git
cd prefect-admin-wrapper
python setup.py bdist_wheel 
pip install dist/prefect_wrapper-*.whl

prefect_wrapper -v
```

# Executing API
The script allows to execute others GraphQL's using a class inherited from [GQLBase](ktxo/prefect/admin/gql/base.py), there is an example in [GQLLog](GQLs/dummy/gql_example.py)

To execute :
- Add class to PYTHONPATH
- Create a JSON file with GraphQL params (if apply) or using command line. Command line accept only the following:

  **"PARAM1=VALUE1 PARAM2=VALUE2 path_json_params"**
- Use command/option **api --execute package_file.class" --variables "PARAM1=VALUE1 PARAM2=VALUE2 path_json_params"**
- Refer to [GQL classes](ktxo/prefect/admin/gql) for more examples
- 
Example:
```
# Assuming that custom class was copied to "/tmp/GQLs"
mkdir /tmp/GQLs 2>/dev/null
cp -rp GQLs/dummy  /tmp/GQLs
export PYTHONPATH=/tmp/GQLs

prefect_wrapper api --execute dummy.gql_example.GQLLog -p /tmp/GQLs/dummy/gql_log.json
    ID                                    FLOW_RUN_ID                           NAME                     MESSAGE
--  ------------------------------------  ------------------------------------  -----------------------  ----------------------------------------------------------------------------
 0  b636753b-8ece-4946-a39a-efd800013e95  b5705f6d-262e-44f8-95a4-31a701eb1d6c  AGENT1                   Submitted for execution: PID: 114094
 1  7bffe05a-1a01-4b64-9438-776958be1fe1  b5705f6d-262e-44f8-95a4-31a701eb1d6c  prefect.CloudFlowRunner  Beginning Flow run for 'DUMMY_FLOW'
 2  306f94b6-5e26-4f9c-9467-57c4fa56dfba  b5705f6d-262e-44f8-95a4-31a701eb1d6c  prefect.CloudTaskRunner  Task 'random_number': Starting task run...
 3  ea0e9a54-d37a-4298-92ee-372e739a0a0d  b5705f6d-262e-44f8-95a4-31a701eb1d6c  prefect.CloudTaskRunner  Task 'random_number': Finished task run for task with final state: 'Success'
 4  6ca086b7-6f07-44c1-ad7a-afad5a861517  b5705f6d-262e-44f8-95a4-31a701eb1d6c  prefect.CloudTaskRunner  Task 'param1': Starting task run...
 5  69ff4abc-ad7c-41e0-937b-0d1e282c98d9  b5705f6d-262e-44f8-95a4-31a701eb1d6c  prefect.CloudTaskRunner  Task 'param1': Finished task run for task with final state: 'Success'
 6  69e81152-9dec-4996-872c-e5092c819196  b5705f6d-262e-44f8-95a4-31a701eb1d6c  prefect.CloudTaskRunner  Task 'plus_one': Starting task run...
 7  fd7ebad8-4e50-4386-b8d7-5b3aea23d35c  b5705f6d-262e-44f8-95a4-31a701eb1d6c  prefect.CloudTaskRunner  Task 'plus_one': Finished task run for task with final state: 'Success'
 8  06329b4b-926e-4005-98df-0d2d02f56e8d  b5705f6d-262e-44f8-95a4-31a701eb1d6c  prefect.CloudFlowRunner  Flow run SUCCESS: all reference tasks succeeded

```