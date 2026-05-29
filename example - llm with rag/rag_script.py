import os  # To interact with the file system (list files)

# --- Core LangChain Components ---
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from pypdf import PdfReader

# --- Configuration ---
SOURCE_DIRECTORY = "source_docs"  # Folder with your PDF files
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "phi4-mini"

print("--- Simple RAG Demo ---")
print(f"Using Ollama model: {OLLAMA_MODEL}")
print(f"Looking for PDFs in: '{SOURCE_DIRECTORY}'")


def load_pdf_texts(source_directory):
    pdf_texts = []
    pdf_metadatas = []

    for filename in os.listdir(source_directory):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(source_directory, filename)
        print(f"  Loading {filename}...")
        pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(pdf_path).pages)
        pdf_text = pdf_text.strip()
        if not pdf_text:
            continue

        pdf_texts.append(pdf_text)
        pdf_metadatas.append({"source": pdf_path})

    return pdf_texts, pdf_metadatas


def format_context(documents):
    formatted_chunks = []
    for doc in documents:
        source_name = os.path.basename(doc.metadata.get("source", "Unknown"))
        formatted_chunks.append(f"Source: {source_name}\n{doc.page_content}")

    return "\n\n".join(formatted_chunks)

# --- 1. Load Documents ---
pdf_texts, pdf_metadatas = load_pdf_texts(SOURCE_DIRECTORY)

print(f"Loaded {len(pdf_texts)} PDF(s).")

# --- 2. Split Documents ---
print("Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)
split_chunks = text_splitter.create_documents(pdf_texts, metadatas=pdf_metadatas)
print(f"Split into {len(split_chunks)} chunks.")

# --- 3. Create Embeddings & Vector Store ---
# Embeddings turn text chunks into numerical vectors
print("Creating embeddings and vector store (may take a moment)...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
# Chroma is a vector store.
vector_store = Chroma.from_documents(
    documents=split_chunks, embedding=embeddings
)
print("Vector store created.")

# --- 4. Initialize LLM ---
print(f"Initializing LLM: {OLLAMA_MODEL}...")
# Assumes Ollama is running and the model is pulled
llm = OllamaLLM(model=OLLAMA_MODEL)
print("LLM initialized.")

# --- 5. Create RAG Chain ---
# Prompt Template: How we ask the LLM, using retrieved context
prompt_template = """
Answer the following question based only on the provided context:

Context:
{context}

Question:
{input}

Answer:"""
prompt = ChatPromptTemplate.from_template(prompt_template)

# Retriever: Gets relevant chunks from the vector store
retriever = vector_store.as_retriever(search_type="mmr")

print("\nRAG system ready!")

# --- 6. Ask Questions Loop ---
while True:
    query = input("\nEnter your question (or type 'exit' to quit): ")
    if query.lower() == "exit":
        break
    if not query.strip():
        continue

    print("Thinking...")
    retrieved_docs = retriever.invoke(query)
    context = format_context(retrieved_docs)
    prompt_value = prompt.invoke(
        {
            "context": context or "No relevant context was retrieved.",
            "input": query,
        }
    )
    answer = llm.invoke(prompt_value)

    print("\nAnswer:")
    print(answer)
    print("-" * 50)

print("Goodbye!")
