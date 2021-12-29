"""
Prefect Admin wrapper
"""

import argparse
import getpass
import json
import logging
import logging.config
import os
import re
import sys
import prefect
from ktxo.prefect.admin import _about as about
from ktxo.prefect.admin.gql.gql_admin import (GQLSecretQuery, GQLSecretList,
                                              GQLFlowList, GQLFlowQuery,
                                              GQLFlowScheduleEnable,GQLFlowScheduleDisable,
                                              GQLFlowRunList,
                                              GQLProjectList,
                                              GQLAgentList,
                                              GQLSetParameter)

#---------------------------------------------------------------------------
# Global vars
#---------------------------------------------------------------------------
_log = logging.getLogger("ktxo.prefect.admin")
client:prefect.Client = None

#---------------------------------------------------------------------------
#   Versions helper
#---------------------------------------------------------------------------
def get_version():
    """Get version: python, current script and other needed"""
    python_version=sys.version.replace('\n','')
    prefect_version=prefect.__version__
    return [f'{about.__name__} v{about.__version__} ({about.__date__}) by {about.__author__}',
            about.__version__,
            f"Python version {python_version}",
            f"Prefect version {prefect_version}"
            ]

def show_version():
    """Print version"""
    print(get_version()[0])
    print(get_version()[2])
    print(get_version()[3])


#---------------------------------------------------------------------------
#   Command args
#---------------------------------------------------------------------------
description_message = about.__description_message__
example_usage = f'''
Examples:
- List flows 
{about.__name__} flow -l

- Set parameter 'A=1' to flow_group_id=a4846d5b-5371-4cf8-8251-a33d30497300, log level DEBUG
{about.__name__} -LD flow -p A=1 -g a4846d5b-5371-4cf8-8251-a33d30497300

- Get details from flow DUMMY_FLOW
{about.__name__} flow -q DUMMY_FLOW 

- List Agents 
{about.__name__} agent -l

- Execute GraphQL from class 'GQLLog' include in 'dummy.gql_example.py' with args from json file '/tmp/gql_log.json'
{about.__name__}  api --execute dummy.gql_example.GQLLog -p /tmp/gql_log.json

- Get flow runs for flow 'DUMMY_FLOW'
{about.__name__}  flow_run -l DUMMY_FLOW

'''
#---------------------------------------------------------------------------
def parse_args():
    """Command arg parse"""
    parser = argparse.ArgumentParser(prog=about.__name__,
                                     description=about.__description_message__,
                                     epilog=example_usage,
                                     formatter_class=argparse.RawTextHelpFormatter)
    subparser = parser.add_subparsers(title="Commands",dest='command', help="Valid commands")

    secret_parser = subparser.add_parser("secret")
    secret_parser.add_argument("-s","--set", metavar="SECRET_NAME", help="Create a secret on Prefect Cloud", type=str)
    secret_parser.add_argument("-q", "--query", metavar="SECRET_NAME", help="Query secret value. Use 'all' to get all", type=str)
    secret_parser.add_argument("-l", "--list", help="List secrets", action='store_true')

    flow_parser = subparser.add_parser("flow")
    flow_parser.add_argument("-q", "--query", metavar="FLOW_NAME", help="Get flow details", type=str)
    flow_parser.add_argument("-l", "--list", help="List flows", action='store_true')
    flow_parser.add_argument("-se", "--schedule_enable", metavar="FLOW_ID", help="Enable schedule flows")
    flow_parser.add_argument("-sd", "--schedule_disable",metavar="FLOW_ID", help="Disable schedule flows")
    flow_parser.add_argument("-p", "--parameter", help="Set parameters flow", nargs='+')
    flow_parser.add_argument("-g", "--group", metavar="FLOW_GROUP_ID", help="Flow group id")
    flow_parser.add_argument("-a", "--archived", help="Include archived flows", action='store_false',default=True)

    flow_run_parser = subparser.add_parser("flow_run")
    flow_run_parser.add_argument("-l", "--list", metavar="FLOW_NAME", help="List flow runs")

    agent_parser = subparser.add_parser("agent")
    agent_parser.add_argument("-l", "--list", help="List agents", action='store_true')

    api_parser = subparser.add_parser("api")
    api_parser.add_argument("-e", "--execute", metavar="PACKAGE.CLASS", help="Allow to execute GraphQL against Prefect API")
    api_parser.add_argument("-p", "--variables", help="Set variables for class that implement GraphQL", nargs='*')

    # register_parser = subparser.add_parser("register")
    # register_parser.add_argument("-r", "--register", metavar="PROJECT_ID", help="Register a flow")
    # register_parser.add_argument("-m", "--module", metavar="PATH_MODULE", help="Module containing the flow", type=str)
    # register_parser.add_argument("-l", "--labels", metavar="LABELS", help="Labels", type=str,nargs='+', default=["DFLT"])

    project_parser = subparser.add_parser("project")
    project_parser.add_argument("-l", "--list", help="Query projects", action='store_true', default=True)

    parser.add_argument("-f", "--format", help="Output format", default="text")

    parser.add_argument("-l", "--log", help="Logging configuration file")

    parser.add_argument("-L", "--log_level",
                        help="Log level. Valid options: I(info), D(debug), W(warning), E(error)",
                        choices=['I','D','W','E'],
                        default='W')

    parser.add_argument("-v", "--version",
                        help="Show script version",
                        action='store_true')

    args = parser.parse_args()
    if args.version:
        show_version()
        sys.exit(0)

    if args.command == "flow" and args.parameter and not args.group:
        parser.error(f"Option 'parameter' requires option 'group', use command 'flow' + 'list' to query this value")

    # No arguments received or missing
    if len(sys.argv) == 1 or args.command is None or \
            args.command in ["secret"] and (any([args.list, args.query, args.set]) == False) or \
            args.command in ["flow"] and (any([args.list, args.query,args.parameter,args.schedule_enable,args.schedule_disable]) == False) or \
            args.command in ["flow_run"] and (any([args.list]) == False) or \
            (args.command in ["agent"] and any([args.list]) == False):
        #parser.print_usage()
        parser.error("Ops, missing arguments")
        #parser.print_help()
    return args


