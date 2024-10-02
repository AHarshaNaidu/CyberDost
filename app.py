import streamlit as st
import pandas as pd
from groq import Groq
import spacy  # NLP library for processing audit reports

# Setup API key for Groqcloud
api_key = st.secrets["api_key"]
client = Groq(api_key=api_key)

# Load NLP model for unstructured data analysis
nlp = spacy.load("en_core_web_sm")  # You can replace this with a custom model for better domain performance

# Template for processing cybersecurity audit reports
preprocess_prompt_template = """
A user uploads an unstructured cybersecurity audit report.
You are an AI assistant specializing in cybersecurity analysis.
Analyze the report, summarize the findings, and provide actionable insights regarding vulnerabilities, risks, and recommendations.

### Example Summary Format:
- **Key Findings**:
  - [Description of key findings]
- **Identified Vulnerabilities**:
  - [Description of vulnerabilities]
- **Risk Assessment**:
  - [Risk description]
- **Recommended Actions**:
  - [Recommendations to mitigate risks]
"""

qa_prompt_template = """
A user asks a decision-making question related to the cybersecurity audit report.
You are an AI assistant providing insights based on the processed report.
Use the insights to answer the question with actionable recommendations.

### Example:
- **Question:** [User's question]
- **Answer:** [Response based on audit report]
"""

def call_llm_api(prompt_template, user_content):
    data = {
        "model": "llama3-groq-70b-8192-tool-use-preview",
        "messages": [
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": user_content}
        ]
    }
    response = client.chat.completions.create(**data)
    return response.choices[0].message.content

# Streamlit interface for the cybersecurity audit analysis
st.set_page_config(page_title="Cybersecurity Audit Analysis Assistant", page_icon="🔍")
st.title("Cybersecurity Audit Analysis Assistant 🔍")

# Initialize session state variables
if 'audit_summary' not in st.session_state:
    st.session_state['audit_summary'] = None
if 'qa_response' not in st.session_state:
    st.session_state['qa_response'] = None

# Step 1: Upload and Process Cybersecurity Audit Report
def upload_and_process_report():
    st.header('Step 1: Upload and Analyze Cybersecurity Audit Report')

    uploaded_file = st.file_uploader("Upload your unstructured cybersecurity audit report", type=["txt", "pdf"])

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        st.write("Audit Report Content:", content)

        if st.button('Analyze Report'):
            with st.spinner("Analyzing..."):
                doc = nlp(content)
                audit_summary = call_llm_api(preprocess_prompt_template, content)
                st.session_state['audit_summary'] = audit_summary

            st.write("### Audit Report Summary:")
            st.write(st.session_state['audit_summary'])

            return st.session_state['audit_summary']

# Step 2: Question and Answer Interaction
def qa_interaction():
    st.header('Step 2: Chat-based Q&A on Audit Report')

    if st.session_state['audit_summary']:
        st.write("### Processed Audit Report Summary from Step 1:")
        st.write(st.session_state['audit_summary'])

    question = st.text_input("Ask a question related to the audit report:")
    if st.button('Get Answer'):
        with st.spinner("Processing..."):
            qa_prompt = f"Audit Summary:\n{st.session_state['audit_summary']}\n\nQuestion:\n{question}"
            st.session_state['qa_response'] = call_llm_api(qa_prompt_template, qa_prompt)

        st.write("### Answer:")
        st.write(st.session_state['qa_response'])

        return st.session_state['qa_response']

# Main function to integrate all steps
def main():
    st.sidebar.title("Cybersecurity Audit Assistant")
    step = st.sidebar.radio("Select Step", ["Step 1: Upload and Analyze Report", "Step 2: Chat-based Q&A"])

    if step == "Step 1: Upload and Analyze Report":
        audit_summary = upload_and_process_report()
    elif step == "Step 2: Chat-based Q&A":
        if st.session_state['audit_summary'] is None:
            st.warning("Please complete Step 1: Upload and Analyze Report first.")
        else:
            qa_interaction()

if __name__ == '__main__':
    main()
