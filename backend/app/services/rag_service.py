import json
from typing import List, Tuple

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger("rag_service")

class RAGService:
    def __init__(self):
        # Embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # Vector store
        self.vector_store = Chroma(
            collection_name="ai_knowledge_docs",
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PATH,
        )
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        # LLM – model is configurable via GEMINI_MODEL env var
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=settings.TEMPERATURE,
        )
        # Prompt that forces source‑only answers and proper citations
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

    def process_and_store_document(self, text: str, document_id: str, filename: str, owner_id: str) -> None:
        """Chunk a document's text, embed the chunks and store them with ownership metadata.
        Args:
            text: Full extracted text of the PDF.
            document_id: Primary key of the Document record.
            filename: Original uploaded filename (used for citation purposes).
            owner_id: ID of the user who uploaded the document – used for isolation.
        """
        if not text.strip():
            logger.warning(f"Empty text for document {document_id}")
            return

        chunks = self.text_splitter.split_text(text)
        metadatas = [
            {"owner_id": owner_id, "document_id": document_id, "source": filename, "chunk": i}
            for i in range(len(chunks))
        ]
        self.vector_store.add_texts(texts=chunks, metadatas=metadatas)
        logger.info(f"Stored {len(chunks)} chunks for document {document_id}")

    def query_documents(self, question: str, user_id: str) -> Tuple[str, List[dict]]:
        """Retrieve relevant chunks for a user and generate an answer.
        Returns a tuple of (answer, sources) where sources is a list of dictionaries
        containing citation information.
        """
        # Retrieve only vectors belonging to the requesting user
        try:
            docs = self.vector_store.similarity_search(
                question,
                k=settings.TOP_K_RETRIEVAL,
                where={"owner_id": user_id},
            )
        except Exception as e:
            logger.error(f"Vector store similarity search failed: {e}")
            return "Sorry, I could not retrieve relevant information.", []

        if not docs:
            return "I couldn't find this information in your uploaded documents.", []

        context_parts: List[str] = []
        sources: List[dict] = []
        for doc in docs:
            metadata = doc.metadata
            source_name = metadata.get("source", "Unknown Document")
            chunk_num = metadata.get("chunk", "Unknown")
            context_parts.append(f"Source: {source_name} (Chunk {chunk_num})\nContent: {doc.page_content}")
            sources.append({"source": source_name, "chunk": chunk_num})

        context = "\n\n".join(context_parts)
        prompt = self.prompt_template.format(context=context, question=question)

        try:
            response = self.llm.invoke(prompt)
            answer = response.content
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            answer = "Sorry, I encountered an error while trying to answer your question."
        return answer, sources

    def delete_document_vectors(self, document_id: str) -> None:
        """Delete all vector entries that belong to a specific document.
        Uses the underlying Chroma collection's `delete` method with a metadata filter.
        """
        try:
            # The underlying Chroma collection is accessible via the private `_collection` attribute.
            # This call removes all items where the metadata field `document_id` matches.
            self.vector_store._collection.delete(where={"document_id": document_id})
            logger.info(f"Deleted vectors for document {document_id}")
        except Exception as e:
            logger.error(f"Failed to delete vectors for document {document_id}: {e}")

# Singleton instance used throughout the application
rag_service = RAGService()
