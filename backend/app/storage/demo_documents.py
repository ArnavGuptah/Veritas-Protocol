"""
Tiny demo corpus so `/ask` works out of the box with no external RAG index.
Replace with your real ingestion pipeline (PDF/HTML -> chunks -> Qdrant) —
the Retriever class only needs a list[Document] with doc_id/source/text.
"""

DEMO_DOCUMENTS = [
    {
        "doc_id": "doc1",
        "source": "Nobel Prize official archive",
        "text": (
            "The Nobel Prize in Physics 2022 was awarded jointly to Alain Aspect, "
            "John F. Clauser and Anton Zeilinger for experiments with entangled "
            "photons, establishing the violation of Bell inequalities and "
            "pioneering quantum information science.\n\n"
            "The three laureates each conducted groundbreaking experiments using "
            "entangled quantum states, where two particles behave like a single "
            "unit even when separated."
        ),
    },
    {
        "doc_id": "doc2",
        "source": "Peer-reviewed oncology review (BMJ)",
        "text": (
            "No clinical evidence supports the claim that aspirin cures cancer. "
            "Some observational studies suggest regular low-dose aspirin use may "
            "modestly reduce risk of certain cancers (notably colorectal) over "
            "long time horizons, but this is a risk-reduction association, not "
            "a treatment effect, and is not equivalent to curing existing cancer.\n\n"
            "Aspirin's anti-cancer research is limited to prevention hypotheses "
            "and is not part of standard oncology treatment protocols."
        ),
    },
    {
        "doc_id": "doc3",
        "source": "IPCC AR6 Synthesis Report",
        "text": (
            "Human activities, principally through emissions of greenhouse gases, "
            "have unequivocally caused global warming, with global surface "
            "temperature reaching 1.1C above 1850-1900 in 2011-2020.\n\n"
            "Widespread and rapid changes have occurred in the atmosphere, ocean, "
            "cryosphere and biosphere."
        ),
    },
]
