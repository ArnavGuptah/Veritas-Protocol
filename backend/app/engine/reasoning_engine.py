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
        
        verdict = proof.verdict.verdict

        print("\n========== VERIFICATION ==========")
        print("Verdict:", verdict)
        print("Confidence:", proof.verdict.confidence_score)
        print("==================================")

        if verdict == "supported":

            signature = generate_signature(proof.root_hash)

            try:
                anchor = ledger.anchor(
                    record_id=proof.record_id,
                    root_hash=proof.root_hash,
                    verifier_signature=signature,
                )

                proof.chain_anchor = anchor

            except Exception as exc:
                print("\n========== BLOCKCHAIN ANCHOR FAILED ==========")
                print("Error:", exc)
                print("Proof remains valid locally.")
                print("==============================================\n")

                proof.chain_anchor = {
                    "status": "pending",
                    "reason": "Blockchain confirmation timed out",
                    "error": str(exc),
                }

        else:

            proof.chain_anchor = {
                "status": "not_anchored",
                "reason": verdict,
            }

        # Save ONLY after the complete proof object has been constructed.
        record_store.save(proof)

        return proof