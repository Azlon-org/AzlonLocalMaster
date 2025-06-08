import os
import chromadb
import sys
from tqdm import tqdm
from html2text import html2text

sys.path.extend(['.', '..'])
from api_handler import load_api_config
from llm import OpenaiEmbeddings, LLM
from memory import Memory, split_sklearn, split_tools
# from state import State


class RetrieveTool:
    def __init__(self, model: str, embeddings: OpenaiEmbeddings, doc_path: str = 'multi_agents/tools/ml_tools_doc', collection_name: str = 'tools'):
        self.llm = model
        # self.embeddings = embeddings # Commented out: No active embedding calls
        self.doc_path = os.path.join(os.getcwd(), doc_path)
        # self.client = chromadb.PersistentClient(path='multi_agents/db') # Commented out: No active chromadb usage
        self.collection_name = collection_name

        # self.db = Memory(self.client, self.collection_name, self.embeddings) # Commented out: No active Memory/DB usage
 
    def create_db_sklearn(self, doc_type: str = '.rst'): # or .html
        rst_path = []
        if os.path.exists(self.doc_path) and os.path.isdir(self.doc_path):
            for file in os.listdir(self.doc_path):
                # Ensure it checks only files in 'pandas/reference' and not sub-folders
                file_path = os.path.join(self.doc_path, file)
                # read .rst files
                if os.path.isfile(file_path) and file.endswith(doc_type):
                    rst_path.append(file_path)
        
        # Read the HTML files   
        for path in tqdm(rst_path):
            with open(path, 'r') as f:
                content = f.read()
                content = html2text(content)
                chunks = split_sklearn(content)
                # self.db.insert_vectors(chunks, path) # Commented out: No active embedding calls

    def query_sklearn(self, query: str):
        # results = self.db.search_context(query) # Commented out: No active embedding calls
        # path = results['metadatas'][0][0]['doc name']
        # # print(path)
        # details = []
        # for i in results['metadatas'][0]:
        #     path = i['doc name']
        #     # open the html file
        #     with open(path, 'r') as f:
        #         content = f.read()
        #         content = html2text(content)
        #         details.append(content)

        # prompt = ''' Based on the instruction "{details}", extract the top-3 most relevant key information from the following text. Just output in the following json format:
        # {{
        #     "name of the function 1": {{str="exaplantion of function 1", str="code example of function 1"}},
        #     "name of the function 2": {{str="exaplantion of function 2", str="code example of function 2"}},
        #     "name of the function 3": {{str="exaplantion of function n", str="code example of function 3"}}
        # }}

        # text: {content}
        # '''
        # prompt = prompt.format(details=details, content=content)
        # conclusion, _ = self.llm.generate(prompt, history=None)
        
        # return conclusion
        return "Querying sklearn documentation is currently disabled."
    
    def create_db_tools(self, doc_type: str = '.md'):
        md_path = []
        if os.path.exists(self.doc_path) and os.path.isdir(self.doc_path):
            for file in os.listdir(self.doc_path):
                # Ensure it checks only files in 'pandas/reference' and not sub-folders
                file_path = os.path.join(self.doc_path, file)
                # read .rst files
                if os.path.isfile(file_path) and file.endswith(doc_type):
                    md_path.append(file_path)

        # print(md_path)
        # Read the HTML files
        # num_data = self.db.check_collection_none() # Commented out: No active DB usage
        # if num_data == 0: # Commented out: No active DB usage
        #     for path in tqdm(md_path):
        #         with open(path, 'r') as f:
        #             content = f.read()
        #             chunks = split_tools(content)
        #             # self.db.insert_vectors(chunks, path.split('/')[-1]) # Commented out: No active embedding calls

    def query_tools(self, query: str, state_name: str='data_cleaning'):
        # label = state_name + '_tools.md'
        # results = self.db.search_context_with_metadatas(query, label) # Commented out: No active embedding calls
        # return results['documents'][0][0]
        return "Querying tools is currently disabled."


            


def main():
    # print(load_api_config())
    # embeddings = OpenaiEmbeddings(api_key='') # Commented out: No active embedding calls
    # llm = LLM('gpt-4.1', 'api') # Commented out

    # tool = RetrieveTool(llm, embeddings) # Commented out
    # # tool.create_db_tools() # Commented out
    # conclusion = tool.query_tools('Use the fill_missing_values tool.') # Commented out
    # print(conclusion) # Commented out
    print("RetrieveTool main() is currently disabled due to no active embedding calls.")



if __name__ == '__main__':
    main()
        