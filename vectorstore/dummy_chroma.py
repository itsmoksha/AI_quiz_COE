import chromadb
import os

PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")

def get_chroma_collection(collection_name: str = "cybersecurity_modules"):
    """
    Initializes a persistent ChromaDB collection and populates it
    with sample chapter materials for testing RAG retrieval.
    """
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_or_create_collection(name=collection_name)

    # Ingest baseline chapters if collection is empty
    if collection.count() == 0:
        sample_chapters = [
            {
                "id": "sqli_ch1",
                "text": (
                    "SQL Injection (SQLi) occurs when untrusted user input is directly concatenated "
                    "into database queries without proper sanitization. The primary and most effective defense "
                    "against SQLi is the use of Parameterized Queries (Prepared Statements), which ensure the "
                    "database interpreter treats user input strictly as data rather than executable code. "
                    "Secondary defenses include input validation using allowlists and enforcing the principle "
                    "of least privilege on database accounts."
                ),
                "metadata": {
                    "module": "web_security",
                    "chapter_title": "SQL Injection & Defense",
                    "track": "beginner"
                }
            },
            {
                "id": "k8s_ch2",
                "text": (
                    "Kubernetes uses health probes to monitor pod containers: Startup probes determine if "
                    "an application has started; Readiness probes verify if a pod is ready to accept incoming "
                    "network traffic (traffic is rerouted away if failing); Liveness probes verify if the container "
                    "is still alive (kubelet terminates and restarts the container if failing). An OOMKilled "
                    "(Exit Code 137) status indicates that the container exceeded its defined memory limit."
                ),
                "metadata": {
                    "module": "cloud_security",
                    "chapter_title": "Kubernetes Container Health",
                    "track": "advanced"
                }
            }
        ]

        collection.add(
            ids=[c["id"] for c in sample_chapters],
            documents=[c["text"] for c in sample_chapters],
            metadatas=[c["metadata"] for c in sample_chapters]
        )

    return collection

def retrieve_chapter_context(collection, query: str, n_results: int = 1) -> str:
    """
    Queries ChromaDB and returns the most semantically relevant chapter chunk.
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    if results and results["documents"] and len(results["documents"][0]) > 0:
        return results["documents"][0][0]
    return ""