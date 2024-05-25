from flask import Flask, request, render_template, send_file
import json
import spacy
from fpdf import FPDF

app = Flask(__name__)

# Load base resume
with open('base_resume.json') as f:
    base_resume = json.load(f)

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def tailor_resume(base_resume, job_requirements):
    tailored_resume = base_resume.copy()
    
    # Extract skills from job requirements using NLP
    doc = nlp(job_requirements)
    required_skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]
    
    # Match skills
    tailored_resume['skills'] = ", ".join([skill for skill in base_resume['skills'] if skill in required_skills])
    
    return tailored_resume

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Resume', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

def generate_pdf(tailored_resume, output_file):
    pdf = PDF()
    pdf.add_page()

    pdf.chapter_title(tailored_resume['name'])
    pdf.chapter_body(tailored_resume['contact'])
    
    pdf.chapter_title('Education')
    pdf.chapter_body(tailored_resume['education'])
    
    pdf.chapter_title('Experience')
    for experience in tailored_resume['experience']:
        pdf.chapter_title(experience['title'] + " at " + experience['company'])
        pdf.chapter_body(experience['description'])

    pdf.chapter_title('Skills')
    pdf.chapter_body(tailored_resume['skills'])
    
    pdf.chapter_title('Awards')
    pdf.chapter_body(", ".join(tailored_resume['awards']))

    pdf.output(output_file)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_requirements = request.form['job_requirements']
        tailored_resume = tailor_resume(base_resume, job_requirements)
        output_file = 'tailored_resume.pdf'
        generate_pdf(tailored_resume, output_file)
        return send_file(output_file, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
