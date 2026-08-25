from typing import TypedDict, Annotated
from langgraph.graph import StateGraph,START,END
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from datetime import datetime, timezone
from langgraph.prebuilt import ToolNode
from langchain.chat_models import init_chat_model
from database.conn import Session
from database.models import DevAgentTable
from sqlalchemy import select
from fastembed import TextEmbedding
from core.settings import settings
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
def check_similarity(prompt):
    embedding_list = list(model.embed(prompt))
    embedding_vector = embedding_list[0]
    embedding = embedding_vector.tolist()
    with Session() as db:
        search = db.execute(select(DevAgentTable).where(DevAgentTable.vector.cosine_distance(embedding) < 0.4).order_by(DevAgentTable.vector.cosine_distance(embedding))
        .limit(2))
        result = search.scalars().all()
    output = f''
    if len(result) > 0:
        for index in result:
            output += f'title: {index.title} content: {index.content} \n\n'
    else:
        output = ""
    return output
llm = init_chat_model("google_genai:gemini-3.1-flash-lite",api_key = settings.GEMINI_API_KEY)
# llm = ChatOllama(model="llama3.2", temperature=0)

def chatbot(state: GraphState):
    result = llm.invoke(state["messages"])
    return {"messages": result}


builder = StateGraph(GraphState)

builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)



graph = builder.compile()

if __name__ == "__main__":
    while True:
        user_input = input("you:   ")
        RAG_DATA = check_similarity(user_input)
        initial_message = [{"role":"system", "content": f"""You are a precise, analytical assistant. Your primary task is to answer the user's question using ONLY the factual information provided in the "Database Context" section below.

        Rules:
        1. If the exact answer is not contained within the Database Context, you must explicitly state: "I do not have enough information in my database to answer this." 
        2. Do not use outside knowledge, speculate, or make assumptions.
        3. Keep your answer concise and directly address the user's query.

        <Database Context>
        {RAG_DATA}
        </Database Context>"""}]
        initial_message.append({"role":"user","content": user_input})
        graph_output = graph.invoke({"messages": initial_message})
        print(f'assistant:   {graph_output["messages"][-1].content[0]['text']}')