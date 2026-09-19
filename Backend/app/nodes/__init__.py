from Backend.app.nodes.triggers.manual import ManualTriggerNode
from Backend.app.nodes.transform.set_node import SetNode
from Backend.app.nodes.utility.log import LogNode
from Backend.app.nodes.logic.if_node import IfNode
from Backend.app.nodes.utility.http_request import HttpRequestNode


def register_nodes(registry):
    registry.register(ManualTriggerNode)
    registry.register(SetNode)
    registry.register(LogNode)
    registry.register(IfNode)
    registry.register(HttpRequestNode)