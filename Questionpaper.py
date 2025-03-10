import re
import json
import random
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class QuestionPaperPipeline:
    def __init__(self, pdf_files):
        """Initialize with a list of PDF file paths."""
        self.pdf_files = pdf_files  # List of PDF files containing questions
        self.text = ""  # Stores extracted text from PDFs
        self.questions = []  # Stores extracted questions
        self.clustered_questions = {}  # Dictionary to store clustered questions

    def extract_text_from_pdfs(self):
        """Extract text from all provided PDF files."""
        log.info("Extracting text from PDFs...")
        for pdf in self.pdf_files:
            reader = PdfReader(pdf)  # Load the PDF file
            for page in reader.pages:
                self.text += page.extract_text()  # Append text from each page

        # Remove unwanted text and unnecessary newlines
        self.text = self.text.replace("\n", " ")
        self.text = self.text.replace(
            "BANGALORE INSTITUTE OF TECHNOLOGY K R ROAD, V V PURA, BENGALURU-04 DE", ""
        )
        self.text = self.text.replace("OR", "")  # Remove 'OR' occurrences (optional)

        return self  # Return the object to allow method chaining

    def extract_questions(self):
        """Extract questions using regex pattern."""
        log.info("Extracting questions...")

        # Regular expression to capture questions (assumes questions start with a number and a letter)
        pattern = r"\d+\.\w+\)\s*(.*?)\s*(?=\d+\.\w+\)|PART|$)"
        self.questions = re.findall(pattern, self.text, re.DOTALL)

        # Remove unnecessary spaces from questions
        self.questions = [" ".join(q.split()) for q in self.questions]

        # List to store cleaned questions
        cleaned_questions = []

        for q in self.questions:
            # Match the question structure (question text, marks, PO'S, CO'S, Blooms Level)
            match = re.match(
                r"(.+?)\s+(\d+)\s+(\d+)\s+([\d,\s]+?)\s+(\d+)\s*$", q.strip()
            )

            if match:
                question_text = match.group(1).strip()  # Extract the question text
                marks = match.group(2)  # Extract marks
                pos = match.group(3)  # Extract PO'S
                cos = re.sub(r"\s+", "", match.group(4))  # Remove spaces from CO'S
                blooms_level = match.group(5)  # Extract Blooms Level

                # Append cleaned question
                cleaned_questions.append(
                    f"{question_text} {marks} {pos} {cos} {blooms_level}"
                )
            else:
                cleaned_questions.append(q)  # Keep original if no match found

        self.questions = cleaned_questions  # Update self.questions with cleaned data

        # Re-clean questions for extra safety
        cleaned_questions = []
        for q in self.questions:
            match = re.match(r"(.+?)\s+(\d+)\s+(\d+)\s+([\d,]+)\s+(\d+)", q)

            if match:
                question_text = match.group(1).strip()
                marks = match.group(2)
                pos = match.group(3)
                cos = match.group(4)
                blooms_level = match.group(5)

                cleaned_questions.append(
                    f"{question_text} {marks} {pos} {cos} {blooms_level}"
                )
            else:
                cleaned_questions.append(q)  # Keep original if no match found

        self.questions = cleaned_questions  # Final cleaned list of questions
        log.info(f"Extracted Questions: ")  # Print extracted questions for debugging
        return self  # Return the object to allow method chaining

    def cluster_questions(self, num_clusters=12):
        """Clusters questions using TF-IDF and KMeans."""
        log.info(f"Clustering questions into {num_clusters} clusters...")

        # Convert questions into numerical representation using TF-IDF
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(self.questions)

        # Perform KMeans clustering on questions
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        kmeans.fit(X)
        labels = kmeans.labels_  # Get cluster labels for each question

        # Initialize cluster dictionary
        self.clustered_questions = {i: [] for i in range(num_clusters)}
        for i, label in enumerate(labels):
            self.clustered_questions[label].append(
                self.questions[i]
            )  # Assign questions to respective clusters

        return self  # Return the object to allow method chaining

    def select_final_questions(self):
        """Selects one question from each cluster for the final paper."""
        log.info("Selecting final questions...")
        final_paper = []

        for cluster in self.clustered_questions:
            if self.clustered_questions[cluster]:  # Ensure non-empty clusters
                final_paper.append(
                    random.choices(self.clustered_questions[cluster], k=1)
                )  # Select a random question

        return final_paper  # Return the selected questions

    def parse_question(self, question):
        """Parses question text into a structured format."""
        parts = question.split()
        try:
            # Extract components of the question
            question_text = " ".join(parts[:-4])  # Extract question text
            marks = int(parts[-4])  # Extract marks
            difficulty = int(parts[-3])  # Extract PO'S (difficulty level)
            topics = list(map(int, parts[-2].split(",")))  # Extract CO'S
            learning_outcome = int(parts[-1])  # Extract Blooms Level

            return {
                "Question": question_text,
                "Marks": marks,
                "PO'S": difficulty,
                "CO'S": topics,
                "Blooms Level": learning_outcome,
            }
        except ValueError:
            print(f"Error parsing question: {question}")
            return {
                "Error": "Invalid question format"
            }  # Handle incorrect format errors

    def generate_json(self, final_paper):
        """Converts final questions into a structured JSON output."""
        log.info("Generating JSON output...")
        data = {}
        count = 1

        for question_set in final_paper:
            for question in question_set:
                data[f"Question{count}"] = self.parse_question(
                    question
                )  # Store parsed question in dictionary
                count += 1

        return json.dumps(data, indent=4)  # Convert dictionary to JSON format

    def run_pipeline(self):
        """Runs the entire pipeline and returns JSON output."""
        self.extract_text_from_pdfs().extract_questions().cluster_questions()

        final_paper = self.select_final_questions()  # Select final questions
        return self.generate_json(final_paper)  # Convert final questions to JSON
