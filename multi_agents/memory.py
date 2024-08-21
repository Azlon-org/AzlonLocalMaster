import chromadb
from chromadb.api.client import Client
import re
from tqdm import tqdm
import json

# from SOP import SOP
from LLM import OpenaiEmbeddings


def transfer_text_to_json(content: str):
    # Use regular expression to find the JSON data
    json_match = re.search(r'```json\n(.*?)```', content, re.DOTALL)

    if json_match:
        # Extract the JSON string
        json_str = json_match.group(1)
        data = json.loads(json_str)
        return data
    else:
        return None


class Memory:
    def __init__(self, client: Client, collection_name: str, embedding_model: OpenaiEmbeddings):
        self.chroma_client = client
        self.collection_name = collection_name
        # choose cosine similarity for the search
        self.collection = self.chroma_client.get_or_create_collection(self.collection_name, metadata={"hnsw:space": "cosine"}) 

        # Load the embedding model 
        self.embedding_model = embedding_model
        
    def insert_vectors(self, chunks: list):
        results = chunks
        # insert the vectors into the collection
        for idx, result in tqdm(enumerate(results)):
            text_embedding = self.embedding_model.encode(result)[0].embedding
            
            # insert the vectors into the collection
            self.collection.add(
                documents=result,
                ids=f'{idx}',
                embeddings=text_embedding,
            )
        print('---------------------------------')
        print(f'Finished inserting vectors for <{self.collection_name}>!')
        print('---------------------------------')

    # use the query to search the most similar context
    def search_context(self, query: str, n_results=2) -> dict:
        query_embeddings = self.embedding_model.encode(query)[0].embedding
        results =  self.collection.query(query_embeddings=query_embeddings, n_results=n_results, include=['documents', 'distances', 'embeddings'])
        return results


def test_db():

    with open("multi_agents/competition/titanic/understand_background/summarizer_reply.txt", 'r') as f:
        text = f.read()
    json_data = transfer_text_to_json(text)
    # trasnfer json data to list of strings
    # json_data = json_data.split('\n')
    print(json_data['final_answer'])

    # chunks = chunk_text(json_data)
    # print(chunks)  


if __name__ == '__main__':
    test_db()
    pass