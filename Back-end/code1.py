# backend/code1.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import os

DATA_FOLDER = 'data/' # Define a constant for the data folder

def load_data():
    """Load all datasets and clean column names."""
    certifications = pd.read_csv(os.path.join(DATA_FOLDER, "Dataset_certifications.csv")).rename(columns=lambda x: x.strip())
    internships = pd.read_csv(os.path.join(DATA_FOLDER, "Dataset_internship.csv")).rename(columns=lambda x: x.strip())
    projects = pd.read_csv(os.path.join(DATA_FOLDER, "Dataset_projects.csv")).rename(columns=lambda x: x.strip())
    return certifications, internships, projects

def prepare_data_for_clustering(certifications, internships, projects):
    """Convert categorical data into text format for clustering."""
    combined_data = []
    dataset_labels = []

    # Convert dataset rows into textual format
    for _, row in certifications.iterrows():
        combined_data.append(f"{row['Job_Role']} {row['Skill']} {row['Certification']}")
        dataset_labels.append("Certifications")

    for _, row in internships.iterrows():
        combined_data.append(f"{row['Job_Role']} {row['Skill']} {row['Internship']}")
        dataset_labels.append("Internships")

    for _, row in projects.iterrows():
        combined_data.append(f"{row['Job_Role']} {row['Skill']} {row['Project']}")
        dataset_labels.append("Projects")

    return combined_data, dataset_labels

def train_kmeans_model(text_data, num_clusters=5):
    """Train a K-Means model on the processed text data."""
    vectorizer = TfidfVectorizer(stop_words='english')
    text_vectors = vectorizer.fit_transform(text_data)

    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(text_vectors)

    return vectorizer, kmeans, clusters, text_vectors

def suggest_resources(job_role, skill, vectorizer, kmeans, text_data, clusters, text_vectors, dataset_labels):
    """Suggests certifications, internships, and projects based on job role and skill."""
    input_text = f"{job_role} {skill}"
    input_vector = vectorizer.transform([input_text])
    cluster_label = kmeans.predict(input_vector)[0]

    relevant_indices = [i for i in range(len(text_data)) if clusters[i] == cluster_label]

    if not relevant_indices:
        return {"Certifications": [], "Internships": [], "Projects": []}

    relevant_vectors = text_vectors[relevant_indices]
    similarities = cosine_similarity(input_vector, relevant_vectors).flatten()
    top_indices = [relevant_indices[i] for i in similarities.argsort()[-5:][::-1]]

    recommendations = {"Certifications": [], "Internships": [], "Projects": []}

    for idx in top_indices:
        category = dataset_labels[idx]
        recommendations[category].append(text_data[idx])

    return recommendations

def load_and_train_model():
    """Loads data and trains the K-Means model. Returns the trained components."""
    certifications, internships, projects = load_data()
    text_data, dataset_labels = prepare_data_for_clustering(certifications, internships, projects)
    vectorizer, kmeans, clusters, text_vectors = train_kmeans_model(text_data)
    return vectorizer, kmeans, text_data, clusters, text_vectors, dataset_labels