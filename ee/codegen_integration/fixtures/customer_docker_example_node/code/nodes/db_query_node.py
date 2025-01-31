from typing import Any, Dict, List

from vellum.workflows.nodes import BaseNode

# from utils.demo_postgres import execute_query


class DBQueryNode(BaseNode):
    # TODO needs merging
    # query = "SELECT * FROM users"

    class Outputs(BaseNode.Outputs):
        rows: List[Dict[str, Any]]

    def run(self) -> Outputs:
        return self.Outputs(rows=[])
