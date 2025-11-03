# backend/code4.py
import google.generativeai as genai
import os

# Configure the Gemini API key from environment variable in Flask app
def configure_gemini():
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def fetch_recruitment_process(company_name, job_role):
    """Fetch recruitment process dynamically using Gemini."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"What is the recruitment process for fresher {job_role} at {company_name}. Give the brief info about the steps of round after application?. Give the info in 8 - 10. Give the minimum eligibile criteria of Percentage"
    response = model.generate_content(prompt)
    return response.text