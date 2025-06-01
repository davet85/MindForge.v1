import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from utils.constants import MEMORY_STORE_PATH
from utils.logger import log_info, log_error

def cluster_thoughts(memory: list, n_clusters: int = 4) -> dict:
    """
    Cluster user thoughts into symbolic groups using TF-IDF + KMeans.
    Returns a dict: cluster index -> list of thoughts.
    """
    try:
        if not memory or not isinstance(memory, list):
            return {}

        thoughts = [entry.get("thought", "") for entry in memory if entry.get("thought")]
        if len(thoughts) < n_clusters:
            n_clusters = max(2, len(thoughts))  # prevent crash

        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(thoughts)

        kmeans = KMeans(n_clusters=n_clusters, n_init="auto", random_state=42)
        labels = kmeans.fit_predict(tfidf_matrix)

        clustered = {}
        for idx, label in enumerate(labels):
            clustered.setdefault(label, []).append(thoughts[idx])

        log_info(f"Clustered {len(thoughts)} thoughts into {n_clusters} groups.")
        return clustered

    except Exception as e:
        log_error(f"Error during thought clustering: {e}")
        return {}

def generate_cluster_label(thoughts: list, openai_client=None, model="gpt-4") -> str:
    """
    Generate a symbolic label for a cluster of thoughts using GPT.
    Requires an OpenAI client instance (OpenAI()) to be passed.
    """
    if not thoughts or not openai_client:
        return "Unnamed Cluster"

    prompt = (
        "The following reflections belong to the same cognitive/emotional theme:\n\n"
        + "\n".join(f"- {t}" for t in thoughts[:8]) +  # Limit to 8 thoughts for token control
        "\n\nReturn a short symbolic label (1–3 words) that captures the theme."
    )

    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a symbolic compression engine."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=20
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        log_error(f"Failed to generate cluster label: {e}")
        return "Unlabeled Cluster"
