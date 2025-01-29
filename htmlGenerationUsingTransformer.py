

# import os
# import random
# import sys
# from transformers import GPT2Tokenizer, GPT2LMHeadModel

# def get_resource_path(relative_path):
#     """Get the absolute path to a resource, considering PyInstaller's _MEIPASS."""
#     try:
#         base_path = sys._MEIPASS  # PyInstaller temporary directory
#     except AttributeError:
#         base_path = os.path.abspath(".")  # Development environment
#     return os.path.join(base_path, relative_path)

# # Step 1: Load the fine-tuned model and tokenizer
# # Use dynamic paths for the fine-tuned model directory
# script_dir = os.path.dirname(os.path.abspath(__file__))
# output_dir = get_resource_path("fine_tuned_gpt2")  # Path to fine-tuned GPT-2

# model = GPT2LMHeadModel.from_pretrained(output_dir)
# tokenizer = GPT2Tokenizer.from_pretrained(output_dir)

# # Prompts for HTML generation
# prompts = [
#     "<html><body>", "<html><body><h1>", "<html><body><p>", "<html><body><div>", "<html><body><span>",
#     "<html><body><ul>", "<html><body><li>", "<html><body><a>", "<html><body><img>", "<html><body><table>",
#     "<html><body><form>", "<html><body><input>", "<html><body><button>", "<html><body><header>", "<html><body><footer>",
#     "<html><body><nav>", "<html><body><section>", "<html><body><article>", "<html><body><aside>", "<html><body><blockquote>",
#     "<html><body><canvas>", "<html><body><iframe>", "<html><body><label>", "<html><body><code>", "<html><body><strong>",
#     "<html><body><em>", "<html><body><figure>", "<html><body><figcaption>", "<html><body><abbr>", "<html><body><address>",
#     "<html><body><audio>", "<html><body><b>", "<html><body><cite>", "<html><body><datalist>", "<html><body><details>",
#     "<html><body><dialog>", "<html><body><dfn>", "<html><body><kbd>", "<html><body><mark>", "<html><body><meter>",
#     "<html><body><noscript>", "<html><body><object>", "<html><body><output>", "<html><body><progress>", "<html><body><q>",
#     "<html><body><ruby>", "<html><body><s>", "<html><body><samp>", "<html><body><small>", "<html><body><source>",
#     "<html><body><sub>", "<html><body><sup>", "<html><body><template>", "<html><body><time>", "<html><body><track>",
#     "<html><body><u>", "<html><body><var>", "<html><body><video>", "<html><body><wbr>", "<html><body><main>",
#     "<html><body><summary>", "<html><body><h2>", "<html><body><h3>", "<html><body><h4>", "<html><body><h5>",
#     "<html><body><h6>", "<html><body><dl>", "<html><body><dt>", "<html><body><dd>", "<html><body><menu>",
#     "<html><body><menuitem>", "<html><body><optgroup>", "<html><body><option>", "<html><body><script>", "<html><body><style>",
#     "<html><body><svg>", "<html><body><math>", "<html><body><base>", "<html><body><link>", "<html><body><meta>",
#     "<html><body><title>", "<html><body><html>", "<html><body><head>", "<html><body><body>", "<html><body><br>",
#     "<html><body><hr>", "<html><body><bdi>", "<html><body><bdo>", "<html><body><big>", "<html><body><center>",
#     "<html><body><col>", "<html><body><colgroup>", "<html><body><del>", "<html><body><dir>", "<html><body><font>",
#     "<html><body><frame>", "<html><body><frameset>", "<html><body><isindex>", "<html><body><marquee>", "<html><body><noframes>",
# ]

# # Step 3: Define the HTML generation function
# def generate_html(prompt, model, tokenizer, max_length=512, num_return_sequences=1, temperature=0.7):
#     """
#     Generate HTML content based on the prompt.
#     """
#     inputs = tokenizer(prompt, return_tensors="pt")
#     outputs = model.generate(
#         inputs["input_ids"],
#         max_length=max_length,
#         num_return_sequences=num_return_sequences,
#         temperature=temperature,
#         num_beams=5,
#         eos_token_id=tokenizer.eos_token_id,
#     )
#     return [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]

