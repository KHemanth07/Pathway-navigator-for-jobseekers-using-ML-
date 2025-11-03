import pandas as pd
import math
import os

DATA_FOLDER = 'data/'

def load_job_skills_from_csv(file_path):
    df = pd.read_csv(file_path)
    df["Job Role"] = df["Job Role"].apply(lambda x: str(x).strip())
    return df.groupby("Job Role")["Skills"].apply(lambda x: ', '.join(x)).to_dict()

def recommend_learning_path(job_role, current_year, file_name="job_roles_skills_detailed.csv", total_years=4):
    file_path = os.path.join(DATA_FOLDER, file_name)
    job_skills = load_job_skills_from_csv(file_path)

    job_role_cleaned = job_role.strip().lower()

    # 🔍 Debug print to help trace what's going on
    print("Normalized input:", job_role_cleaned)
    print("CSV Job Roles:", [k.strip().lower() for k in job_skills.keys()])

    # Perform normalized matching
    matched_role = next((key for key in job_skills if key.strip().lower() == job_role_cleaned), None)

    if not matched_role:
        return f"Job role '{job_role}' not found."

    skills = [skill.strip() for skill in job_skills[matched_role].split(',')]
    years_left = total_years - current_year + 1

    if years_left <= 0:
        return "You have completed your academic years."

    skills_per_year = math.ceil(len(skills) / years_left)
    learning_path = {}

    for i in range(years_left):
        year = current_year + i
        start_index = i * skills_per_year
        end_index = min(start_index + skills_per_year, len(skills))
        learning_path[f"Year {year}"] = skills[start_index:end_index]

    return learning_path
