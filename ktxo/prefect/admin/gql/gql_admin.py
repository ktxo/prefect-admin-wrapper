
from ktxo.prefect.admin.gql.base import GQLBase
class GQLAgentList(GQLBase):
    def __init__(self):
        super().__init__(
            gql_string="query {agents {id, core_version, name, type, created, updated, last_queried, labels }}",
            object="agents",
            fields=["id", "core_version", "name", "type", "created", "updated", "last_queried", "labels"],
            cols=["ID", "CORE_VER", "NAME", "TYPE", "CREATED", "UPDATED", "LAST_QUERIED", "LABELS"])

class GQLProjectList(GQLBase):
    def __init__(self):
        super().__init__(
            gql_string="""query{
  project {
  id,name, description,flows_aggregate(distinct_on:flow_group_id){aggregate{count}}
}}""",
            object="project",
            fields=["id","name","description","flows_aggregate.aggregate.count"],
            cols=["ID","NAME","DESCRIPTION","NUM_FLOWS"])


class GQLFlowRunList(GQLBase):
    def __init__(self):
        super().__init__(
            gql_string="""query F($flow_name:String){
  flow_run(where:{flow:{name:{_eq:$flow_name}}}){
  id,version,name, state,state_message,agent {id,name,},start_time,end_time,labels,run_config,scheduled_start_time
}}""",
            object="flow_run",
            fields=["id", "version", "name", "agent.id", "agent.name", "state", "state_message", "scheduled_start_time", "start_time", "end_time", "labels", "run_config.labels"],
            cols=["ID", "VER", "NAME", "AGENT_ID", "AGENT", "STATE", "STATE_MESSAGE", "SCHEDULED_AT","START", "END", "LABEL", "RUN_CONFG_LABELS"])


class GQLFlowScheduleEnable(GQLBase):
    def __init__(self):
        super().__init__(
            gql_string="""mutation F($flow_id:UUID){
    set_schedule_active(input:{
    flow_id: $flow_id
    }){success
}}""",
            object="set_schedule_active",
            fields=None,
            cols=None)

class GQLFlowScheduleDisable(GQLBase):
    def __init__(self):
        super().__init__(
            gql_string="""mutation F($flow_id:UUID){
    set_schedule_inactive(input:{
    flow_id: $flow_id
    }){success
}}""",
            object="set_schedule_inactive",
            fields=None,
            cols=None)


class GQLFlowList(GQLBase):
    def __init__(self):
        super().__init__(
            gql_string="""query F($archived:Boolean){ 
    flow (where:{archived:{_eq:$archived}},limit:100, order_by:{version:desc,created:asc,updated:desc}){
    id,version,name,archived,created,updated,is_schedule_active,flow_group_id, run_config
}}""",
            object="flow",
            fields=["version","archived","id","name","created","updated","is_schedule_active","flow_group_id", "run_config.labels"],
            cols=["VER","ARCHIVED","ID","NAME","CREATED","UPDATED","SCHEDULED","GROUP_ID","LABELS"])


class GQLSecretList(GQLBase):
    def __init__(self):
        super().__init__(
            gql_string="query {secret_names}",
            object="secret_names",
            fields=["secret_name"],
            cols=["SECRET"])

    def execute(self, variables="all"):
        super().execute()
        return self

    def print(self,out="text"):
        if out == "json":
            print(self.values)
        else:
            data = [[d] for d in self.values]
            self.print_table(data)

class GQLSecretQuery(GQLBase):
    def __init__(self):
        super().__init__(
            gql_string="query F($secret_name:String) {secret_value(name: $secret_name )}",
            object="secret_value",
            fields=["secret_name", "secret_value"],
            cols=["SECRET", "VALUE"])

    def execute(self, variables="all"):
        values = []
        if variables == "all":
            #secrets = do_graphql(GQL_SECRET_LIST, "secret_names")
            secrets = GQLSecretList().execute().values
            for s in secrets:
                super().execute({"secret_name": s})
                values.append([s,self.values])
        else:
            super().execute({"secret_name": variables})
            values = [[variables, self.values]]
        self.values = values
        return self

    def print(self,out="text"):
        if out == "json":
            print(self.values)
        else:
            #data = self.build_table()
            self.print_table(self.values)


class GQLFlowQuery(GQLBase):
    def __init__(self):
        super().__init__(
            gql_string="""query F($flow_name:String,$archived:Boolean){
    flow (where: {name: {_eq: $flow_name},_and: {archived:{_eq:$archived}}},limit:100, order_by:{version:desc,created:asc,updated:desc}){
    id,version,name,archived,,created,updated,is_schedule_active, flow_group_id, run_config,parameters,flow_group {default_parameters}
}}""",
            object="flow",
            fields=["version","archived","id","name","created","updated","is_schedule_active","flow_group_id", "run_config.labels", "parameters[*][name,default,required]", "flow_group.default_parameters"],
            cols=["VER","ARCHIVED","ID","NAME","CREATED","UPDATED","SCHEDULED","GROUP_ID","LABELS", "PARAMETERS(NAME,DFLT,REQ)","DEFAULT_PARAMETERS"])

class GQLSetParameter(GQLBase):
    def __init__(self):
        super().__init__(
            gql_string="""mutation F($flow_group_id:UUID!, $parameters:JSON!){
    set_flow_group_default_parameters(input:{
    flow_group_id: $flow_group_id,
    parameters: $parameters
    }){success
}}""",
            object="set_flow_group_default_parameters",
            fields=None,
            cols=None)
