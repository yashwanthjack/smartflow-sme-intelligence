import os
import pypdf

pdf_dir = r"C:\Users\yashw\Downloads\IEEE FEB"
pdf_files = [
    "Adaptive_Portfolio_Management_in_Volatile_Markets_Using_Deep_Reinforcement_Learning.pdf",
    "Decision_Support_System_Terms_of_SMEs_Credit_Lending_Based_on_Machine_Learning_Approach.pdf",
    "Prediction_of_Delays_in_Invoice_Payments_Using_Machine_Learning.pdf",
    "Utilizing_Transforming_Portfolio_Management_Through_Automation_Using_Advanced_Deep_Reinforcement_Learning_Algorithms_for_Optimized_Investment_Strategies.pdf",
    "ai-powered-msme-credit-scoring-and-risk-analytics-platform.pdf"
]

output_dir = "extracted_pdf_content"
os.makedirs(output_dir, exist_ok=True)

for filename in pdf_files:
    pdf_path = os.path.join(pdf_dir, filename)
    if not os.path.exists(pdf_path):
        print(f"Skipping {filename}: File not found.")
        continue
    
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        output_filename = os.path.splitext(filename)[0] + ".txt"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Extracted content from {filename} to {output_path}")

    except Exception as e:
        print(f"Error extracting {filename}: {e}")
