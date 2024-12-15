import os
from nltk.tokenize import sent_tokenize
from nltk.data import find
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import fitz  # PyMuPDF for PDF processing
import docx
import streamlit as st



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
    matches = []
    
    for i, ref_vec in enumerate(ref_vectors):
        similarity_scores = cosine_similarity(ref_vec, comp_vectors)
        max_score = similarity_scores.max()
        if max_score < 0.7:  # Threshold for similarity
            missing_clauses.append(ref_clauses[i])
        else:
            matches.append((ref_clauses[i], max_score))
    
    for i, comp_vec in enumerate(comp_vectors):
        similarity_scores = cosine_similarity(comp_vec, ref_vectors)
        max_score = similarity_scores.max()
        if max_score < 0.7:
            new_clauses.append(comp_clauses[i])
    
    return missing_clauses, new_clauses, matches

# Streamlit UI
st.title("Dynamic Clause Comparison Tool")

# Upload files
st.header("Upload Documents")
ref_file = st.file_uploader("Upload Reference file (.docx or .pdf)", type=["docx", "pdf"])
comp_file = st.file_uploader("Upload Comparison file (.docx or .pdf)", type=["docx", "pdf"])

if ref_file and comp_file:
    ref_text = extract_text_from_pdf(ref_file) if ref_file.type == "application/pdf" else extract_text_from_docx(ref_file)
    comp_text = extract_text_from_pdf(comp_file) if comp_file.type == "application/pdf" else extract_text_from_docx(comp_file)
    
    st.header("Comparing Clauses...")
    missing_clauses, new_clauses, matches = compare_clauses(ref_text, comp_text)

    st.subheader("Missing Clauses from Comparison File")
    if missing_clauses:
        for clause in missing_clauses:
            st.write(f"- {clause}")
    else:
        st.write("No missing clauses detected.")

    st.subheader("New Clauses in Comparison File")
    if new_clauses:
        for clause in new_clauses:
            st.write(f"- {clause}")
    else:
        st.write("No new clauses detected.")

    st.subheader("Matched Clauses")
    for match, score in matches:
        st.write(f"- {match} (Similarity Score: {score:.2f})")