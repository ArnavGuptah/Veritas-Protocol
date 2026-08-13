"""
Tiny demo corpus so `/ask` works out of the box with no external RAG index.
Replace with your real ingestion pipeline (PDF/HTML -> chunks -> Qdrant) —
the Retriever class only needs a list[Document] with doc_id/source/text.
"""

DEMO_DOCUMENTS = [

    {
        "doc_id": "who_tb",
        "source": "World Health Organization — Tuberculosis",
        "text": """
Tuberculosis (TB) is an infectious disease caused by the bacterium
Mycobacterium tuberculosis. It most often affects the lungs, although
it can affect other parts of the body.

TB bacteria are spread through the air when people with pulmonary
tuberculosis cough, sneeze, speak or spit. A person needs only to
inhale a small number of these bacteria to become infected.

Tuberculosis is preventable and curable. TB disease is treated with
antibiotic medicines, and treatment requires taking multiple medicines
over a period of several months.
""",
    },

    {
        "doc_id": "cdc_tb",
        "source": "CDC — Tuberculosis",
        "text": """
Tuberculosis is caused by Mycobacterium tuberculosis bacteria.
The bacteria usually attack the lungs, but TB bacteria can attack
any part of the body such as the kidney, spine, and brain.

TB bacteria spread through the air from one person to another.
People with active TB disease of the lungs or throat can spread
the bacteria when they cough, speak, or sing.

Not everyone infected with TB bacteria becomes sick. Some people
develop inactive TB infection, while others develop TB disease.
TB disease can be treated with several medicines.
""",
    },

    {
        "doc_id": "nobel_physics_2022",
        "source": "Nobel Prize — Physics 2022",
        "text": """
The 2022 Nobel Prize in Physics was awarded jointly to Alain Aspect,
John F. Clauser and Anton Zeilinger for experiments with entangled
photons, establishing the violation of Bell inequalities and
pioneering quantum information science.

The laureates conducted experiments using entangled quantum states,
demonstrating important foundations for quantum information science.
""",
    },

    {
        "doc_id": "ipcc_ar6",
        "source": "IPCC — AR6 Synthesis Report",
        "text": """
Human activities, principally through emissions of greenhouse gases,
have unequivocally caused global warming. Global surface temperature
reached approximately 1.1°C above the 1850–1900 average during
2011–2020.

Widespread and rapid changes have occurred in the atmosphere, ocean,
cryosphere and biosphere.
""",
    },

    {
        "doc_id": "cancer_aspirin",
        "source": "Peer-reviewed oncology review",
        "text": """
There is no clinical evidence that aspirin cures cancer.

Some observational research suggests that regular low-dose aspirin
use may be associated with a modest reduction in the risk of certain
cancers, particularly colorectal cancer. This association is not
equivalent to a treatment effect and does not establish that aspirin
cures existing cancer.

Aspirin is not a standard treatment for curing cancer.
""",
    },
]