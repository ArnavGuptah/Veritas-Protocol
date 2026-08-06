from app.pipeline.orchestrator import run_pipeline
from app.retrieval.retrieval import Retriever, Document
from app.storage.demo_documents import DEMO_DOCUMENTS
from app.storage.record_store import record_store
from app.blockchain.ledger import ledger, generate_signature

class ReasoningEngine:
    """
    Entry point for all reasoning requests.

    The API should ONLY talk to this class.
    Everything else stays behind this abstraction.
    """

    def __init__(self):

        documents = [
            Document(
                doc_id=doc["doc_id"],
                source=doc["source"],
                text=doc["text"],
            )
            for doc in DEMO_DOCUMENTS
        ]

        self.retriever = Retriever(documents)       

    def process(self, question: str):
        """
        Execute the complete verification pipeline.
        """
        proof = run_pipeline(question=question, retriever=self.retriever,)
        record_store.save(proof)
        signature = generate_signature(proof.root_hash)

        proof.chain_anchor = ledger.anchor(
            record_id=proof.record_id,
            root_hash=proof.root_hash,
            verifier_signature=signature,
        )

        return proof