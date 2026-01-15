import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config.settings import GOOGLE_API_KEY, RAG_CONFIG
from database.db_connection import db

class PolicyRAG:
    """RAG system for retrieving company policies"""

    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        self.vectorstore_path = RAG_CONFIG["vectorstore_path"]
        self.vectorstore = None
        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """Initialize or load existing vectorstore"""
        if os.path.exists(self.vectorstore_path):
            print("Loading existing policy vectorstore...")
            self.vectorstore = Chroma(
                persist_directory=self.vectorstore_path,
                embedding_function=self.embeddings
            )
        else:
            print("Creating new policy vectorstore...")
            self._create_vectorstore()

    def _create_vectorstore(self):
        """Create vectorstore from policies in database"""
        # Fetch all policies from database
        query = "SELECT policy_id, policy_name, policy_type, policy_content, doc_id FROM policies"
        policies = db.fetch_all(query)

        if not policies:
            print("No policies found in database. Creating empty vectorstore.")
            try:
                self.vectorstore = Chroma(
                    persist_directory=self.vectorstore_path,
                    embedding_function=self.embeddings
                )
            except Exception as e:
                print(f"Warning: Could not create vectorstore: {e}")
                self.vectorstore = None
            return

        # Create documents
        documents = []
        for policy in policies:
            policy_id, policy_name, policy_type, policy_content, doc_id = policy
            doc = Document(
                page_content=policy_content,
                metadata={
                    "policy_id": policy_id,
                    "policy_name": policy_name,
                    "policy_type": policy_type,
                    "doc_id": doc_id or ""
                }
            )
            documents.append(doc)

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=RAG_CONFIG["chunk_size"],
            chunk_overlap=RAG_CONFIG["chunk_overlap"]
        )
        splits = text_splitter.split_documents(documents)

        # Create vectorstore
        try:
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=self.vectorstore_path
            )
            print(f"Vectorstore created with {len(splits)} document chunks")
        except Exception as e:
            print(f"Warning: Could not create vectorstore (API quota?): {e}")
            self.vectorstore = None
            # Store documents for fallback queries
            self._fallback_documents = documents

    def query_policies(self, query: str, policy_type: str = None, top_k: int = None):
        """Query policies using RAG"""
        k = top_k or RAG_CONFIG["top_k"]

        # If vectorstore is not available, use fallback
        if not self.vectorstore:
            if hasattr(self, '_fallback_documents') and self._fallback_documents:
                # Return matching documents from fallback (simple filter)
                results = []
                for doc in self._fallback_documents:
                    if policy_type is None or doc.metadata.get("policy_type") == policy_type:
                        results.append(doc)
                        if len(results) >= k:
                            break
                return results
            return []

        # Build filter if policy_type specified
        filter_dict = {"policy_type": policy_type} if policy_type else None

        # Perform similarity search
        try:
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                filter=filter_dict
            )
            return results
        except Exception as e:
            print(f"Warning: Vectorstore query failed: {e}")
            # Fallback to returning stored documents
            if hasattr(self, '_fallback_documents') and self._fallback_documents:
                results = []
                for doc in self._fallback_documents:
                    if policy_type is None or doc.metadata.get("policy_type") == policy_type:
                        results.append(doc)
                        if len(results) >= k:
                            break
                return results
            return []

    def add_policy(self, policy_id: str, policy_name: str, policy_type: str,
                   policy_content: str, doc_id: str = None):
        """Add a new policy to vectorstore"""
        doc = Document(
            page_content=policy_content,
            metadata={
                "policy_id": policy_id,
                "policy_name": policy_name,
                "policy_type": policy_type,
                "doc_id": doc_id or ""
            }
        )

        # Split and add to vectorstore
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=RAG_CONFIG["chunk_size"],
            chunk_overlap=RAG_CONFIG["chunk_overlap"]
        )
        splits = text_splitter.split_documents([doc])

        if self.vectorstore:
            self.vectorstore.add_documents(splits)
            print(f"Added policy {policy_id} to vectorstore")

    def refresh_vectorstore(self):
        """Refresh vectorstore from database"""
        print("Refreshing policy vectorstore...")
        # Delete existing vectorstore
        if os.path.exists(self.vectorstore_path):
            import shutil
            shutil.rmtree(self.vectorstore_path)

        # Recreate
        self._create_vectorstore()
        if self.vectorstore:
            print("Vectorstore refreshed successfully")
        else:
            print("Vectorstore refresh failed, using fallback mode")

# Global RAG instance (lazy initialization)
_policy_rag = None

def get_policy_rag():
    """Get or create the PolicyRAG instance (lazy initialization)"""
    global _policy_rag
    if _policy_rag is None:
        _policy_rag = PolicyRAG()
    return _policy_rag

# For backward compatibility
class PolicyRAGProxy:
    """Proxy class for lazy initialization of PolicyRAG"""
    def __getattr__(self, name):
        return getattr(get_policy_rag(), name)

policy_rag = PolicyRAGProxy()
