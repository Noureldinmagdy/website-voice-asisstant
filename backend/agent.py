from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import (
    openai,
    noise_cancellation,
)
from livekit.plugins import google
import numpy as np
from livekit.agents import ModelSettings, Agent
from typing import AsyncIterable
import json 

from map.engine import Engine
from livekit.agents import function_tool, Agent, RunContext
from typing import Any

load_dotenv(".env.local")

class Assistant(Agent):
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        super().__init__(instructions=f"""
                         

You are an AI agent that guides users through a website using predefined Flows.
Each Flow consists of ordered Steps that must be followed strictly.

Strict Execution Rules

    1- Handle one Step at a time only.

    2- Never collect inputs for multiple Steps together.

    3- Always state the current Flow and current Step.

    4- Ask for one input only if the Step requires it.

    5- Do not proceed to the next Step until:

        5.1- The input is received

        5.2- The input is logically validated

        5.3- It is sent using send_params_for_current_flow

        5.4- The result is confirmed as OK


Flow Control

    - If the user wants to change the Flow:

        - Confirm intent

        - Call select_flow

    Allow:

        - Going back to the previous Step

        - Canceling or exiting the current Flow safely
                         
Forbidden

    - Skipping Steps

    - Assuming missing data

    - Inventing Steps or inputs

    - Asking multiple questions in one message

⚠️ Operate only within the provided Flow definitions.

                         
here is the flows desciption so user can choose what he wants to do :

{self.engine.flows_desciption}
""")
        
    @function_tool()
    async def select_flow(
        self,
        context: RunContext,
        index_of_flow: int,
    ) -> dict[str, Any]:
        """
        Change or select a flow by it is index
        
        Args:
            index_of_flow: the index of the flow.

        Returns:
            the current state and logs of the flow 
        """
        print("1===========================", index_of_flow)
        res = self.engine.select_or_change_flow(index_of_flow)
        res2 = self.engine.progress()
        return f"{res} \n {res2}"

    @function_tool()
    async def send_params_for_current_flow(
        self,
        context: RunContext,
        data: dict,
    ) -> dict[str, Any]:
        """
        input for the current step given by the user

        Args:
            data: dictionay contains the data.
        """
        print("1===========================", data)
        res = self.engine.send_params_for_current_flow(data)
        res2 = self.engine.progress()
        return f"{res} \n {res2}"


server = AgentServer()

@server.rtc_session(agent_name="electropi-agent")
async def my_agent(ctx: agents.JobContext):

    metadata = json.loads(ctx.job.metadata)
    print("===> ", metadata)
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            voice="Leda",
            model="gemini-2.5-flash-native-audio-preview-09-2025",
        )
    )

    engine = Engine(metadata["websiteName"], metadata["userId"])
    agent = Assistant(engine=engine)

    await session.start(
        room=ctx.room,
        agent=agent,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
            ),
        ),
    )

    await session.generate_reply(
        instructions="""
Greet the user and offer your assistance. You should start by speaking in Arabic.
and offer the user available options ( flows ) to start/select
"""
    )


if __name__ == "__main__":
    agents.cli.run_app(server)