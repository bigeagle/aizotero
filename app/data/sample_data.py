"""
Sample paper data for development and testing
"""

from datetime import datetime
from pathlib import Path

from app.models.paper import PaperRecord, PaperResponse

# Calculate base directory for sample files
SAMPLE_DIR = Path(__file__).parent / "sample"


SAMPLE_RECORDS = [
    PaperRecord(
        id="ai-001",
        title="Attention Is All You Need",
        authors=[
            "Ashish Vaswani",
            "Noam Shazeer",
            "Niki Parmar",
            "Jakob Uszkoreit",
            "Llion Jones",
            "Aidan N. Gomez",
            "Lukasz Kaiser",
            "Illia Polosukhin",
        ],
        year=2017,
        journal="Advances in Neural Information Processing Systems",
        abstract="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.",
        doi="10.5555/3295222.3295349",
        url="https://arxiv.org/abs/1706.03762",
        pdf_path=None,
        tags=["transformers", "attention", "nlp", "deep-learning"],
        collections=["neural-networks", "transformers"],
        keywords=[
            "attention mechanism",
            "transformer",
            "machine translation",
            "neural networks",
        ],
        notes="Key paper introducing the Transformer architecture",
        date_added=datetime(2024, 1, 15, 10, 30, 0),
        date_modified=datetime(2024, 1, 15, 10, 30, 0),
        zotero_key="ATTENTION2017",
        zotero_version=1,
    ),
    PaperRecord(
        id="ai-002",
        title="Deep Learning for AI",
        authors=["Yann LeCun", "Yoshua Bengio", "Geoffrey Hinton"],
        year=2015,
        journal="Nature",
        abstract="Deep learning allows computational models that are composed of multiple processing layers to learn representations of data with multiple levels of abstraction. These methods have dramatically improved the state-of-the-art in speech recognition, visual object recognition, and many other domains.",
        doi="10.1038/nature14539",
        url="https://www.nature.com/articles/nature14539",
        pdf_path=None,
        tags=["deep-learning", "neural-networks", "review", "foundations"],
        collections=["foundations", "reviews"],
        keywords=[
            "deep learning",
            "neural networks",
            "machine learning",
            "artificial intelligence",
        ],
        notes="Foundational review paper on deep learning",
        date_added=datetime(2024, 1, 16, 14, 20, 0),
        date_modified=datetime(2024, 1, 16, 14, 20, 0),
        zotero_key="DEEPLEARNING2015",
        zotero_version=1,
    ),
    PaperRecord(
        id="ai-003",
        title="BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        authors=["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
        year=2018,
        journal="arXiv preprint",
        abstract="We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context.",
        doi="10.48550/arXiv.1810.04805",
        url="https://arxiv.org/abs/1810.04805",
        pdf_path=None,
        tags=["bert", "transformers", "nlp", "pre-training"],
        collections=["transformers", "nlp", "pre-training"],
        keywords=["bert", "transformer", "language model", "pre-training", "nlp"],
        notes="Introduced BERT model for bidirectional language understanding",
        date_added=datetime(2024, 1, 17, 9, 15, 0),
        date_modified=datetime(2024, 1, 17, 9, 15, 0),
        zotero_key="BERT2018",
        zotero_version=1,
    ),
    PaperRecord(
        id="ai-004",
        title="Generative Adversarial Networks",
        authors=[
            "Ian Goodfellow",
            "Jean Pouget-Abadie",
            "Mehdi Mirza",
            "Bing Xu",
            "David Warde-Farley",
            "Sherjil Ozair",
            "Aaron Courville",
            "Yoshua Bengio",
        ],
        year=2014,
        journal="Advances in Neural Information Processing Systems",
        abstract="We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G that captures the data distribution, and a discriminative model D that estimates the probability that a sample came from the training data rather than G.",
        doi="10.5555/2969033.2969125",
        url="https://arxiv.org/abs/1406.2661",
        pdf_path=None,
        tags=["gan", "generative-models", "adversarial", "deep-learning"],
        collections=["generative-models", "deep-learning"],
        keywords=[
            "generative adversarial networks",
            "gan",
            "generative models",
            "unsupervised learning",
        ],
        notes="Introduced GANs framework for generative modeling",
        date_added=datetime(2024, 1, 18, 11, 45, 0),
        date_modified=datetime(2024, 1, 18, 11, 45, 0),
        zotero_key="GAN2014",
        zotero_version=1,
    ),
    PaperRecord(
        id="ai-005",
        title="Language Models are Few-Shot Learners",
        authors=[
            "Tom B. Brown",
            "Benjamin Mann",
            "Nick Ryder",
            "Melanie Subbiah",
            "Jared Kaplan",
        ],
        year=2020,
        journal="arXiv preprint",
        abstract="Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task. While typically task-agnostic in architecture, this method still requires task-specific fine-tuning datasets of thousands or tens of thousands of examples.",
        doi="10.48550/arXiv.2005.14165",
        url="https://arxiv.org/abs/2005.14165",
        pdf_path=None,
        tags=["gpt-3", "language-models", "few-shot", "openai"],
        collections=["language-models", "transformers"],
        keywords=[
            "gpt-3",
            "language model",
            "few-shot learning",
            "transformer",
            "large language model",
        ],
        notes="GPT-3 paper demonstrating few-shot learning capabilities",
        date_added=datetime(2024, 1, 19, 16, 30, 0),
        date_modified=datetime(2024, 1, 19, 16, 30, 0),
        zotero_key="GPT32020",
        zotero_version=1,
    ),
    PaperRecord(
        id="ai-006",
        title="ImageNet Classification with Deep Convolutional Neural Networks",
        authors=["Alex Krizhevsky", "Ilya Sutskever", "Geoffrey E. Hinton"],
        year=2012,
        journal="Advances in Neural Information Processing Systems",
        abstract="We trained a large, deep convolutional neural network to classify the 1.2 million high-resolution images in the ImageNet LSVRC-2010 contest into the 1000 different classes. The neural network achieved a top-1 error rate of 37.5% and a top-5 error rate of 17.0%, considerably better than previous results.",
        doi="10.5555/2999134.2999257",
        url="https://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks",
        pdf_path=None,
        tags=["cnn", "imagenet", "computer-vision", "deep-learning"],
        collections=["computer-vision", "deep-learning"],
        keywords=[
            "alexnet",
            "convolutional neural networks",
            "imagenet",
            "computer vision",
        ],
        notes="AlexNet paper that sparked deep learning revolution in computer vision",
        date_added=datetime(2024, 1, 20, 13, 20, 0),
        date_modified=datetime(2024, 1, 20, 13, 20, 0),
        zotero_key="ALEXNET2012",
        zotero_version=1,
    ),
    PaperRecord(
        id="ai-007",
        title="Improving Language Understanding by Generative Pre-Training",
        authors=[
            "Alec Radford",
            "Karthik Narasimhan",
            "Tim Salimans",
            "Ilya Sutskever",
        ],
        year=2018,
        journal="OpenAI Blog",
        abstract="We introduce a new approach to language understanding that involves generative pre-training of a language model on a diverse corpus of unlabeled text, followed by discriminative fine-tuning on each specific task. Our method significantly outperforms previous approaches on a wide range of NLP tasks while requiring minimal task-specific modifications.",
        doi="10.48550/arXiv.1810.04805",
        url="https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf",
        pdf_path=str(SAMPLE_DIR / "gpt-1.pdf"),
        tags=["gpt", "pre-training", "language-models", "openai"],
        collections=["language-models", "transformers", "pre-training"],
        keywords=[
            "gpt",
            "generative pre-training",
            "language model",
            "unsupervised learning",
        ],
        notes="Original GPT paper introducing generative pre-training approach",
        date_added=datetime(2024, 1, 21, 10, 0, 0),
        date_modified=datetime(2024, 1, 21, 10, 0, 0),
        zotero_key="GPT2018",
        zotero_version=1,
    ),
]


