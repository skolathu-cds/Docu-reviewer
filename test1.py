import os
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import fitz  # PyMuPDF for PDF processing
import docx
import streamlit as st
from transformers import pipeline

# Function to extract text from PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

# Function to extract text from Word document
def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

# Function to preprocess text
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    sentences = sent_tokenize(text)
    preprocessed = []
    for sentence in sentences:
        words = [word.lower() for word in sentence.split() if word.lower() not in stop_words]
        preprocessed.append(" ".join(words))
    return preprocessed

# Compare clauses using semantic similarity
def compare_clauses(ref_text, comp_text):
    ref_clauses = preprocess_text(ref_text)
    comp_clauses = preprocess_text(comp_text)
    
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(ref_clauses + comp_clauses)
    ref_vectors = vectors[:len(ref_clauses)]
    comp_vectors = vectors[len(ref_clauses):]

    missing_clauses = []
    new_clauses = []
    
    for i, ref_vec in enumerate(ref_vectors):
        similarity_scores = cosine_similarity(ref_vec, comp_vectors)
        max_score = similarity_scores.max()
        if max_score < 0.7:  # Threshold for similarity
            missing_clauses.append(ref_clauses[i])
    
    for i, comp_vec in enumerate(comp_vectors):
        similarity_scores = cosine_similarity(comp_vec, ref_vectors)
        max_score = similarity_scores.max()
        if max_score < 0.7:
            new_clauses.append(comp_clauses[i])
    
    return missing_clauses, new_clauses

# Function to summarize text using an open-source LLM with custom prompt
def summarize_with_llm(ref_text, comp_text):
    # Construct the custom prompt
    prompt = f"""
        Compare the following two documents and summarize the key changes:

        Reference file:
        {ref_text}

        Comparison file:
        {comp_text}

        Provide a concise summary of the key differences in terms of structure, content, and meaning in a bullet point format, limit only to clauses which have a difference. 
        Provide potential impacts of each change below the differences.

        Provide a recommended negotiation strategy or plan (max 5 bullet points) to address these changes with the supplier in a separate section. 
        Prioritize the clauses from very important to less important to optimize negotiations.
        
        In case of payment term differences, provide cost of finance or financial impact based on WAPT calculation and explain the financial impact in real numbers for a period of one year. In the absence of contract value, use USD 1,000,000 as the base value for comparison, and use the interest rate in USA or Canada for calculation. If the query is not related to payment terms, avoid this financial impact due to payment terms.
        
        Use the following template as an example to generate your response for all clauses where there is a difference, and provide one line space between each point for better readability:

        Key Differences:

        1. **Payment Clause Terms:** The original agreement allows the client xx days to pay invoices, while the revised agreement reduces this to xx days.
            o Financial Impact: Using an interest rate of y% (average rate in the USA), the cost of financing the payment for xx days would be approximately x,xxx.xx per year for an assumed contract value of USD x,xxx,xxx.

        **Recommended Negotiation Strategy:**

        1. Prioritize negotiation on Payment Terms due to the significant financial impact of shorter payment timelines.
        2. Discuss and align on the Termination Notice Period to ensure sufficient time for transitioning services if termination occurs.
        3. Clarify the implications of the fixed Term Duration and assess if it aligns with the long-term goals of both parties.
        4. Address concerns regarding Jurisdiction and Venue to ensure a fair and accessible legal framework for both parties.
        5. Revisit the Notice Address section to determine the preferred mode of communication and update as necessary for effective correspondence.
    """
    
    # Use Hugging Face pipeline for summarization (example with BART model)
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(prompt, max_length=1000, min_length=300, do_sample=False)
    
    return summary[0]['summary_text']

# Streamlit UI
st.title("Dynamic Clause Comparison Tool")

# Upload files
st.header("Upload Documents")
ref_file = st.file_uploader("Upload Reference file (.docx or .pdf)", type=["docx", "pdf"])
comp_file = st.file_uploader("Upload Comparison file (.docx or .pdf)", type=["docx", "pdf"])

if ref_file and comp_file:
    # Extract text from the uploaded files
    ref_text = extract_text_from_pdf(ref_file) if ref_file.type == "application/pdf" else extract_text_from_docx(ref_file)
    comp_text = extract_text_from_pdf(comp_file) if comp_file.type == "application/pdf" else extract_text_from_docx(comp_file)
    
    # Perform clause comparison
    st.header("Comparing Clauses...")
    missing_clauses, new_clauses = compare_clauses(ref_text, comp_text)

    # Display results: Missing Clauses
    st.subheader("Missing Clauses from Comparison File")
    if missing_clauses:
        for clause in missing_clauses:
            st.write(f"- {clause}")
            st.write(summarize_with_llm(ref_text, comp_text))  # Summarize using LLM
    else:
        st.write("No missing clauses detected.")

    # Display results: New Clauses
    st.subheader("New Clauses in Comparison File")
    if new_clauses:
        for clause in new_clauses:
            st.write(f"- {clause}")
            st.write(summarize_with_llm(ref_text, comp_text))  # Summarize using LLM
    else:
        st.write("No new clauses detected.")