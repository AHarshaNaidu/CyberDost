import streamlit as st
import pandas as pd
from groq import Groq

# Setup API key for Groqcloud
api_key = st.secrets["api_key"]
client = Groq(api_key=api_key)

# Define the optimized and detailed prompt templates for cybersecurity audits
preprocess_prompt_template = """
You are an AI assistant specialized in cybersecurity audits.
Analyze the given cybersecurity audit report and provide a detailed summary.
Identify key findings, vulnerabilities, recommendations, and areas of concern.
Ensure the summary includes a clear explanation of each identified item and its importance for security.

### Example Format:
- **Key Findings**:
  - [Description of key findings]
- **Vulnerabilities**:
  - [Description of vulnerabilities]
- **Recommendations**:
  - [Description of recommendations]
- **Other Security Concerns**:
  - [Description of other concerns]
"""

decision_support_prompt_template = """
You are an AI assistant specialized in cybersecurity audit analysis.
Use the provided cybersecurity audit report summary to assist with decision-making.
Answer the following decision-related questions based on the audit findings and provide actionable insights.

### Example Questions:
1. What are the most critical vulnerabilities?
2. What actions should be prioritized for remediation?
3. Are there any compliance issues highlighted in the audit?
4. What are the risks if no action is taken?
"""

# Function to call the Groq API
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

# Streamlit interface
st.set_page_config(page_title="Cybersecurity Audit Analyzer 🛡️", page_icon="🛡️")
st.title("Cybersecurity Audit Analyzer 🛡️")

# Initialize session state variables
if 'audit_summary' not in st.session_state:
    st.session_state['audit_summary'] = None
if 'decision_support' not in st.session_state:
    st.session_state['decision_support'] = None

# Step 1: Upload and Analyze Cybersecurity Audit
def analyze_audit():
    st.header('Step 1: Upload and Analyze Cybersecurity Audit Report')

    uploaded_file = st.file_uploader("Upload your audit report (PDF, DOCX, etc.)", type=["pdf", "docx", "txt"])

    if uploaded_file:
        st.write("Uploaded file:", uploaded_file.name)

        if st.button('Analyze Report'):
            with st.spinner("Analyzing..."):
                # For simplicity, we'll use dummy content for the uploaded file
                file_content = "Sample cybersecurity audit content"  # Replace this with actual file reading logic

                analysis_prompt = f"Analyze this cybersecurity audit:\n{file_content}"
                audit_summary = call_llm_api(preprocess_prompt_template, analysis_prompt)

                st.session_state['audit_summary'] = audit_summary

            st.write("### Audit Summary:")
            st.write(st.session_state['audit_summary'])

            return st.session_state['audit_summary']

# Step 2: Provide Decision Support
def decision_support():
    st.header('Step 2: Decision Support')

    if st.session_state['audit_summary']:
        st.write("### Audit Summary from Step 1:")
        st.write(st.session_state['audit_summary'])

    if st.button('Provide Decision Support'):
        with st.spinner("Generating decision support..."):
            decision_prompt = f"Provide decision support for this audit summary:\n{st.session_state['audit_summary']}"
            st.session_state['decision_support'] = call_llm_api(decision_support_prompt_template, decision_prompt)

        st.write("### Decision Support Insights:")
        st.write(st.session_state['decision_support'])

        return st.session_state['decision_support']

# Main function to integrate steps
def main():
    st.sidebar.title("Cybersecurity Audit Analyzer")
    step = st.sidebar.radio("Select Step", ["Step 1: Analyze Audit Report", "Step 2: Decision Support"])

    if step == "Step 1: Analyze Audit Report":
        audit_summary = analyze_audit()
    elif step == "Step 2: Decision Support":
        if st.session_state['audit_summary'] is None:
            st.warning("Please complete Step 1: Analyze Audit Report first.")
        else:
            decision_support()

if __name__ == '__main__':
    main()
