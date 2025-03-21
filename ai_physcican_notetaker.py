# -*- coding: utf-8 -*-
"""AI physcican notetaker

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1E70VwWQr6f_gPVK3TBpwL-8yviXC2DrV
"""

# Upgrade pip first
!pip install --upgrade pip

# Install essential libraries
!pip install transformers datasets nltk spacy scispacy torch

# Install specific versions to avoid conflicts
!pip install spacy==3.7.2
!pip install scispacy==0.5.5
!pip install pydantic==2.7.4

# Install SciSpaCy Medical Models
!pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_ner_bc5cdr_md-0.5.1.tar.gz  # Better for diseases & symptoms

# Extra libraries for text summarization
!pip install bert-extractive-summarizer sentencepiece

# Check installations
!python -c "import spacy; print('SpaCy Version:', spacy.__version__)"
!python -c "import scispacy; print('SciSpaCy Version:', scispacy.__version__)"
!python -c "import pydantic; print('Pydantic Version:', pydantic.__version__)"


import spacy
import re
from transformers import pipeline

# Load medical NER model
nlp = spacy.load("en_ner_bc5cdr_md")

# Sample physician note
text = """
Physician: Good morning, Ms. Jones. How are you feeling today?
Patient: Good morning, doctor. I’m doing better, but I still have some discomfort now and then.
Physician: I understand you were in a car accident last September. Can you walk me through what happened?
Patient: Yes, it was on September 1st, around 12:30 in the afternoon. I was driving from Cheadle Hulme to Manchester when I had to stop in traffic. Out of nowhere, another car hit me from behind, which pushed my car into the one in front.
Physician: That sounds like a strong impact. Were you wearing your seatbelt?
Patient: Yes, I always do.
Physician: What did you feel immediately after the accident?
Patient: At first, I was just shocked. But then I realized I had hit my head on the steering wheel, and I could feel pain in my neck and back almost right away.
Physician: Did you seek medical attention at that time?
Patient: Yes, I went to Moss Bank Accident and Emergency. They checked me over and said it was a whiplash injury, but they didn’t do any X-rays. They just gave me some advice and sent me home.
Physician: How did things progress after that?
Patient: The first four weeks were rough. My neck and back pain were really bad—I had trouble sleeping and had to take painkillers regularly. It started improving after that, but I had to go through ten sessions of physiotherapy to help with the stiffness and discomfort.
Physician: That makes sense. Are you still experiencing pain now?
Patient: It’s not constant, but I do get occasional backaches. It’s nothing like before, though.
Physician: That’s good to hear. Have you noticed any other effects, like anxiety while driving or difficulty concentrating?
Patient: No, nothing like that. I don’t feel nervous driving, and I haven’t had any emotional issues from the accident.
Physician: And how has this impacted your daily life? Work, hobbies, anything like that?
Patient: I had to take a week off work, but after that, I was back to my usual routine. It hasn’t really stopped me from doing anything.
Physician: That’s encouraging. Let’s go ahead and do a physical examination to check your mobility and any lingering pain.
[Physical Examination Conducted]
Physician: Everything looks good. Your neck and back have a full range of movement, and there’s no tenderness or signs of lasting damage. Your muscles and spine seem to be in good condition.
Patient: That’s a relief!
Physician: Yes, your recovery so far has been quite positive. Given your progress, I’d expect you to make a full recovery within six months of the accident. There are no signs of long-term damage or degeneration.
Patient: That’s great to hear. So, I don’t need to worry about this affecting me in the future?
Physician: That’s right. I don’t foresee any long-term impact on your work or daily life. If anything changes or you experience worsening symptoms, you can always come back for a follow-up. But at this point, you’re on track for a full recovery.
Patient: Thank you, doctor. I appreciate it.
Physician: You’re very welcome, Ms. Jones. Take care, and don’t hesitate to reach out if you need anything.
"""

# Process text with SciSpaCy
doc = nlp(text)

# Extract relevant medical entities
medical_entities = {ent.text.lower(): ent.label_ for ent in doc.ents if ent.label_ in ["DISEASE", "SYMPTOM"]}

# Remove duplicate entities
unique_medical_entities = list(medical_entities.keys())

# Remove incorrect or non-relevant terms
filtered_entities = [entity for entity in unique_medical_entities if entity not in ["’d", "worry"]]

# Print filtered medical entities
print("\n🩺 **Filtered Medical Entities Found:**")
print(", ".join(filtered_entities) if filtered_entities else "No relevant medical terms found.")

# Load text summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Generate summary
summary = summarizer(text, max_length=150, min_length=80, do_sample=False)

# Print improved summary
print("\n📑 **Improved Summarized Note:**")
print(summary[0]['summary_text'])

# Extract sections from physician note
subjective_match = re.search(r"Patient: (.*)", text)
objective_match = re.search(r"Physician: .*?(\[Physical Examination Conducted\].*?)Physician:", text, re.DOTALL)

# Generate structured SOAP note
soap_note = f"""
📝 **SOAP Note**
**S (Subjective):** {subjective_match.group(1) if subjective_match else 'Not Available'}
**O (Objective):** {objective_match.group(1).strip() if objective_match else 'Not Available'}
**A (Assessment):** {", ".join(filtered_entities) if filtered_entities else "Not Available"}
**P (Plan):** Further evaluation and treatment for {", ".join(filtered_entities) if filtered_entities else "the reported symptoms"}.
"""

print("\n📄 **Improved SOAP Note:**")
print(soap_note)

