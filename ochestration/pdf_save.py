import pymupdf4llm
import json
from ochestration.main import llm
from fastembed import TextEmbedding
from database.conn import Session
from database.models import DevAgentTable
from sqlalchemy import insert


model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

initial_message = [{"role":"system", "content": """
You are an expert semantic analyst and data extraction engine. 

Your task is to analyze the provided raw text and segment it into distinct, chronological sections based on major topic shifts. 

INSTRUCTIONS:
1. Identify the primary themes and logical breaks in the text.
2. Group the text into contiguous chunks based on these themes. 
3. Do not summarize, paraphrase, or omit any information. The combined content of your chunks must perfectly reconstruct the original text.
4. Assign a concise, descriptive string title to each topic.

CONSTRAINTS:
- You must output ONLY valid JSON.
- Do not include conversational filler, preamble, or explanations.
- Do not wrap the output in markdown blocks (e.g., no ```json).

OUTPUT SCHEMA:
{
  "document_analysis": [
    {
      "topic": "text_chunk"
    }
  ]
}"""}]
def add_chunks(path: str):
    pdf = pymupdf4llm.to_markdown(path)
    initial_message.append({"role":"user","content": pdf})
    result =llm.invoke(initial_message)
    print(f'llm chunks: \n\n {result} \n')
    result = result.content
    data = json.loads(result[0]['text'])
    print(type(json.loads(result[0]['text']))) 
    for index in data['document_analysis']:
        for key,value in index.items():
            content = f'topic: {key}, content: {value}'
            print(f'\n{content}\n')
            embedding_list = list(model.embed(content))
            embedding_vector = embedding_list[0]
            embedding = embedding_vector.tolist()
            print(f'vector: \n\n {embedding}')
            with Session() as db:
                db.execute(insert(DevAgentTable).values(content=value,title=key,source='pdf',vector= embedding))
                db.commit()
user = input(f'input file path of document: ')
add_chunks(user)