LOG_LEVELS={'I':logging.INFO,'D':logging.DEBUG,'W':logging.WARNING,'E':logging.ERROR}
def init_log(args):
    if args.log:
        with open(args.log, 'r', encoding="utf-8") as fd:
            logging.config.dictConfig(json.load(fd))
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    # Set root level
    # For specific logger: _log.setLevel(LOG_LEVELS.get(args.log_level,logging.INFO))
    logging.getLogger().setLevel(LOG_LEVELS.get(args.log_level,logging.INFO))

#---------------------------------------------------------------------------
def build_variables(params:list):
    variables={}
    if params is None: return variables
    for p in params:
        if re.match(r'[a-zA-Z0-9]+=[a-zA-Z0-9]+', p.strip()):
            variables[p.split("=")[0]] = p.split("=")[1]
        else:
            try:
                with open(p, "r") as fd:
                    variables.update(json.load(fd))
            except Exception as e:
                _log.error(f"Invalid parameter '{p}', cannot read/open json file. {str(e)}")
                _log.info(f"Aplication end, pid={os.getpid()}")
                sys.exit(1)

    return variables
#---------------------------------------------------------------------------
def load_class(package_class):
    import importlib
    module_file=".".join(package_class.split(".")[:-1])
    class_name = package_class.split(".")[-1]

    module = importlib.import_module(module_file)
    class_ = getattr(module, class_name)
    return class_
#---------------------------------------------------------------------------
#   Main
#---------------------------------------------------------------------------
def main():
    global client
    args = parse_args()
    init_log(args)

    _log.info(get_version()[0])
    _log.info(get_version()[2])
    _log.info(get_version()[3])

    _log.info(f"Starting pid={os.getpid()}")
    _log.info(f"Using args {args}")
    client = prefect.Client()

    # ---------------------------------------------------------------------------
    #   Application code
    # ---------------------------------------------------------------------------
    if args.command == "secret" and args.set:
        secret_value = getpass.getpass(f"Enter value for secret '{args.set}':")
        client.set_secret(name=args.set, value=secret_value)
    elif args.command == "secret" and args.query:
        gql = GQLSecretQuery()
        gql.execute(args.query).print(args.format)
    elif args.command == "secret" and args.list:
        gql = GQLSecretList()
        gql.execute().print(args.format)

    elif args.command == "flow" and args.list:
        variables ={}
        if args.archived:
            variables = {"flow_name": args.query, "archived": False}
        gql = GQLFlowList()
        gql.execute(variables).print(args.format)

    elif args.command == "flow" and args.query:
        if args.archived:
            variables = {"flow_name": args.query, "archived": False}
        else:
            variables = {"flow_name": args.query}
        gql = GQLFlowQuery()
        gql.execute(variables).print(args.format)

    elif args.command == "flow" and args.parameter:
        parameters = build_variables(args.parameter)
        gql = GQLSetParameter()
        gql.execute({"flow_group_id": args.group,"parameters": parameters})

    elif args.command == "flow" and args.schedule_enable:
        gql = GQLFlowScheduleEnable()
        gql.execute({"flow_id": args.schedule_enable})

    elif args.command == "flow" and args.schedule_disable:
        gql = GQLFlowScheduleDisable()
        gql.execute({"flow_id": args.schedule_disable})

    elif args.command == "flow_run" and args.list:
        gql = GQLFlowRunList()
        gql.execute({"flow_name": args.list}).print(args.format)

    elif args.command == "project" and args.list:
        gql = GQLProjectList()
        gql.execute().print(args.format)

    elif args.command == "agent" and args.list:
        gql = GQLAgentList()
        gql.execute().print(args.format)

    elif args.command == "api" and args.execute:
        variables = build_variables(args.variables)
        class_instance = load_class(args.execute)()
        class_instance.execute(variables).print(args.format)



    _log.info(f"Aplication end, pid={os.getpid()}")

if __name__ == '__main__':
    main()
    sys.exit(0)