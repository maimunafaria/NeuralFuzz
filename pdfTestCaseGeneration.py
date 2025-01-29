# import os
# import torch
# from transformers import GPT2LMHeadModel, GPT2Tokenizer
# from pathlib import Path
# import sys

# # [Previous PDFComponentGenerator class and generate_and_save_pdf function remain the same]
# class PDFComponentGenerator:
#     def __init__(self, model, tokenizer, temperature=0.6):
#         self.model = model
#         self.tokenizer = tokenizer
#         self.temperature = temperature
#         self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
#     def generate_component(self, prompt, max_length=512):
#         inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)
        
#         outputs = self.model.generate(
#             **inputs,
#             max_length=max_length,
#             num_return_sequences=1,
#             temperature=self.temperature,
#             top_p=0.9,
#             top_k=50,
#             pad_token_id=self.tokenizer.eos_token_id,
#             do_sample=True
#         )
        
#         return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

#     # [All the generate_* methods remain exactly the same]
#     def generate_header(self):
#         prompt = """%PDF-1.4
# %âãÏÓ"""
#         return self.generate_component(prompt)
    
#     def generate_catalog(self):
#         prompt = """1 0 obj
# <<
# /Type /Catalog
# /Pages 2 0 R
# >>
# endobj"""
#         return self.generate_component(prompt)
    
#     def generate_pages(self):
#         prompt = """2 0 obj
# <<
# /Type /Pages
# /Kids [3 0 R]
# /Count 1
# >>
# endobj"""
#         return self.generate_component(prompt)
    
#     def generate_page(self):
#         prompt = """3 0 obj
# <<
# /Type /Page
# /Parent 2 0 R
# /Resources <<
# /Font <<
# /F1 4 0 R
# >>
# /ProcSet [/PDF /Text /ImageB /ImageC /ImageI]
# >>
# /MediaBox [0 0 612 792]
# /Contents 5 0 R
# >>
# endobj"""
#         return self.generate_component(prompt)
    
#     def generate_font(self):
#         prompt = """4 0 obj
# <<
# /Type /Font
# /Subtype /Type1
# /BaseFont /Helvetica
# >>
# endobj"""
#         return self.generate_component(prompt)
    
#     def generate_content_stream(self):
#         prompt = """5 0 obj
# <<
# /Length 44
# >>
# stream
# BT
# /F1 24 Tf
# 72 720 Td
# (Hello, World!) Tj
# ET
# endstream
# endobj"""
#         return self.generate_component(prompt)
    
#     def generate_xref(self):
#         prompt = """xref
# 0 6
# 0000000000 65535 f
# 0000000015 00000 n
# 0000000074 00000 n
# 0000000192 00000 n
# 0000000372 00000 n
# 0000000465 00000 n"""
#         return self.generate_component(prompt)
    
#     def generate_trailer(self):
#         prompt = """trailer
# <<
# /Size 6
# /Root 1 0 R
# >>
# startxref
# 565
# %%EOF"""
#         return self.generate_component(prompt)
    
#     def generate_complete_pdf(self):
#         """
#         Generate a complete PDF by combining all components
#         """
#         components = [
#             self.generate_header(),
#             self.generate_catalog(),
#             self.generate_pages(),
#             self.generate_page(),
#             self.generate_font(),
#             self.generate_content_stream(),
#             self.generate_xref(),
#             self.generate_trailer()
#         ]
        
#         return "\n\n".join(components)

# def generate_and_save_pdf(checkpoint_path, output_file, temperature=0.6):
#     """
#     Generate and save a complete PDF
#     """
#     try:
#         # Load model
#         model = GPT2LMHeadModel.from_pretrained(checkpoint_path)
#         tokenizer = GPT2Tokenizer.from_pretrained(checkpoint_path)
#         tokenizer.pad_token = tokenizer.eos_token
#         model.to('cuda' if torch.cuda.is_available() else 'cpu')
#         model.eval()
        
#         # Create generator
#         generator = PDFComponentGenerator(model, tokenizer, temperature)
        
#         # Generate complete PDF
#         print("Generating PDF components...")
#         pdf_text = generator.generate_complete_pdf()
        
#         # Save the generated PDF
#         print(f"Saving PDF to {output_file}")
#         with open(output_file, 'w', encoding='utf-8') as f:
#             f.write(pdf_text)
        
#         # Print the structure
#         print("\nGenerated PDF structure:")
#         print("=" * 50)
#         print(pdf_text)
#         print("=" * 50)
        
#         return pdf_text
        
#     except Exception as e:
#         print(f"Error generating PDF: {str(e)}")
#         raise


# if __name__ == "__main__":
#     # Get arguments from command line
#     num_test_cases = int(sys.argv[1])
#     working_dir = sys.argv[2]
#     generated_dir = sys.argv[3]
    
#     # Set up paths
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     model_path = os.path.join(script_dir, "best_Model_PDF")
    
#     # Create output directory if it doesn't exist
#     os.makedirs(generated_dir, exist_ok=True)
    
#     print(f"Generating {num_test_cases} test cases...")
#     print(f"Using model from: {model_path}")
#     print(f"Saving outputs to: {generated_dir}")
    
#     # Generate multiple test cases based on command line argument
#     for i in range(num_test_cases):
#         output_file = os.path.join(generated_dir, f"generated_pdf_{i+1}.txt")
#         print(f"\nGenerating test case {i+1}...")
#         pdf_text = generate_and_save_pdf(model_path, output_file)
    
#     print(f"\nGenerated {num_test_cases} PDF files in {generated_dir}")


