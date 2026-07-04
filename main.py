import os
import asyncio

from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types

# ---------------------------------------------------------------------------
# 1. Load environment variables
# ---------------------------------------------------------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY not found. Please set it in your .env file.")

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL_NAME = "llama-3.1-8b-instant"

# LiteLlm lets ADK talk to any OpenAI-compatible endpoint (like Groq)
# by prefixing the model with "openai/" and pointing api_base at Groq.
groq_model = LiteLlm(
    model=f"openai/{GROQ_MODEL_NAME}",
    api_base=GROQ_BASE_URL,
    api_key=GROQ_API_KEY,
)


# ---------------------------------------------------------------------------
# 2. Simple security guardrail
# ---------------------------------------------------------------------------
def check_security(prompt: str) -> None:
    """Raises an exception if the prompt looks like a prompt-injection attempt."""
    if "ignore" in prompt.lower():
        raise Exception("Security Alert: Prompt Injection Blocked")


# ---------------------------------------------------------------------------
# 3. Connect to the MCP server (spawns mcp_server.py as a subprocess)
# ---------------------------------------------------------------------------
bank_data_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python3",
            args=["mcp_server.py"],
        ),
    ),
)


# ---------------------------------------------------------------------------
# 4. Define the agents
# ---------------------------------------------------------------------------
risk_analyst_agent = LlmAgent(
    name="risk_analyst_agent",
    model=groq_model,
    description="Analyzes bank client data to flag compliance and risk issues.",
    instruction=(
        "You are a Risk Analyst at a bank. When asked to review a compliance "
        "alert for a client, use the get_client_data tool to fetch the client's "
        "bank records, then produce a concise risk assessment covering: "
        "1) any suspicious activity, 2) an overall risk rating (Low/Medium/High), "
        "and 3) a recommended next action."
    ),
    tools=[bank_data_toolset],
)

orchestrator_agent = LlmAgent(
    name="orchestrator_agent",
    model=groq_model,
    description="Routes banking and compliance requests to the correct specialist agent.",
    instruction=(
        "You are an orchestrator. For any request involving compliance alerts, "
        "risk review, or client account analysis, delegate the task to the "
        "risk_analyst_agent and return its final answer to the user."
    ),
    sub_agents=[risk_analyst_agent],
)


# ---------------------------------------------------------------------------
# 5. Run the agent
# ---------------------------------------------------------------------------
async def main():
    user_prompt = "Please review the compliance alert for Bob Smith."

    # Security check before anything touches the model
    check_security(user_prompt)

    runner = InMemoryRunner(agent=orchestrator_agent, app_name="bank_compliance_app")

    user_id = "coach_user"
    session_id = "session_001"

    await runner.session_service.create_session(
        app_name="bank_compliance_app",
        user_id=user_id,
        session_id=session_id,
    )

    content = types.Content(role="user", parts=[types.Part(text=user_prompt)])

    final_output = None
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_output = event.content.parts[0].text

    print("\n=== FINAL RISK ASSESSMENT ===")
    print(final_output)


if __name__ == "__main__":
    asyncio.run(main())