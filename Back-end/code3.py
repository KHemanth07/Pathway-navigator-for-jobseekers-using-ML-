# backend/code3.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import os

DATA_FOLDER = 'data/'

def preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df.dropna(inplace=True)  # Remove missing values

    vectorizer = TfidfVectorizer()
    df['Skills_Vectorized'] = list(vectorizer.fit_transform(df['Skills']).toarray())

    return df, vectorizer

def train_kmeans(df, n_clusters=5):
    le = LabelEncoder()
    df['JobRole_Encoded'] = le.fit_transform(df['Job Role'])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(list(df['Skills_Vectorized']))

    df['Cluster'] = kmeans.labels_
    return df, kmeans, le

def divide_skills_by_year_inclusive(remaining_skills, user_year):
    num_skills = len(remaining_skills)
    skill_distribution = {
        1: remaining_skills[:max(3, num_skills // 4)],
        2: remaining_skills[max(3, num_skills // 4):max(6, num_skills // 2)],
        3: remaining_skills[max(6, num_skills // 2):max(9, 3 * num_skills // 4)],
        4: remaining_skills[max(9, 3 * num_skills // 4):]
    }

    upcoming_skills_inclusive = {}
    for year in range(user_year, 5):
        upcoming_skills_inclusive[f"Year {year}"] = skill_distribution.get(year, [])

    return upcoming_skills_inclusive

def recommend_path(df, user_branch, user_job_role, user_skill, user_year, vectorizer, kmeans, le):
    user_skill_vector = vectorizer.transform([user_skill]).toarray()
    cluster_label = kmeans.predict(user_skill_vector)[0]

    recommended_jobs = df[(df['Cluster'] == cluster_label) & (df['Branch'] == user_branch)]
    if recommended_jobs.empty:
        return {}, "No recommendations", "No recommendations", "No recommendations"

    user_skills = set([s.strip() for s in user_skill.split(',')])
    all_skills = set([s.strip() for s in ', '.join(recommended_jobs['Skills']).split(',')])
    remaining_skills = list(all_skills - user_skills)
    upcoming_skills_inclusive = divide_skills_by_year_inclusive(remaining_skills, user_year)

    certifications = recommended_jobs['Certifications'].iloc[0] if not recommended_jobs.empty and 'Certifications' in recommended_jobs.columns else "No recommendations"
    internships = recommended_jobs['Internships'].iloc[0] if not recommended_jobs.empty and 'Internships' in recommended_jobs.columns else "No recommendations"
    projects = recommended_jobs['Projects'].iloc[0] if not recommended_jobs.empty and 'Projects' in recommended_jobs.columns else "No recommendations"

    # Return the inclusive upcoming skills
    return upcoming_skills_inclusive, certifications, internships, projects

def load_and_train_nonit_model():
    """Loads Non-IT data and trains the K-Means model. Returns the trained components."""
    df, vectorizer = preprocess_data(os.path.join(DATA_FOLDER, "Dataset_NonIT.csv"))
    df_trained, kmeans, le = train_kmeans(df)
    return df_trained, vectorizer, kmeans, le