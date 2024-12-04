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
st.title("Document Comparison and Analysis")

# Sidebar Navigation
if "expanded_section" not in st.session_state:
    st.session_state.expanded_section = "About the Tool"  # Default expanded section

def set_section(section):
    """Update session state to expand the selected section and collapse others."""
    st.session_state.expanded_section = section

st.sidebar.title("Navigation")

# Rectangular sections in the sidebar
sections = ["About the Tool", "Disclaimer", "Creator Info"]

for section in sections:
    if st.sidebar.button(section, use_container_width=True):
        set_section(section)

# Show content of the selected section
st.sidebar.markdown("---")
if st.session_state.expanded_section == "About the Tool":
    st.sidebar.subheader("About the Tool")
    st.sidebar.markdown("""
    **Document Comparison and Analysis Tool**  
    This tool allows users to:
    - Compare two documents and summarize key differences.
    - Answer questions based on document content.
    - Generate a concise summary with highlighted differences.

    **How to use**:
    - Upload the reference and comparison files in .docx format.
    - Use the provided buttons to analyze and interact with the documents.
    """)
elif st.session_state.expanded_section == "Disclaimer":
    st.sidebar.subheader("Disclaimer")
    st.sidebar.markdown("""
    **Data Privacy and Accuracy Notice**  
    - This tool uses open-source LLMs to process the uploaded documents. 
    - Document data may be transmitted to external servers for processing.  
    - Please avoid uploading sensitive or confidential data.  
    - The tool's outputs are based on LLM-generated analysis and may not always be fully accurate.  
    """)
elif st.session_state.expanded_section == "Creator Info":
    st.sidebar.subheader("Creator Info")
    st.sidebar.markdown("""
    **Tool Created By**:  
    [Sriram Kolathu](https://www.linkedin.com/in/sriram-kolathu-cpsm-61b03211/)  
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

        Provide a recommended negotiation strategy or plan (max 5 bullet points) to address these changes with the supplier in a separate section. 
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
        Provide a detailed answer based on Comparison file in comparison to Reference file, prioritizing the Comparison file.
        you do not make up your own answers, limit the content to the documents.
        Reference file is the company agreed standard.
        in case of pyament term related query, provide cost of finance or fincial impact based on wapt calculation and explain the financial imapct in real numbers. in the absence of contract value use USD 1000000 as base value for comparison use interest rate in USA or Canada for calculation.
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
        Focus on the impact of these differences and provide recomended action plan or negotiation strategy. Limit the summary to 200 words.

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
