from flask import Flask, request, jsonify, send_from_directory
from backend.code1 import load_and_train_model as load_and_train_it_model, suggest_resources as suggest_it_resources
from backend.code2 import recommend_learning_path as recommend_it_learning_path
from backend.code3 import load_and_train_nonit_model, recommend_path as recommend_nonit_path
from backend.code4 import fetch_recruitment_process, configure_gemini
import os

# Initialize Flask app and set the static folder to serve index.html
app = Flask(__name__, static_folder='frontend', static_url_path='')

# Configure Gemini API
configure_gemini()
if not os.getenv("GOOGLE_API_KEY"):
    print("Warning: GOOGLE_API_KEY environment variable not set for Gemini.")

# Load and train IT model
try:
    it_vectorizer, it_kmeans, it_text_data, it_clusters, it_text_vectors, it_dataset_labels = load_and_train_it_model()
    it_model_loaded = True
    print("✅ IT K-Means model loaded successfully.")
except Exception as e:
    it_vectorizer = it_kmeans = it_text_data = it_clusters = it_text_vectors = it_dataset_labels = None
    it_model_loaded = False
    print(f"❌ Error loading IT model: {e}")

# Load and train Non-IT model
try:
    nonit_df, nonit_vectorizer, nonit_kmeans, nonit_le = load_and_train_nonit_model()
    nonit_model_loaded = True
    print("✅ Non-IT K-Means model loaded successfully.")
except Exception as e:
    nonit_df = nonit_vectorizer = nonit_kmeans = nonit_le = None
    nonit_model_loaded = False
    print(f"❌ Error loading Non-IT model: {e}")

# Serve the frontend index.html
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# IT recommendations
@app.route('/recommend_it', methods=['POST'])
def recommend_it():
    if not it_model_loaded:
        return jsonify({"error": "IT Model not loaded."}), 503
    data = request.get_json()
    if not data or 'job_role' not in data or 'skill' not in data:
        return jsonify({"error": "Missing job_role or skill."}), 400
    recommendations = suggest_it_resources(
        data['job_role'], data['skill'],
        it_vectorizer, it_kmeans,
        it_text_data, it_clusters, it_text_vectors, it_dataset_labels
    )
    return jsonify(recommendations), 200

# IT learning path
@app.route('/learning_path', methods=['POST'])
def get_learning_path():
    data = request.get_json()
    if not data or 'job_role' not in data or 'current_year' not in data:
        return jsonify({"error": "Missing job_role or current_year."}), 400
    try:
        current_year = int(data['current_year'])
    except ValueError:
        return jsonify({"error": "current_year must be an integer."}), 400
    learning_path = recommend_it_learning_path(data['job_role'], current_year)
    return jsonify(learning_path), 200

# Non-IT pathway
@app.route('/recommend_nonit', methods=['POST'])
def recommend_nonit():
    if not nonit_model_loaded:
        return jsonify({"error": "Non-IT Model not loaded."}), 503
    data = request.get_json()
    if not data or 'branch' not in data or 'job_role' not in data or 'skill' not in data or 'year' not in data:
        return jsonify({"error": "Missing branch, job_role, skill, or year."}), 400
    try:
        year = int(data['year'])
    except ValueError:
        return jsonify({"error": "year must be an integer."}), 400

    upcoming_skills_inclusive, certifications, internships, projects = recommend_nonit_path(
        nonit_df, data['branch'], data['job_role'], data['skill'], year,
        nonit_vectorizer, nonit_kmeans, nonit_le
    )
    return jsonify({
        "skill_division": upcoming_skills_inclusive,
        "certifications": certifications,
        "internships": internships,
        "projects": projects
    }), 200

# Recruitment process from Gemini
@app.route('/get_recruitment', methods=['POST'])
def get_recruitment():
    data = request.get_json()
    if not data or 'company_name' not in data or 'job_role' not in data:
        return jsonify({"error": "Missing company_name or job_role."}), 400
    try:
        recruitment_process = fetch_recruitment_process(data['company_name'], data['job_role'])
        return jsonify({"recruitment_process": recruitment_process}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"Failed to fetch recruitment process: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
