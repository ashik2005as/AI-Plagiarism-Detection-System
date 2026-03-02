"""Core plagiarism detection engine using TF-IDF and cosine similarity."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocessing import preprocess_text, tokenize_sentences


def classify_plagiarism_level(similarity_pct):
    """
    Classify plagiarism severity based on similarity percentage.

    Args:
        similarity_pct (float): Similarity percentage (0–100).

    Returns:
        str: One of "Low", "Medium", or "High".
    """
    if similarity_pct < 30:
        return "Low"
    if similarity_pct < 70:
        return "Medium"
    return "High"


def calculate_similarity(text1, text2):
    """
    Calculate the overall cosine similarity between two documents.

    Both texts are preprocessed before vectorisation.

    Args:
        text1 (str): First document text.
        text2 (str): Second document text.

    Returns:
        float: Similarity score in the range [0.0, 1.0].
    """
    processed1 = preprocess_text(text1)
    processed2 = preprocess_text(text2)

    if not processed1 or not processed2:
        return 0.0

    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([processed1, processed2])
    except ValueError:
        return 0.0

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return float(similarity[0][0])


def get_sentence_matches(text1, text2, top_n=10):
    """
    Find the most similar sentence pairs between two documents.

    Each sentence from *text1* is compared against every sentence in
    *text2* using TF-IDF cosine similarity. The top-*top_n* pairs by
    similarity score are returned.

    Args:
        text1 (str): First document text.
        text2 (str): Second document text.
        top_n (int): Maximum number of sentence pairs to return.

    Returns:
        list[dict]: List of dicts with keys "sentence1", "sentence2",
            and "similarity" (float, 0–1).
    """
    sentences1 = tokenize_sentences(text1)
    sentences2 = tokenize_sentences(text2)

    if not sentences1 or not sentences2:
        return []

    processed1 = [preprocess_text(s) for s in sentences1]
    processed2 = [preprocess_text(s) for s in sentences2]

    # Keep only sentences that have content after preprocessing
    valid1 = [(s, p) for s, p in zip(sentences1, processed1) if p]
    valid2 = [(s, p) for s, p in zip(sentences2, processed2) if p]

    if not valid1 or not valid2:
        return []

    orig1, proc1 = zip(*valid1)
    orig2, proc2 = zip(*valid2)

    vectorizer = TfidfVectorizer()
    try:
        all_processed = list(proc1) + list(proc2)
        tfidf_matrix = vectorizer.fit_transform(all_processed)
    except ValueError:
        return []

    matrix1 = tfidf_matrix[: len(proc1)]
    matrix2 = tfidf_matrix[len(proc1) :]

    sim_matrix = cosine_similarity(matrix1, matrix2)

    matches = []
    for i, row in enumerate(sim_matrix):
        for j, score in enumerate(row):
            if score > 0:
                matches.append(
                    {
                        "sentence1": orig1[i],
                        "sentence2": orig2[j],
                        "similarity": round(float(score), 4),
                    }
                )

    matches.sort(key=lambda x: x["similarity"], reverse=True)
    return matches[:top_n]


def compare_documents(text1, text2):
    """
    Perform a full plagiarism comparison between two documents.

    Args:
        text1 (str): First document text.
        text2 (str): Second document text.

    Returns:
        dict: Result containing:
            - ``similarity_percentage`` (float): 0–100
            - ``plagiarism_level`` (str): "Low", "Medium", or "High"
            - ``sentence_matches`` (list[dict]): Top sentence pairs
    """
    similarity = calculate_similarity(text1, text2)
    similarity_pct = round(similarity * 100, 2)
    level = classify_plagiarism_level(similarity_pct)
    sentence_matches = get_sentence_matches(text1, text2)

    return {
        "similarity_percentage": similarity_pct,
        "plagiarism_level": level,
        "sentence_matches": sentence_matches,
    }


def compare_multiple_documents(texts):
    """
    Compare multiple documents and produce a pairwise similarity matrix.

    Args:
        texts (list[str]): List of document text strings (at least 2).

    Returns:
        dict: Result containing:
            - ``similarity_matrix`` (list[list[float]]): NxN matrix of
              similarity percentages (rounded to 2 dp).
            - ``document_count`` (int): Number of documents compared.
    """
    n = len(texts)
    if n < 2:
        raise ValueError("At least two documents are required for comparison.")

    processed = [preprocess_text(t) for t in texts]
    valid_indices = [i for i, p in enumerate(processed) if p]

    # Build an n×n zero matrix
    matrix = [[0.0] * n for _ in range(n)]

    if len(valid_indices) >= 2:
        valid_processed = [processed[i] for i in valid_indices]
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform(valid_processed)
            sim = cosine_similarity(tfidf_matrix)
            for row_idx, i in enumerate(valid_indices):
                for col_idx, j in enumerate(valid_indices):
                    matrix[i][j] = round(float(sim[row_idx][col_idx]) * 100, 2)
        except ValueError:
            pass

    # Ensure diagonal is 100
    for i in range(n):
        matrix[i][i] = 100.0

    return {
        "similarity_matrix": matrix,
        "document_count": n,
    }
