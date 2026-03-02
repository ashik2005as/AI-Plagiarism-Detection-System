"""Text preprocessing utilities for the AI Plagiarism Detection System."""

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer


def download_nltk_data():
    """Download required NLTK data packages if not already present."""
    packages = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
    ]
    for path, package in packages:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(package, quiet=True)


# Ensure NLTK data is available on import
download_nltk_data()


def preprocess_text(text):
    """
    Preprocess input text for plagiarism comparison.

    Steps:
        1. Convert to lowercase
        2. Remove punctuation and special characters
        3. Tokenize
        4. Remove stopwords
        5. Lemmatize tokens

    Args:
        text (str): Raw input text.

    Returns:
        str: Cleaned and preprocessed text as a single string.
    """
    if not text or not isinstance(text, str):
        return ""

    # Handle encoding issues
    try:
        text = text.encode("utf-8", errors="ignore").decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        text = str(text)

    # Lowercase
    text = text.lower()

    # Remove special characters and digits, keep spaces
    text = re.sub(r"[^a-z\s]", " ", text)

    # Tokenize
    tokens = word_tokenize(text)

    # Remove stopwords and short tokens
    stop_words = set(stopwords.words("english"))
    tokens = [t for t in tokens if t not in stop_words and len(t) > 1]

    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]

    return " ".join(tokens)


def tokenize_sentences(text):
    """
    Split text into individual sentences.

    Args:
        text (str): Raw input text.

    Returns:
        list[str]: List of sentence strings.
    """
    if not text or not isinstance(text, str):
        return []
    sentences = sent_tokenize(text.strip())
    return [s.strip() for s in sentences if s.strip()]


def extract_text_from_file(file_path):
    """
    Extract plain text from .txt, .pdf, or .docx files.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Extracted text content.

    Raises:
        ValueError: If the file format is unsupported.
        IOError: If the file cannot be read.
    """
    file_path = str(file_path)
    ext = file_path.rsplit(".", 1)[-1].lower()

    if ext == "txt":
        return _read_txt(file_path)
    if ext == "pdf":
        return _read_pdf(file_path)
    if ext == "docx":
        return _read_docx(file_path)
    raise ValueError(f"Unsupported file format: .{ext}")


def _read_txt(file_path):
    """Read a plain text file with encoding fallback."""
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(file_path, "r", encoding=encoding) as fh:
                return fh.read()
        except UnicodeDecodeError:
            continue
    raise IOError(f"Could not decode file: {file_path}")


def _read_pdf(file_path):
    """Extract text from a PDF file using PyPDF2."""
    try:
        import PyPDF2  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError("PyPDF2 is required to read PDF files.") from exc

    text_parts = []
    with open(file_path, "rb") as fh:
        reader = PyPDF2.PdfReader(fh)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _read_docx(file_path):
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError("python-docx is required to read DOCX files.") from exc

    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)
