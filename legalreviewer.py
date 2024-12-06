# Import required libraries
import os
from dotenv import load_dotenv
import openai
import docx
import streamlit as st
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Fetch API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key
else:
    st.error("API Key not found. Please configure it in a .env file.")

# Configure Streamlit page (hide the GitHub link and other elements)
st.set_page_config(
    page_title="Document Comparison and Analysis Tool",
    page_icon="📄",
    layout="wide",  # Choose 'wide' for a better layout
    initial_sidebar_state="expanded"
)

# Hide Streamlit branding, GitHub link, and hamburger menu
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
    **Sriram Kolathu**  
    Data Science | CPSM  
    [LinkedIn Profile](https://www.linkedin.com/in/sriram-kolathu-cpsm-61b03211/)  
    """)
    #qr_image = Image.open("assets/linkedin_qr.png")
    #resized_qr_image = qr_image.resize((10, 10)) 
    #st.sidebar.image("assests/Linkedin.png",caption="Scan to visit LinkedIn", use_container_width=False)

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

        Provide a concise summary of the key differences in terms of structure, content, and meaning in a bullet point format (max 10 points) limit only to clause which has substantial difference. 
        Provide potential impacts of each change below the differences. 

        Provide a recommended negotiation strategy or plan (max 5 bullet points) to address these changes with the supplier in a separate section. 
        Prioritize the clauses from very important to less important to optimize negotiations.
        
        in case of payment term difference , then provide cost of finance or fincial impact based on wapt calculation and explain the financial imapct in real numbers for a period of one year. in the absence of contract value use USD 1000000 as base value for comparison use interest rate in USA or Canada for calculation. If query is not related to payment term avoid this fiancial impact due to payment term.
        
        use the following template as example to generate your response: 
        Key Differences:
        
        1.	Payment Terms: The original agreement allows the client xx days to pay invoices, while the revised agreement reduces this to xx days.
            o	Financial Impact: Using an interest rate of y% (average rate in the USA), the cost of financing the payment for xx days would be approximately x,xxx.xx  per year for a assumed contract value of USD x,xxx,xxx.
            
        2.	Termination Notice Period: The original agreement requires a xx-day advance written notice for termination, whereas the revised agreement extends this to 60 days.
            o	Impact: The longer notice period in the revised agreement provides more time for both parties to prepare for termination, potentially reducing any abrupt disruptions in services.
        

        3.	Term Duration: The original agreement has an indefinite term until cancelled with a 40-day notice, while the revised agreement specifies a fixed term of x yyyy from the date of contract execution.
            o	Impact: The fixed term in the revised agreement provides more certainty and clarity regarding the duration of the contractual relationship.
        

        4.	Jurisdiction and Venue: The original agreement specifies Kansas as the governing law and jurisdiction, while the revised agreement changes the venue to New Jersey, USA.
            o	Impact: The change in jurisdiction and venue may have legal implications and affect the ease of resolving disputes, especially if the parties are located in different states.
        

        5.	Notice Address: The original agreement provides space for fax numbers for both parties, while the revised agreement omits this detail.
            o	Impact: This change may affect the efficiency of communication between the parties, especially if written communication is preferred or required.

        **Recommended Negotiation Strategy:**

        1.	Prioritize negotiation on Payment Terms due to the significant financial impact of shorter payment timelines.
        2.	Discuss and align on the Termination Notice Period to ensure sufficient time for transitioning services if termination occurs.
        3.	Clarify the implications of the fixed Term Duration and assess if it aligns with the long-term goals of both parties.
        4.	Address concerns regarding Jurisdiction and Venue to ensure a fair and accessible legal framework for both parties.
        5.	Revisit the Notice Address section to determine the preferred mode of communication and update as necessary for effective correspondence.

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
        you do not make up your own answers, limit the content to the documents. Limit the answer to max 100 words, 
        Reference file is the company agreed standard.
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