def get_sample_records() -> list[PaperRecord]:
    """Get complete paper records for development and testing"""
    return SAMPLE_RECORDS


def get_sample_papers() -> list[PaperResponse]:
    """Get simplified paper responses for frontend display"""
    return [
        PaperResponse(
            id=record.id,
            title=record.title,
            authors=record.authors,
            year=record.year,
            journal=record.journal,
            abstract=record.abstract,
        )
        for record in SAMPLE_RECORDS
    ]


def get_paper_by_id(paper_id: str) -> PaperRecord | None:
    """Get complete paper record by ID"""
    return next((paper for paper in SAMPLE_RECORDS if paper.id == paper_id), None)


def get_paper_response_by_id(paper_id: str) -> PaperResponse | None:
    """Get simplified paper response by ID"""
    paper = get_paper_by_id(paper_id)
    if paper:
        return PaperResponse(
            id=paper.id,
            title=paper.title,
            authors=paper.authors,
            year=paper.year,
            journal=paper.journal,
            abstract=paper.abstract,
        )
    return None


def search_papers(query: str) -> list[PaperResponse]:
    """Search papers by title, authors, or abstract"""
    query_lower = query.lower()
    return [
        PaperResponse(
            id=record.id,
            title=record.title,
            authors=record.authors,
            year=record.year,
            journal=record.journal,
            abstract=record.abstract,
        )
        for record in SAMPLE_RECORDS
        if query_lower in record.title.lower()
        or any(query_lower in author.lower() for author in record.authors)
        or query_lower in record.abstract.lower()
        or any(query_lower in tag.lower() for tag in record.tags)
        or any(query_lower in keyword.lower() for keyword in record.keywords)
    ]