# # Get arguments
# num_test_cases = int(sys.argv[1])
# working_dir = sys.argv[2]
# generated_dir = sys.argv[3]

# # Ensure generated directory exists
# os.makedirs(generated_dir, exist_ok=True)

# # Step 4: Select prompts and generate HTML files
# selected_prompts = ["<html><body>"] + random.sample(prompts[1:], num_test_cases - 1)

# generated_htmls = []
# for prompt in selected_prompts:
#     generated_html = generate_html(prompt, model, tokenizer, max_length=512, num_return_sequences=1, temperature=0.7)
#     generated_htmls.append(generated_html[0])

# # Step 5: Save the generated HTML files in the specified directory
# for i, html in enumerate(generated_htmls):
#     with open(os.path.join(generated_dir, f"generated_html_{i + 1}.html"), 'w', encoding='utf-8') as f:
#         f.write(html)

# print(f"Generated {num_test_cases} HTML files saved in {generated_dir}")

import os
import random
import sys
from transformers import GPT2Tokenizer, GPT2LMHeadModel

class HTMLGenerator:
    # HTML generation prompts
    PROMPTS = [
        "<html><body>", "<html><body><h1>", "<html><body><p>", "<html><body><div>", "<html><body><span>",
        "<html><body><ul>", "<html><body><li>", "<html><body><a>", "<html><body><img>", "<html><body><table>",
        "<html><body><form>", "<html><body><input>", "<html><body><button>", "<html><body><header>", "<html><body><footer>",
        # ... (rest of your prompts)
    ]

    def __init__(self):
        """Initialize the HTML Generator"""
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
        """Initialize the transformer model and tokenizer"""
        try:
            if not self.initialized:
                # Use dynamic paths for the fine-tuned model directory
                output_dir = self.get_resource_path("fine_tuned_gpt2")
                
                print(f"Loading model from: {output_dir}")
                self.model = GPT2LMHeadModel.from_pretrained(output_dir)
                self.tokenizer = GPT2Tokenizer.from_pretrained(output_dir)
                self.initialized = True
            return True
        except Exception as e:
            print(f"Error initializing model: {str(e)}")
            return False

    def generate_html(self, prompt, max_length=512, num_return_sequences=1, temperature=0.7):
        """Generate HTML content based on the prompt."""
        if not self.initialized and not self.initialize_model():
            raise Exception("Failed to initialize model")

        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            temperature=temperature,
            num_beams=5,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        return [self.tokenizer.decode(output, skip_special_tokens=True) for output in outputs]

    def generate_html_files(self, count, working_dir, output_dir):
        """Generate multiple HTML files"""
        try:
            # Initialize model if not already initialized
            if not self.initialized and not self.initialize_model():
                raise Exception("Failed to initialize model")

            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

            # Select prompts
            selected_prompts = ["<html><body>"] + random.sample(self.PROMPTS[1:], count - 1)

            # Generate files
            for i, prompt in enumerate(selected_prompts):
                generated_html = self.generate_html(prompt, max_length=512, num_return_sequences=1, temperature=0.7)
                
                output_file = os.path.join(output_dir, f"generated_html_{i + 1}.html")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(generated_html[0])

            print(f"Generated {count} HTML files saved in {output_dir}")
            return True

        except Exception as e:
            print(f"Error generating HTML files: {str(e)}")
            return False

# For command line usage
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python htmlGenerationUsingTransformer.py <count> <working_dir> <output_dir>")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
        working_dir = sys.argv[2]
        output_dir = sys.argv[3]

        generator = HTMLGenerator()
        success = generator.generate_html_files(count, working_dir, output_dir)
        
        if not success:
            sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)