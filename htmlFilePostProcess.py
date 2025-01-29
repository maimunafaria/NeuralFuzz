# # from bs4 import BeautifulSoup
# # import os
# # import sys

# # def get_resource_path(relative_path):
# #     """Get the absolute path to a resource, considering PyInstaller's _MEIPASS."""
# #     try:
# #         base_path = sys._MEIPASS  # Path used by PyInstaller in the packaged app
# #     except AttributeError:
# #         base_path = os.path.abspath(".")  # Path during development
# #     return os.path.join(base_path, relative_path)

# # def fix_html_structure(html_content):
# #     """Fix the HTML structure using BeautifulSoup."""
# #     soup = BeautifulSoup(html_content, 'html.parser')
# #     return soup.prettify()

# # def process_generated_html(input_folder, output_folder):
# #     """Process and fix the structure of all HTML files in the input folder."""
# #     os.makedirs(output_folder, exist_ok=True)

# #     for filename in os.listdir(input_folder):
# #         if filename.endswith('.html'):
# #             input_path = os.path.join(input_folder, filename)
# #             output_path = os.path.join(output_folder, filename)

# #             with open(input_path, 'r', encoding='utf-8') as file:
# #                 html_content = file.read()

# #             # Fix structure and save
# #             fixed_html = fix_html_structure(html_content)
# #             with open(output_path, 'w', encoding='utf-8') as output_file:
# #                 output_file.write(fixed_html)

# #             print(f"Fixed structure: {filename}")

# # # Set paths dynamically using get_resource_path
# # generated_path = get_resource_path("generated_htmls")
# # generated_path_post = get_resource_path("generated_htmls_Processed")

# # print(f"Input folder: {generated_path}")
# # print(f"Output folder: {generated_path_post}")

# # # Process the generated HTML files
# # process_generated_html(generated_path, generated_path_post)

# from bs4 import BeautifulSoup
# import os
# import sys

# def get_resource_path(relative_path):
#     """Get the absolute path to a resource, considering PyInstaller's _MEIPASS."""
#     try:
#         base_path = sys._MEIPASS  # Path used by PyInstaller in the packaged app
#     except AttributeError:
#         base_path = os.path.abspath(".")  # Path during development
#     return os.path.join(base_path, relative_path)

# def fix_html_structure(html_content):
#     """Fix the HTML structure using BeautifulSoup."""
#     soup = BeautifulSoup(html_content, 'html.parser')
#     return soup.prettify()

# def process_generated_html(input_folder, output_folder):
#     """Process and fix the structure of all HTML files in the input folder."""
#     os.makedirs(output_folder, exist_ok=True)
    
#     for filename in os.listdir(input_folder):
#         if filename.endswith('.html'):
#             input_path = os.path.join(input_folder, filename)
#             output_path = os.path.join(output_folder, filename)
            
#             with open(input_path, 'r', encoding='utf-8') as file:
#                 html_content = file.read()
            
#             # Fix structure and save
#             fixed_html = fix_html_structure(html_content)
#             with open(output_path, 'w', encoding='utf-8') as output_file:
#                 output_file.write(fixed_html)
            
#             print(f"Fixed structure: {filename}")

# # Get arguments
# working_dir = sys.argv[1]
# generated_dir = sys.argv[2]
# processed_dir = os.path.join(working_dir, "generated_html_preprocessed")

# print(f"Input folder: {generated_dir}")
# print(f"Output folder: {processed_dir}")

# # Process the generated HTML files
# process_generated_html(generated_dir, processed_dir)

# # from bs4 import BeautifulSoup
# # import os
# # def fix_html_structure(html_content):
# #     soup = BeautifulSoup(html_content, 'html.parser')
# #     return soup.prettify()

# # def process_generated_html(input_folder, output_folder):
# #     os.makedirs(output_folder, exist_ok=True)

# #     for filename in os.listdir(input_folder):
# #         if filename.endswith('.html'):
# #             input_path = os.path.join(input_folder, filename)
# #             output_path = os.path.join(output_folder, filename)

# #             with open(input_path, 'r', encoding='utf-8') as file:
# #                 html_content = file.read()

# #             # Fix structure and save
# #             fixed_html = fix_html_structure(html_content)
# #             with open(output_path, 'w', encoding='utf-8') as output_file:
# #                 output_file.write(fixed_html)

# #             print(f"Fixed structure: {filename}")

# # current_dir = os.path.dirname(__file__)
# # generated_path = os.path.join(current_dir, "generated_htmls")
# # generated_path_Post = os.path.join(current_dir, "generated_htmls_Processed")
# # print(generated_path)
# # process_generated_html(generated_path, generated_path_Post)


from bs4 import BeautifulSoup
import os
import sys

class HTMLPostProcessor:
    def __init__(self):
        """Initialize the HTML Post Processor"""
        pass

    def get_resource_path(self, relative_path):
        """Get the absolute path to a resource, considering PyInstaller's _MEIPASS."""
        try:
            base_path = sys._MEIPASS  # Path used by PyInstaller in the packaged app
        except AttributeError:
            base_path = os.path.abspath(".")  # Path during development
        return os.path.join(base_path, relative_path)

    def fix_html_structure(self, html_content):
        """Fix the HTML structure using BeautifulSoup."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.prettify()
        except Exception as e:
            print(f"Error fixing HTML structure: {str(e)}")
            raise

    def process_html_files(self, input_folder, output_folder):
        """
        Process and fix the structure of all HTML files in the input folder.
        
        Returns:
            tuple: (success_count, total_count)
        """
        success_count = 0
        total_count = 0

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)

            # Process each HTML file
            for filename in os.listdir(input_folder):
                if filename.endswith('.html'):
                    total_count += 1
                    try:
                        input_path = os.path.join(input_folder, filename)
                        output_path = os.path.join(output_folder, filename)

                        # Read input file
                        with open(input_path, 'r', encoding='utf-8') as file:
                            html_content = file.read()

                        # Fix structure and save
                        fixed_html = self.fix_html_structure(html_content)
                        with open(output_path, 'w', encoding='utf-8') as output_file:
                            output_file.write(fixed_html)

                        print(f"Fixed structure: {filename}")
                        success_count += 1

                    except Exception as e:
                        print(f"Error processing file {filename}: {str(e)}")
                        continue

            return success_count, total_count

        except Exception as e:
            print(f"Error in process_html_files: {str(e)}")
            return success_count, total_count

# For command line usage
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python htmlFilePostProcess.py <working_dir> <generated_dir>")
        sys.exit(1)

    try:
        working_dir = sys.argv[1]
        generated_dir = sys.argv[2]
        processed_dir = os.path.join(working_dir, "generated_html_preprocessed")

        print(f"Input folder: {generated_dir}")
        print(f"Output folder: {processed_dir}")

        processor = HTMLPostProcessor()
        success_count, total_count = processor.process_html_files(generated_dir, processed_dir)

        if success_count != total_count:
            print(f"Warning: Only processed {success_count} out of {total_count} files")
            sys.exit(1)

        print(f"Successfully processed all {success_count} files")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)