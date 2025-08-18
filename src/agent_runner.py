import json
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from config import CHAT_MODEL
from agent_tools import make_tools
from build_index import build_or_load_vectorstore

SYSTEM = """\
You are a precise financial-analyst AI. Always:
- Decompose complex or comparative questions into sub-queries.
- Use the `sec_10k_search` tool to retrieve evidence.
- When asked to compute growth or do numeric comparisons, use the `calculator` tool.
- Cite sources from the retrieved documents by returning their metadata (ticker, year, page, file).
Return your final output STRICTLY as minified JSON with keys:
  "query": <original user question string>,
  "answer": <concise direct answer string>,
  "reasoning": <1-3 sentence reasoning describing decomposition and synthesis>,
  "sub_queries": [<each sub-query string you used in order>],
  "sources": [
    {{"ticker": "...", "year": "...", "page": <int>, "file": "...", "excerpt": "<<=200 chars from that chunk>"}}
  ]
If a data point is missing or ambiguous, say so clearly in "answer" and "reasoning" and still include any partial sources.
Be concise. Do not include extra keys.
"""

# The agent sees its tool call transcripts in the scratchpad and must aggregate them into JSON.
PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM),
        ("user", "Question: {input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

def _minify_json_text(s: str) -> str:
    try:
        return json.dumps(json.loads(s), ensure_ascii=False, separators=(",", ":"))
    except Exception:
        # If the model didn't emit perfect JSON, wrap as plain text (still valid JSON string)
        return json.dumps({"raw": s})

def make_agent() -> AgentExecutor:
    vectorstore = build_or_load_vectorstore()
    tools = make_tools(vectorstore)
    llm = ChatOpenAI(model=CHAT_MODEL, temperature=0)
    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=PROMPT)
    return AgentExecutor(agent=agent, tools=tools, verbose=False)

def ask(agent: AgentExecutor, question: str) -> str:
    out: Dict[str, Any] = agent.invoke({"input": question}, config=RunnableConfig())
    text = out["output"]
    return _minify_json_text(text)
