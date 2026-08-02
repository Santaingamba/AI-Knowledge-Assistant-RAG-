import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger("rag_service")

class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = Chroma(
            collection_name="ai_knowledge_docs",
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PATH,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-latest", # Adjust if needed
            google_api_key=settings.GEMINI_API_KEY,
            temperature=settings.TEMPERATURE
        )
        
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are an AI Knowledge Assistant. 
Only answer from the retrieved documents below. 
Never fabricate information. 
If the context is insufficient, respond honestly with "I couldn't find this information in your uploaded documents."
Always cite the document names.

Context:
{context}

Question:
{question}

Answer:"""
        )

    def process_and_store_document(self, text: str, document_id: str, filename: str):
        if not text.strip():
            logger.warning(f"Empty text for document {document_id}")
            return
            
        chunks = self.text_splitter.split_text(text)
        metadatas = [{"document_id": document_id, "source": filename, "chunk": i} for i in range(len(chunks))]
        
        # Add to Chroma
        self.vector_store.add_texts(texts=chunks, metadatas=metadatas)
        logger.info(f"Stored {len(chunks)} chunks for document {document_id}")

    def query_documents(self, question: str):
        # Retrieve
        docs = self.vector_store.similarity_search(question, k=settings.TOP_K_RETRIEVAL)
        
        if not docs:
            return "I couldn't find this information in your uploaded documents.", []
            
        context_parts = []
        sources = []
        
        for doc in docs:
            metadata = doc.metadata
            source_name = metadata.get("source", "Unknown Document")
            chunk_num = metadata.get("chunk", "Unknown")
            
            context_parts.append(f"Source: {source_name} (Chunk {chunk_num})\nContent: {doc.page_content}")
            sources.append({
                "source": source_name,
                "chunk": chunk_num
            })
            
        context = "\n\n".join(context_parts)
        
        # Format prompt
        prompt = self.prompt_template.format(context=context, question=question)
        
        # Generate response
        try:
            response = self.llm.invoke(prompt)
            answer = response.content
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            answer = "Sorry, I encountered an error while trying to answer your question."
            
        return answer, sources

rag_service = RAGService()
