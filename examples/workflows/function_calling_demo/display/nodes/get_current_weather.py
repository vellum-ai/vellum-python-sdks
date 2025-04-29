from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseCodeExecutionNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.get_current_weather import GetCurrentWeather


class GetCurrentWeatherDisplay(BaseCodeExecutionNodeDisplay[GetCurrentWeather]):
    label = "Get Current Weather"
    node_id = UUID("d3734d8b-c3c8-44db-abf8-cbc6c07e20dc")
    target_handle_id = UUID("4d7e27dc-608a-4486-ab45-fe7a476ee3c0")
    output_id = UUID("312cdcea-bef2-498e-80d0-32391857ffcc")
    log_output_id = UUID("fbea8140-56b3-4e34-8550-63c62887c2d5")
    node_input_ids_by_name = {
        "code_inputs.kwargs": UUID("5f08cdf0-e683-44a3-96e6-1d42d4d57f28"),
        "code": UUID("a069f01e-fa1d-48b4-854f-4de6baa0761e"),
        "runtime": UUID("19da0c1a-1c88-40be-8286-134c551dcb32"),
        "code_inputs.gmaps_api_key": UUID("2b5a6327-d026-4b54-997b-00e97125f85e"),
        "code_inputs.openweather_api_key": UUID("32e37882-aee4-47a1-b286-a533b9bf350a"),
    }
    output_display = {
        GetCurrentWeather.Outputs.result: NodeOutputDisplay(
            id=UUID("312cdcea-bef2-498e-80d0-32391857ffcc"), name="result"
        ),
        GetCurrentWeather.Outputs.log: NodeOutputDisplay(id=UUID("fbea8140-56b3-4e34-8550-63c62887c2d5"), name="log"),
    }
    port_displays = {
        GetCurrentWeather.Ports.default: PortDisplayOverrides(id=UUID("f7c33ad9-2414-4c5e-89cb-4cc372ee2adf"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=4740, y=-105), width=460, height=327)
