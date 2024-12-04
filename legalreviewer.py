# Import required libraries
import os
from dotenv import load_dotenv
import openai
import docx
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Fetch API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key
else:
    st.error("API Key not found. Please configure it in a .env file.")

# Set up Streamlit UI
st.title("Document Comparison and Analysis Tool")

# Sidebar Navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio(
    "Go to",
    options=["Tool Overview", "Disclaimer", "About Creator"],
)

if selection == "Tool Overview":
    st.sidebar.markdown("### Tool Overview")
    st.sidebar.markdown("""
    This tool helps you compare and analyze documents. 
    **How to use:**
    - Upload two `.docx` files (Reference and Comparison files).
    - Click the respective buttons to generate a summary, ask questions, or compare documents.
    """)
elif selection == "Disclaimer":
    st.sidebar.markdown("### Disclaimer")
    st.sidebar.markdown("""
    - This tool uses an open-source LLM for analysis.
    - Data transmitted to the LLM may not be private.
    - Ensure no sensitive information is uploaded.
    - While the tool aims for high accuracy, always validate results.
    """)
elif selection == "About Creator":
    st.sidebar.markdown("### About the Creator")
    st.sidebar.markdown("""
    Created by **Sriram Kolathu**.  
    [Connect on LinkedIn](https://linkedin.com/in/sriramkolathu)
    """)

# Upload files
st.header("Upload Documents for Comparison")
doc1_file = st.file_uploader("Upload Reference file (.docx)", type="docx")
doc2_file = st.file_uploader("Upload file to compare (.docx)", type="docx")

# Function to extract text from a Word document
def extract_text_from_docx(file):
    """Extracts and returns all text from a .docx file."""
    doc = docx.Document(file)
    full_text = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    return "\n".join(full_text)

# Compare Documents Section
if doc1_file and doc2_file:
    doc1_text = extract_text_from_docx(doc1_file)
    doc2_text = extract_text_from_docx(doc2_file)

    st.header("Compare Documents")

    def compare_docs_with_gpt(doc1, doc2):
        prompt = f"""
        Compare the following two documents and summarize the key changes:

        Reference file:
        {doc1}

        Comparison file:
        {doc2}

        Provide a concise summary of the differences in terms of structure, content, and meaning in a bullet point format (max 10 points). 
        Provide potential impacts of each change below the differences. 

        Provide a recommended negotiation strategy or plan to address these changes with the supplier in a separate section. 
        Prioritize the clauses from very important to less important to optimize negotiations.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in legal document comparison."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"An error occurred: {e}"

    if st.button("Generate Comparison Summary"):
        comparison_result = compare_docs_with_gpt(doc1_text, doc2_text)
        st.subheader("Document Comparison Summary")
        st.write(comparison_result)

    st.header("Ask Questions about the Documents")

    def answer_question_with_gpt(question, doc2, doc1):
        prompt = f"""
        You are a helpful assistant that can answer questions about two documents.
        Focus primarily on the Comparison file but consider the Reference file for comparisons.

        Comparison file:
        {doc2}

        Reference file:
        {doc1}

        Question: {question}
        Provide a detailed answer based on the documents, prioritizing the Comparison file.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert assistant in document analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"An error occurred while answering the question: {e}"

    question = st.text_input("Enter a question about the contract (optional):")
    if question and st.button("Get Answer"):
        answer = answer_question_with_gpt(question, doc2_text, doc1_text)
        st.write("Answer:")
        st.write(answer)

    st.header("Generate Summary for Comparison File with Key Differences")

    def generate_summary_doc2():
        prompt = f"""
        Provide a brief summary of the Comparison file and highlight the key differences compared to the Reference file.
        Focus on the impact of these differences. Limit the summary to 500 words.

        Comparison file:
        {doc2_text}

        Reference file:
        {doc1_text}
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert summarizer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"An error occurred while generating the summary: {e}"

    if st.button("Generate Comparison File Summary with Key Differences"):
        summary = generate_summary_doc2()
        st.subheader("Summary of Comparison File with Key Differences")
        st.write(summary)

        st.download_button(
            label="Download Summary",
            data=summary,
            file_name="summary_doc2.txt",
            mime="text/plain"
        )
