from openai import OpenAI
import chromadb
from chromadb.api.client import Client
import re

from llms import OpenaiEmbeddings
from SOP import SOP


def chunk_text(texts: str) -> list:
    # if there are multi-blocks inside a agent, split them.
    # split the text by the '### BLOCK '
    blocks = re.split(r'### BLOCK', texts)
    # inside each block, split the text by the '#### CODE:' and '#### EXPLANATION:'
    results = []
    for block in blocks:
        # detect the text after '#### CODE:' and '#### EXPLANATION:'
        pattern_code = r'#### CODE:\n(.*?)\n#### EXPLANATION:'
        pattern_explanation = r'#### EXPLANATION:\n(.*)'
        code_match = re.search(pattern_code, block, re.DOTALL)
        code = code_match.group(1).strip() if code_match else ''
        # print(code)
        # Extract the explanation block
        explanation_match = re.search(pattern_explanation, block, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else ''
        # print(explanation)
        # Create the dictionary
        result = {
            'code': code,
            'explanation': explanation
        }
        results.append(result)

    return results


class VectorStore:
    def __init__(self, client: Client, collection_name: str, api_key: str, base_url: str):
        self.chroma_client = client
        self.collection_name = collection_name
        # choose cosine similarity for the search
        self.collection = self.chroma_client.get_or_create_collection(self.collection_name, metadata={"hnsw:space": "cosine"}) 

        # Load the embedding model 
        self.embedding_model = OpenaiEmbeddings(api_key, base_url)

    def insert_vectors(self, texts: str):
        # ToDO: chunk the text into smaller pieces
        results = chunk_text(texts)
        # delete if the results[idx]['code'] is empty
        results = [result for result in results if result['code']]
        # insert the vectors into the collection
        for idx, result in enumerate(results):
            code = result['code']
            explanation = result['explanation']
            # encode the code and explanation
            explanation_embedding = self.embedding_model.encode(explanation).data[0].embedding
            # insert the vectors into the collection
            metadatas = {'code': code}

            self.collection.add(
                documents=explanation,
                ids=f'{idx}',
                metadatas=metadatas,
                embeddings=explanation_embedding,
            )
        print('---------------------------------')
        print(f'Finished inserting vectors for <{self.collection_name}>!')
        print('---------------------------------')

    # use the query to search the most similar context
    def search_context(self, query: str, n_results=2) -> dict:
        query_embeddings = self.embedding_model.encode(query).data[0].embedding
        results =  self.collection.query(query_embeddings=query_embeddings, n_results=n_results, include=['documents', 'metadatas', 'distances', 'embeddings'])
        return results


class Memory:
    def __init__(self, client: Client, sop: SOP, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.chroma_client = client
        self.sop = sop
        self.vector_store = VectorStore(self.client, self.sop.current_state, self.api_key, self.base_url)

    def update_state(self):
        # update the collection of the db to current state
        self.vector_store = VectorStore(self.client, self.sop.current_state, self.api_key, self.base_url)

    def update_memory(self, new_text):
        # change the collection corresponding to the current state
        self.update_state()
        # update the memory in this collection
        self.vector_store.insert_vectors(new_text)

    def clear_memory(self):
        # clear the memory
        if self.sop.check_finished:
            # delete the collection
            self.chroma_client.delete_collection(self.vector_store.collection_name)
        else:
            raise Exception('Not in the clear state!')

    def query_by_similarity(self, query) -> dict:
        results = self.vector_store.search_context(query)
        return results
    

def test_db():
    client = chromadb.Client()
    # print(type(client))
    api_key = 'your_api_key'
    base_url = None
    db = VectorStore(client, 'test', api_key, base_url)
    with open('multi_agents/data_cleaning_code.txt', 'r') as f:
        test_input = f.read()

    db.insert_vectors(test_input)
    results = db.search_context('This block of code loads the training and test datasets from the specified paths and displays the first 10 rows of the training dataset. This helps in getting an initial look at the data and understanding its structure.')
    print(results['documents'])


if __name__ == '__main__':
    test_db()
    pass