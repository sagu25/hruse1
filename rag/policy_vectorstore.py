import os
from langchain_core.documents import Document
from config.settings import RAG_CONFIG
from database.db_connection import db

class PolicyRAG:
    """RAG system for retrieving company policies using direct database queries"""

    def __init__(self):
        self.policies = []
        self._load_policies()

    def _load_policies(self):
        """Load policies from database"""
        try:
            query = "SELECT policy_id, policy_name, policy_type, policy_content, doc_id FROM policies"
            results = db.fetch_all(query)

            self.policies = []
            for row in results:
                policy_id, policy_name, policy_type, policy_content, doc_id = row
                doc = Document(
                    page_content=policy_content,
                    metadata={
                        "policy_id": policy_id,
                        "policy_name": policy_name,
                        "policy_type": policy_type,
                        "doc_id": doc_id or ""
                    }
                )
                self.policies.append(doc)

            print(f"Loaded {len(self.policies)} policies from database")
        except Exception as e:
            print(f"Warning: Could not load policies: {e}")
            self.policies = []

    def query_policies(self, query: str, policy_type: str = None, top_k: int = None):
        """Query policies using keyword matching"""
        k = top_k or RAG_CONFIG.get("top_k", 3)
        query_lower = query.lower()

        results = []
        for doc in self.policies:
            # Filter by policy_type if specified
            if policy_type and doc.metadata.get("policy_type") != policy_type:
                continue

            # Simple keyword matching - check if query terms appear in content
            content_lower = doc.page_content.lower()
            policy_name_lower = doc.metadata.get("policy_name", "").lower()
            doc_id_lower = doc.metadata.get("doc_id", "").lower()

            # Check for matches
            query_terms = query_lower.split()
            matches = sum(1 for term in query_terms if term in content_lower or term in policy_name_lower or term in doc_id_lower)

            if matches > 0:
                results.append((doc, matches))

        # Sort by number of matches (descending) and return top k
        results.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in results[:k]]

    def add_policy(self, policy_id: str, policy_name: str, policy_type: str,
                   policy_content: str, doc_id: str = None):
        """Add a new policy"""
        doc = Document(
            page_content=policy_content,
            metadata={
                "policy_id": policy_id,
                "policy_name": policy_name,
                "policy_type": policy_type,
                "doc_id": doc_id or ""
            }
        )
        self.policies.append(doc)
        print(f"Added policy {policy_id}")

    def refresh_vectorstore(self):
        """Refresh policies from database"""
        print("Refreshing policies from database...")
        self._load_policies()
        print("Policies refreshed successfully")

# Global RAG instance (lazy initialization)
_policy_rag = None

def get_policy_rag():
    """Get or create the PolicyRAG instance"""
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
