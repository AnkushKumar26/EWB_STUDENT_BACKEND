"""
LangGraph workflow: a Gemini chat model bound to the student-query tools,
with a tool-calling loop (agent -> tools -> agent -> ... -> end).
"""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import Annotated, TypedDict

from app.chatbot.tools import ALL_TOOLS
from app.core.config import settings

SYSTEM_PROMPT = (
    "You are a helpful assistant for a student records system. "
    "Use the available tools to look up real data before answering questions "
    "about students. If a question is conceptual/fuzzy (e.g. about a topic of "
    "study), prefer the semantic search tool. Be concise and factual."
)


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]


def _build_graph():
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0,
    ).bind_tools(ALL_TOOLS)

    def call_model(state: ChatState) -> ChatState:
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: ChatState) -> str:
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "tools"
        return END

    graph = StateGraph(ChatState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(ALL_TOOLS))

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


_compiled_graph = None


def get_graph():
    """Lazily build (and cache) the compiled LangGraph app."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_graph()
    return _compiled_graph


def ask(question: str) -> str:
    """Run one question through the graph and return the final text answer."""
    result = get_graph().invoke(
        {"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=question)]}
    )
    final_message = result["messages"][-1]
    return final_message.content
