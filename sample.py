from agents import Agent, ModelSettings, TResponseInputItem, Runner, RunConfig, trace
from pydantic import BaseModel

r_mobile_agent = Agent(
  name="R-Mobile Agent",
  instructions="You are a call center agent for a telephone company use your fine tuning as a priority in answering customer questions. ",
  model="ft:gpt-4.1-2025-04-14:riis-llc::CellOhfT",
  model_settings=ModelSettings(
    temperature=1,
    top_p=1,
    max_tokens=2048,
    store=True
  )
)


class WorkflowInput(BaseModel):
  input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
  with trace("New workflow"):
    workflow = workflow_input.model_dump()
    conversation_history: list[TResponseInputItem] = [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": workflow["input_as_text"]
          }
        ]
      }
    ]
    r_mobile_agent_result_temp = await Runner.run(
      r_mobile_agent,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_692219781f148190acae41fee68e4a3606006eb1de08b775"
      })
    )

    conversation_history.extend([item.to_input_item() for item in r_mobile_agent_result_temp.new_items])

    r_mobile_agent_result = {
      "output_text": r_mobile_agent_result_temp.final_output_as(str)
    }
    return r_mobile_agent_result
