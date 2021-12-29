from ktxo.prefect.admin.gql.base import GQLBase

class GQLLog(GQLBase):
    def __init__(self):
        super().__init__(
            gql_string="""query F($where_:log_bool_exp){
  log (where: $where_){
    id,flow_run_id,name,message
  }
}""",
            object="log",
            fields=["id","flow_run_id","name", "message"],
            cols=None)
