import chromadb
import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'chroma_db'))

chroma_client = chromadb.PersistentClient(path=DB_PATH)

def ingest_pdf_directory(collection):
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {data_dir}. Waiting for files to be added.")
        return
        
    print(f"Found {len(pdf_files)} PDFs. Ingesting...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    
    all_chunks = []
    all_metadatas = []
    all_ids = []
    
    doc_id_counter = 1
    for pdf_path in pdf_files:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        chunks = text_splitter.split_documents(pages)
        
        for idx, chunk in enumerate(chunks):
            all_chunks.append(chunk.page_content)
            all_metadatas.append({"source": os.path.basename(pdf_path), "page": chunk.metadata.get("page", 0)})
            all_ids.append(f"doc_{doc_id_counter}_{idx}")
        doc_id_counter += 1
        
    if all_chunks:
        collection.add(
            documents=all_chunks,
            metadatas=all_metadatas,
            ids=all_ids
        )
        print("Successfully ingested documents into ChromaDB!")

def initialize_knowledge_base():
    collection = chroma_client.get_or_create_collection(name="guidelines")
    if collection.count() == 0:
        ingest_pdf_directory(collection)
    return collection

def get_relevant_context(user_query: str) -> str:
    collection = initialize_knowledge_base()
    results = collection.query(
        query_texts=[user_query],
        n_results=2
    )
    if results['documents'] and len(results['documents']) > 0:
        return "\n".join(results['documents'][0])
    return "No specific context found."