# if __name__ == "__main__":
#     # Get the number of test cases from command-line arguments
#     num_test_cases = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
#     # Get the current script directory and set up paths
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     model_path = os.path.join(script_dir, "best_Model_PDF")
#     output_dir = os.path.join(script_dir, "generated_pdfs")
    
#     # Create output directory if it doesn't exist
#     os.makedirs(output_dir, exist_ok=True)
    
#     print(f"Generating {num_test_cases} test cases...")
#     print(f"Using model from: {model_path}")
#     print(f"Saving outputs to: {output_dir}")
    
#     # Generate multiple test cases based on command line argument
#     for i in range(num_test_cases):
#         output_file = os.path.join(output_dir, f"generated_pdf_{i+1}.txt")
#         print(f"\nGenerating test case {i+1}...")
#         pdf_text = generate_and_save_pdf(model_path, output_file)
    
#     print(f"\nGenerated {num_test_cases} PDF files in {output_dir}")


import os
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from pathlib import Path
import sys

class PDFComponentGenerator:
    def __init__(self, model, tokenizer, temperature=0.6):
        self.model = model
        self.tokenizer = tokenizer
        self.temperature = temperature
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def generate_component(self, prompt, max_length=512):
        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)
        
        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_return_sequences=1,
            temperature=self.temperature,
            top_p=0.9,
            top_k=50,
            pad_token_id=self.tokenizer.eos_token_id,
            do_sample=True
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def generate_header(self):
        prompt = """%PDF-1.4
%âãÏÓ"""
        return self.generate_component(prompt)
    
    def generate_catalog(self):
        prompt = """1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj"""
        return self.generate_component(prompt)
    
    def generate_pages(self):
        prompt = """2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj"""
        return self.generate_component(prompt)
    
    def generate_page(self):
        prompt = """3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 4 0 R
>>
/ProcSet [/PDF /Text /ImageB /ImageC /ImageI]
>>
/MediaBox [0 0 612 792]
/Contents 5 0 R
>>
endobj"""
        return self.generate_component(prompt)
    
    def generate_font(self):
        prompt = """4 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj"""
        return self.generate_component(prompt)
    
    def generate_content_stream(self):
        prompt = """5 0 obj
<<
/Length 44
>>
stream
BT
/F1 24 Tf
72 720 Td
(Hello, World!) Tj
ET
endstream
endobj"""
        return self.generate_component(prompt)
    
    def generate_xref(self):
        prompt = """xref
0 6
0000000000 65535 f
0000000015 00000 n
0000000074 00000 n
0000000192 00000 n
0000000372 00000 n
0000000465 00000 n"""
        return self.generate_component(prompt)
    
    def generate_trailer(self):
        prompt = """trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
565
%%EOF"""
        return self.generate_component(prompt)
    
    def generate_complete_pdf(self):
        """Generate a complete PDF by combining all components"""
        components = [
            self.generate_header(),
            self.generate_catalog(),
            self.generate_pages(),
            self.generate_page(),
            self.generate_font(),
            self.generate_content_stream(),
            self.generate_xref(),
            self.generate_trailer()
        ]
        
        return "\n\n".join(components)

class PDFGenerator:
    def __init__(self):
        """Initialize the PDF Generator"""
        self.model = None
        self.tokenizer = None
        self.initialized = False
        
    def get_resource_path(self, relative_path):
        """Get the absolute path to a resource, considering PyInstaller's _MEIPASS."""
        try:
            base_path = sys._MEIPASS  # PyInstaller temporary directory
        except AttributeError:
            base_path = os.path.abspath(".")  # Development environment
        return os.path.join(base_path, relative_path)
        
    def initialize_model(self):
        """Initialize the model and tokenizer"""
        try:
            if not self.initialized:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                model_path = os.path.join(script_dir, "best_Model_PDF")
                
                print(f"Loading PDF model from: {model_path}")
                self.model = GPT2LMHeadModel.from_pretrained(model_path)
                self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.model.to('cuda' if torch.cuda.is_available() else 'cpu')
                self.model.eval()
                
                self.initialized = True
            return True
        except Exception as e:
            print(f"Error initializing model: {str(e)}")
            return False

def generate_pdf(count, working_dir, output_dir):
    """
    Generate PDF test cases. This is the main function that will be imported
    and used by the TestCaseGeneratorThread.
    
    Args:
        count (int): Number of PDF files to generate
        working_dir (str): Working directory path
        output_dir (str): Output directory for generated files
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize generator
        generator = PDFGenerator()
        if not generator.initialize_model():
            raise Exception("Failed to initialize PDF model")
        
        # Create component generator
        component_generator = PDFComponentGenerator(
            generator.model,
            generator.tokenizer
        )
        
        # Generate PDFs
        print(f"Generating {count} PDF test cases...")
        for i in range(count):
            output_file = os.path.join(output_dir, f"generated_pdf_{i+1}.txt")
            
            # Generate PDF content
            pdf_text = component_generator.generate_complete_pdf()
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(pdf_text)
            
            print(f"Generated PDF {i+1}/{count}")
        
        print(f"Successfully generated {count} PDF files in {output_dir}")
        return True
        
    except Exception as e:
        print(f"Error generating PDFs: {str(e)}")
        return False

# For command line usage
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python pdfTestCaseGeneration.py <count> <working_dir> <output_dir>")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
        working_dir = sys.argv[2]
        output_dir = sys.argv[3]
        
        success = generate_pdf(count, working_dir, output_dir)
        if not success:
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)