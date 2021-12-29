import datetime
import jmespath
import prefect
from typing import Dict, List, Union
from tabulate import tabulate

class GQLBase():
    DATE_TIME_FIELDS = ["created", "updated", "last_queried", "deleted_at", "start_time", "end_time", "scheduled_start_time"]
    def __init__(self, gql_string:str, object:str, fields:List, cols:List=None):
        self.gql_string = gql_string
        self.object = object
        self.fields = fields
        self.cols = None
        if cols is None or len(cols) == 0 :
            if self.fields is not None:
                self.cols = [c.upper() for c in fields]
        else:
            self.cols = cols
        self.variables = {}
        self.client = prefect.client.Client()
        self.values = {}

    def format_date(self,d:str):
        return datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone().strftime('%Y-%m-%d_%H:%M:%S')

    def build_table(self):
        table = []
        for v in self.values:
            value = []
            for r in self.fields:
                elem = jmespath.search(r, v)
                if isinstance(elem, dict):
                    v_ = ",".join(elem) if isinstance(elem, list) else elem
                else:
                    v_ = elem
                if r in GQLBase.DATE_TIME_FIELDS and v_ is not None:
                    value.append(self.format_date(v_))
                else:
                    value.append(v_)
            table.append(value)
        return table

    def execute(self, variables:Union[dict,str]={}):
        self.variables = variables
        self.values = self.client.graphql(self.gql_string, variables=self.variables).data.to_dict().get(self.object)
        return self

    def print_table(self, data):
        print(tabulate(data, headers=self.cols, showindex=True))

    def print(self, out='text'):
        if out == "json":
            print(self.values)
        else:
            data = self.build_table()
            self.print_table(data)
