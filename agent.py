from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from . import config as c  # also loads .env
from .tools.rag import rag_search
from .tools.static_tools import (
    list_files_and_functions, find_importers,
    build_architecture_diagram, get_project_overview,
)

model = LiteLlm(model=f"nvidia_nim/{c.CHAT_MODEL}")

file_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", str(c.CODE_PROJECT)],
        ),
        timeout=30,
    ),
    tool_filter=["list_directory", "read_file"],
)

NOT_FOUND = 'If the tool finds nothing useful, say "I could not find that." Never make things up.'

searcher = LlmAgent(
    name="code_searcher", model=model,
    description="Finds WHERE something is in the code (which file and lines). Use for 'where is...' questions.",
    instruction="Call rag_search exactly ONE time, using the user's question as it is. Never call it a second time. Then answer using only the code it returned: say which file and which line numbers hold the answer, and explain it in 2 or 3 simple sentences. If the result is exactly 'I could not find that.', say that sentence.",
    tools=[rag_search],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

explainer = LlmAgent(
    name="code_explainer", model=model,
    description="Reads one whole file and explains what it does. Use for 'explain <file>' questions.",
    instruction=f"Read the requested file with read_file, then explain it simply. {NOT_FOUND}",
    tools=[file_tools],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

mapper = LlmAgent(
    name="architecture_mapper", model=model,
    description="Shows how files connect: imports, functions, dependency diagram. Use for 'which files import...' or 'draw the architecture'.",
    instruction="Use find_importers to answer which files import a file. Call it once, then reply with ONLY the file names it returned, exactly as given. Do not add any file that is not in the result, and never list the file itself. Only call build_architecture_diagram if the user asks for a diagram, and then return the Mermaid code block exactly as given. Never transfer to another agent. Never read file contents. If a tool returns nothing, say 'I could not find that.'",
    tools=[list_files_and_functions, find_importers, build_architecture_diagram],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

guide = LlmAgent(
    name="onboarding_guide", model=model,
    description="Tells a newcomer what the project does, how to run it, and where to start.",
    instruction=f"Call get_project_overview, then give 3-5 short steps for a newcomer. {NOT_FOUND}",
    tools=[get_project_overview],
)

root_agent = LlmAgent(
    name="coordinator", model=model,
    description="Sends each question to the right worker.",
    instruction="Never answer yourself. Transfer to the best worker: "
                "code_searcher (where is X), code_explainer (explain a file), "
                "architecture_mapper (connections/diagram), onboarding_guide (where to start).",
    sub_agents=[searcher, explainer, mapper, guide],
)
