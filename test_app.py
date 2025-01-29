import os
import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QComboBox, QLabel, QLineEdit, QMessageBox,
                             QFileDialog, QListWidget, QHBoxLayout, QGridLayout)
from PyQt6.QtCore import QThread, pyqtSignal, QRunnable, QThreadPool, Qt

from datetime import datetime
from HTMLDynamicAnalyzer import HTMLDynamicAnalyzer
from PDFDynamicAnalyzer import PDFDynamicAnalyzer
from PyQt6.QtWidgets import QProgressDialog, QMessageBox
# class TestCaseGeneratorThread(QThread):
#     generation_complete = pyqtSignal(str, str)
#     generation_error = pyqtSignal(str)

#     def __init__(self, count, working_dir, current_script_dir, file_type):
#         super().__init__()
#         self.count = count
#         self.working_dir = working_dir
#         self.current_script_dir = current_script_dir
#         self.file_type = file_type

#     def run(self):
#         try:
#             # Determine output directories based on file type
#             if self.file_type == "HTML":
#                 generated_dir = os.path.join(self.working_dir, "generated_html")
#                 processed_dir = os.path.join(self.working_dir, "generated_html_preprocessed")
#                 # Create directories
#                 os.makedirs(generated_dir, exist_ok=True)
#                 os.makedirs(processed_dir, exist_ok=True)
#             else:  # PDF
#                 generated_dir = os.path.join(self.working_dir, "generated_pdf")
#                 os.makedirs(generated_dir, exist_ok=True)

#             # Determine which script to run based on file type
#             if self.file_type == "HTML":
#                 html_train_script = os.path.join(self.current_script_dir, "htmlGenerationUsingTransformer.py")
#                 html_post_process_script = os.path.join(self.current_script_dir, "htmlFilePostProcess.py")

#                 # Run HTML generation scripts with working_dir and generated_dir as the target directories
#                 # subprocess.run([sys.executable, html_train_script, str(self.count), self.working_dir, generated_dir], 
#                 #             check=True, cwd=self.current_script_dir)
#                 # processed_dir = os.path.join(self.working_dir, "generated_html_preprocessed")
#                 # subprocess.run([sys.executable, html_post_process_script, self.working_dir, generated_dir, processed_dir], 
#                 #             check=True, cwd=self.current_script_dir)
                
#                 # Emit complete signal with processed directory
#                 self.generation_complete.emit(processed_dir, self.file_type)
#             else:  # PDF
#                 pdf_script = os.path.join(self.current_script_dir, "pdfTestCaseGeneration.py")
#                 subprocess.run([sys.executable, pdf_script, str(self.count), self.working_dir, generated_dir], 
#                             check=True, cwd=self.current_script_dir)
                
#                 # Emit complete signal with generated directory
#                 self.generation_complete.emit(generated_dir, self.file_type)

#         except subprocess.CalledProcessError as e:
#             self.generation_error.emit(f"Error during test case generation: {str(e)}")
#         except Exception as e:
#             self.generation_error.emit(f"Unexpected error: {str(e)}")

class TestCaseGeneratorThread(QThread):
    generation_complete = pyqtSignal(str, str)
    generation_error = pyqtSignal(str)
    progress_update = pyqtSignal(str)

    def __init__(self, count, working_dir, current_script_dir, file_type):
        super().__init__()
        self.count = count
        self.working_dir = working_dir
        self.current_script_dir = current_script_dir
        self.file_type = file_type

    def run(self):
        try:
            self.progress_update.emit("Starting generation process...")

            if self.file_type == "HTML":
                # Set up directories
                generated_dir = os.path.join(self.working_dir, "generated_html")
                processed_dir = os.path.join(self.working_dir, "generated_html_preprocessed")
                
                self.progress_update.emit("Creating directories...")
                os.makedirs(generated_dir, exist_ok=True)
                os.makedirs(processed_dir, exist_ok=True)

                try:
                    # Import and use HTMLGenerator class
                    from htmlGenerationUsingTransformer import HTMLGenerator
                    
                    # Create generator instance and generate files
                    self.progress_update.emit("Initializing HTML generator...")
                    generator = HTMLGenerator()
                    
                    self.progress_update.emit("Generating HTML files...")
                    success = generator.generate_html_files(self.count, self.working_dir, generated_dir)
                    if not success:
                        raise Exception("HTML generation failed")

                    # Import and use post-processor
                    from htmlFilePostProcess import HTMLPostProcessor
                    
                    self.progress_update.emit("Post-processing HTML files...")
                    processor = HTMLPostProcessor()
                    success_count, total_count = processor.process_html_files(generated_dir, processed_dir)
                    
                    if success_count != total_count:
                        raise Exception(f"Post-processing failed: only {success_count} of {total_count} files processed")
                    
                except ImportError as e:
                    self.progress_update.emit(f"Error importing generation modules: {str(e)}")
                    raise
                except Exception as e:
                    self.progress_update.emit(f"Error during HTML processing: {str(e)}")
                    raise
                
                self.progress_update.emit("HTML generation and processing completed!")
                self.generation_complete.emit(processed_dir, self.file_type)

            else:  # PDF
                generated_dir = os.path.join(self.working_dir, "generated_pdf")
                os.makedirs(generated_dir, exist_ok=True)

                try:
                    # Import PDF generation function
                    from pdfTestCaseGeneration import generate_pdf
                    
                    self.progress_update.emit("Generating PDF files...")
                    success = generate_pdf(self.count, self.working_dir, generated_dir)
                    
                    if not success:
                        raise Exception("PDF generation failed")
                    
                except ImportError as e:
                    self.progress_update.emit(f"Error importing PDF module: {str(e)}")
                    raise
                
                self.progress_update.emit("PDF generation completed!")
                self.generation_complete.emit(generated_dir, self.file_type)

        except Exception as e:
            error_msg = f"Error during generation: {str(e)}"
            self.progress_update.emit(error_msg)
            self.generation_error.emit(error_msg)
            
class TestCaseGenerator(QMainWindow):

    def __init__(self):
        super().__init__()
        
        # Set up main window
        self.setWindowTitle("Test Case Generator")
        self.setFixedSize(800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QGridLayout(main_widget)
        self.setCentralWidget(main_widget)
        
        # Initialize variables
        self.main_class_path = ""
        self.additional_files = []
        
        # Create layout sections
        self.create_source_selection_section(main_layout)
        self.create_test_generation_section(main_layout)
        self.create_action_section(main_layout)

    def create_source_selection_section(self, main_layout):
        """Section for selecting main and additional source files"""
        # Main class selection
        main_class_layout = QHBoxLayout()
        main_class_layout.addWidget(QLabel("Main Class:"))
        self.main_class_entry = QLineEdit()
        main_class_layout.addWidget(self.main_class_entry)
        
        select_main_btn = QPushButton("Browse")
        select_main_btn.clicked.connect(self.select_main_class)
        main_class_layout.addWidget(select_main_btn)
        
        # Additional files list
        additional_files_label = QLabel("Additional Files:")
        self.additional_files_list = QListWidget()
        
        # Add additional files button
        add_files_btn = QPushButton("Add Additional Files")
        add_files_btn.clicked.connect(self.select_additional_files)
        
        # Compile command section
        compile_command_layout = QHBoxLayout()
        compile_command_label = QLabel("Compile Command:")
        self.compile_command_entry = QLineEdit()
        self.compile_command_entry.setPlaceholderText("javac {selected_file}")
        
        compile_command_layout.addWidget(compile_command_label)
        compile_command_layout.addWidget(self.compile_command_entry)
        
        # Create a vertical layout for this section
        source_section = QVBoxLayout()
        source_section.addLayout(main_class_layout)
        source_section.addWidget(additional_files_label)
        source_section.addWidget(self.additional_files_list)
        source_section.addWidget(add_files_btn)
        
        # Add compile command layout
        source_section.addLayout(compile_command_layout)
        
        # Add to grid layout
        main_layout.addLayout(source_section, 0, 0, 1, 2)

    def create_test_generation_section(self, main_layout):
        """Section for test case generation options"""
        # File type selection
        file_type_layout = QHBoxLayout()
        file_type_layout.addWidget(QLabel("File Type:"))
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["HTML", "PDF"])
        file_type_layout.addWidget(self.file_type_combo)
        
        # Test case count
        test_case_layout = QHBoxLayout()
        test_case_layout.addWidget(QLabel("Number of Test Cases:"))
        self.test_case_input = QLineEdit()
        test_case_layout.addWidget(self.test_case_input)
        
        # Generate button
        generate_btn = QPushButton("Generate Test Cases")
        generate_btn.clicked.connect(self.generate_test_cases)
        
        # Create a vertical layout for this section
        test_gen_section = QVBoxLayout()
        test_gen_section.addLayout(file_type_layout)
        test_gen_section.addLayout(test_case_layout)
        test_gen_section.addWidget(generate_btn)
        
        # Add to grid layout
        main_layout.addLayout(test_gen_section, 1, 0)

    def create_action_section(self, main_layout):
        """Section for actions and generated files"""
        # Generated files list
        generated_files_label = QLabel("Generated Files:")
        self.generated_files_list = QListWidget()
        
        # Action buttons
        action_layout = QHBoxLayout()
        open_dir_btn = QPushButton("Open Output Directory")
        open_dir_btn.clicked.connect(self.open_output_directory)
        action_layout.addWidget(open_dir_btn)
        compile_btn= QPushButton("Complie the Software")
        compile_btn.clicked.connect(self.compile_software)
        action_layout.addWidget(compile_btn)
        
        fuzz_btn = QPushButton("Fuzz")
        fuzz_btn.clicked.connect(self.run_fuzzing)
        action_layout.addWidget(fuzz_btn)
        
        analyze_btn = QPushButton("Analyze")
        analyze_btn.clicked.connect(self.run_analysis)
        action_layout.addWidget(analyze_btn)
        
        # Create a vertical layout for this section
        action_section = QVBoxLayout()
        action_section.addWidget(generated_files_label)
        action_section.addWidget(self.generated_files_list)
        action_section.addLayout(action_layout)
        
        # Add to grid layout
        main_layout.addLayout(action_section, 1, 1)

    def select_main_class(self):
        """
        Opens a file dialog to select the main Java class file.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Main Java File", "", "Java files (*.java)")
        if file_path:
            self.main_class_path = file_path
            # Clear and set the entry
            self.main_class_entry.clear()
            self.main_class_entry.setText(file_path)

    def select_additional_files(self):
        """
        Opens a file dialog to select additional Java files and adds them to the listbox.
        """
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Additional Java Files", "", "Java files (*.java)")
        if file_paths:
            # Clear previous selections
            self.additional_files.clear()
            self.additional_files_list.clear()
            
            for path in file_paths:
                # Don't add if it's the main class
                if path != self.main_class_path:
                    self.additional_files_list.addItem(path)
                    self.additional_files.append(path)

    def get_resource_path(self, relative_path):
        """
        Get the absolute path to a resource, considering PyInstaller's _MEIPASS.
        
        Args:
            relative_path (str): Path to the resource relative to the application
        
        Returns:
            str: Absolute path to the resource
        """
        try:
            # Path used by PyInstaller in the packaged app
            base_path = sys._MEIPASS
        except AttributeError:
            # Path during development
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)

    def generate_test_cases(self):
        # Prevent multiple threads from being created
        if hasattr(self, 'generation_thread') and self.generation_thread.isRunning():
            QMessageBox.warning(self, "In Progress", "Test case generation is already running.")
            return

        # Validate inputs
        try:
            count = int(self.test_case_input.text())
            if count <= 0:
                QMessageBox.critical(self, "Error", "Please enter a positive number of test cases")
                return
        except ValueError:
            QMessageBox.critical(self, "Error", "Please enter a valid number of test cases")
            return

        # Validate main class is selected
        if not self.main_class_path:
            QMessageBox.critical(self, "Error", "Please select a main class first")
            return

        # Get the directory of the main class
        working_dir = os.path.dirname(self.main_class_path)
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        file_type = self.file_type_combo.currentText()

        # Create the thread
        self.generation_thread = TestCaseGeneratorThread(
            count, working_dir, current_script_dir, file_type
        )
        
        # Connect signals
        self.generation_thread.generation_complete.connect(self.on_generation_complete)
        self.generation_thread.generation_error.connect(self.on_generation_error)
        self.generation_thread.progress_update.connect(self.update_progress_dialog)
        
        # Show progress dialog
        self.progress_dialog = QProgressDialog("Initializing...", None, 0, 0, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setWindowFlags(
            self.progress_dialog.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint
        )
        self.progress_dialog.setLabelText("Starting generation process...")
        self.progress_dialog.show()
        
        # Start the thread
        self.generation_thread.start()

    def update_progress_dialog(self, message):
        """Update the progress dialog with the latest status message"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
            self.progress_dialog.setLabelText(message)
    def on_generation_complete(self, source_dir, file_type):
        """
        Handle successful completion of test case generation
        
        Args:
            source_dir (str): Directory containing generated files
            file_type (str): Type of files generated (HTML/PDF)
        """
        # Close the progress dialog
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        # Update generated files list
        self.update_generated_files_list(source_dir)
        
        # Show success message
        QMessageBox.information(self, "Success", "Test cases generated successfully!")

        # Clear the thread reference
        if hasattr(self, 'generation_thread'):
            del self.generation_thread

    def on_generation_error(self, error_msg):
        """
        Handle errors during test case generation
        
        Args:
            error_msg (str): Error message to display
        """
        # Close the progress dialog
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        # Show error message
        QMessageBox.critical(self, "Error", error_msg)

        # Clear the thread reference
        if hasattr(self, 'generation_thread'):
            del self.generation_thread

    # def generate_test_cases(self):
    #     # Prevent multiple threads from being created
    #     if hasattr(self, 'generation_thread') and self.generation_thread.isRunning():
    #         QMessageBox.warning(self, "In Progress", "Test case generation is already running.")
    #         return

    #     # Validate inputs
    #     try:
    #         count = int(self.test_case_input.text())
    #         if count <= 0:
    #             QMessageBox.critical(self, "Error", "Please enter a positive number of test cases")
    #             return
    #     except ValueError:
    #         QMessageBox.critical(self, "Error", "Please enter a valid number of test cases")
    #         return

    #     # Validate main class is selected
    #     if not self.main_class_path:
    #         QMessageBox.critical(self, "Error", "Please select a main class first")
    #         return

    #     # Get the directory of the main class
    #     working_dir = os.path.dirname(self.main_class_path)
    #     current_script_dir = os.path.dirname(os.path.abspath(__file__))
    #     file_type = self.file_type_combo.currentText()

    #     # Create the thread
    #     self.generation_thread = TestCaseGeneratorThread(
    #         count, working_dir, current_script_dir, file_type
    #     )
        
    #     # Connect signals
    #     self.generation_thread.generation_complete.connect(self.on_generation_complete)
    #     self.generation_thread.generation_error.connect(self.on_generation_error)
        
    #     # Show progress dialog
    #     self.progress_dialog = QProgressDialog("Generating Test Cases...", None, 0, 0, self)
    #     self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
    #     self.progress_dialog.setWindowFlags(
    #         self.progress_dialog.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint
    #     )
    #     self.progress_dialog.show()
        
    #     # Start the thread
    #     self.generation_thread.start()

    # def on_generation_complete(self, source_dir, file_type):
    #     # Close the progress dialog
    #     if hasattr(self, 'progress_dialog'):
    #         self.progress_dialog.close()
        
    #     # Update generated files list
    #     self.update_generated_files_list(source_dir)
        
    #     # Show success message
    #     QMessageBox.information(self, "Success", "Test cases generated successfully!")

    #     # Clear the thread reference
    #     if hasattr(self, 'generation_thread'):
    #         del self.generation_thread

    # def on_generation_error(self, error_msg):
    #     # Close the progress dialog
    #     if hasattr(self, 'progress_dialog'):
    #         self.progress_dialog.close()
        
    #     # Show error message
    #     QMessageBox.critical(self, "Error", error_msg)

    #     # Clear the thread reference
    #     if hasattr(self, 'generation_thread'):
    #         del self.generation_thread
    

    def update_generated_files_list(self, source_dir):
        """
        Update the list of generated files in the generated files list widget.
        
        Args:
            source_dir (str): Directory containing the generated files
        """
        # Clear the existing list
        self.generated_files_list.clear()
        print(source_dir)
        print(self.generated_files_list)
        # Check if directory exists
        if not os.path.exists(source_dir):
            QMessageBox.warning(self, "Warning", f"Directory not found: {source_dir}")
            return
        
        # Get all files in the directory
        try:
            files = os.listdir(source_dir)
            # Filter for relevant file types (HTML, PDF, TXT)
            supported_extensions = ['.html', '.pdf', '.txt']
            filtered_files = [
                f for f in files 
                if any(f.lower().endswith(ext) for ext in supported_extensions)
            ]
            
            # Add files to the list
            for file in filtered_files:
                full_path = os.path.join(source_dir, file)
                self.generated_files_list.addItem(full_path)
            
            # If no files found, show a message
            if not filtered_files:
                QMessageBox.information(self, "Info", "No generated files found.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error listing files: {str(e)}")

    def open_generated_file(self, item):
        """
        Open the selected generated file
        
        Args:
            item: The QListWidgetItem representing the file
        """
        file_path = item.text()
        
        try:
            if os.path.exists(file_path):
                # Use the default application to open the file
                if sys.platform.startswith('darwin'):  # macOS
                    subprocess.call(('open', file_path))
                elif os.name == 'nt':  # Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # Linux/Unix
                    subprocess.call(('xdg-open', file_path))
            else:
                QMessageBox.warning(self, "Error", f"File not found: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def open_output_directory(self):
        """
        Open the output directory based on the selected file type
        """
        # Determine the output directory based on file type
        if not self.main_class_path:
            QMessageBox.warning(self, "Warning", "Please select a main class first")
            return

        # Get the directory of the main class
        working_dir = os.path.dirname(self.main_class_path)

        # Determine output directory based on file type
        if self.file_type_combo.currentText() == "HTML":
            output_dir = os.path.join(working_dir, "generated_html_preprocessed")
        else:  # PDF
            output_dir = os.path.join(working_dir, "generated_pdf")
        
        try:
            # Use the appropriate method to open directory based on operating system
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.call(('open', output_dir))
            elif os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif os.name == 'posix':  # Linux/Unix
                subprocess.call(('xdg-open', output_dir))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open directory: {str(e)}")


    def compile_software(self):
        """Compile the selected Java files"""
        # Validate main class selection
        if not self.main_class_path:
            QMessageBox.critical(self, "Error", "Please select a main class first!")
            return

        # Get compile command
        compile_cmd = self.compile_command_entry.text().strip()
        if not compile_cmd:
            QMessageBox.critical(self, "Error", "No compile command entered!")
            return

        # Determine working directory
        working_dir = os.path.dirname(self.main_class_path)
        compilation_successful = True

        try:
            # Compile main class first
            main_cmd = compile_cmd.replace("{selected_file}", self.main_class_path)
            subprocess.run(main_cmd, shell=True, check=True, 
                        cwd=working_dir)
            
            # Compile additional files
            for selected_file in self.additional_files:
                current_cmd = compile_cmd.replace("{selected_file}", selected_file)
                subprocess.run(current_cmd, shell=True, check=True, 
                            cwd=os.path.dirname(selected_file))
            
            # Show success message
            QMessageBox.information(self, "Success", "Compilation Successful!")
            
            # Enable fuzzing and analysis buttons
            # self.fuzzing_btn.setEnabled(True)
            # self.analysis_btn.setEnabled(True)

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Compilation error: {str(e)}")
            
            # Disable fuzzing and analysis buttons
            # self.fuzzing_btn.setEnabled(False)
            # self.analysis_btn.setEnabled(False)

    def run_fuzzing(self):
        """Run fuzzing process"""
        if not self.main_class_path:
            QMessageBox.critical(self, "Error", "Please select a main class first!")
            return

        # Determine file type and paths
        file_type = self.file_type_combo.currentText()
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        tools_dir = os.path.join(current_script_dir, "tools")

        # Set up tool paths
        jacoco_jar = os.path.join(tools_dir, "jacoco/jacocoagent.jar")
        jacoco_cli_jar = os.path.join(tools_dir, "jacoco/jacococli.jar")

        # Determine generated directory based on file type
        if file_type == "HTML":
            generated_dir = os.path.join(os.path.dirname(self.main_class_path), "generated_html_preprocessed")
            file_extension = ".html"
            analyzer = HTMLDynamicAnalyzer()
        else:  # PDF
            generated_dir = os.path.join(os.path.dirname(self.main_class_path), "generated_pdf")
            file_extension = ".txt"
            analyzer = PDFDynamicAnalyzer()

        # Verify directory exists
        if not os.path.exists(generated_dir):
            QMessageBox.critical(self, "Error", f"Directory not found: {generated_dir}")
            return

        # Get test files
        test_files = [
            os.path.join(generated_dir, f) 
            for f in os.listdir(generated_dir) 
            if f.endswith(file_extension)
        ]

        if not test_files:
            QMessageBox.critical(self, "Error", f"No {file_type} files found in the directory.")
            return

        working_dir = os.path.dirname(self.main_class_path)
        fuzzing_successful = True

        analyzer.start_analysis()

        # Run tests with dynamic analysis
        for test_file in test_files:
            try:
                # Dynamic analysis
                with open(test_file, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        if file_type.lower() == "html":
                            analyzer.check_html_structure(line, i)
                        else:
                            analyzer.check_pdf_structure(line, i)

                # Prepare Java command
                java_command = (
                    f'java -javaagent:"{jacoco_jar}"=destfile=jacoco.exec '
                    f'-cp . {os.path.basename(self.main_class_path).replace(".java", "")} '
                    f'"{test_file}"'
                )

                # Add additional files if any
                if self.additional_files:
                    java_command += f" {' '.join(self.additional_files)}"

                # Run Java command
                subprocess.run(java_command, shell=True, check=True, cwd=working_dir)

            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Error during fuzzing: {str(e)}")
                fuzzing_successful = False

        # Generate JaCoCo report
        jacoco_command = (
            f'java -jar "{jacoco_cli_jar}" report jacoco.exec '
            f'--classfiles {working_dir} --sourcefiles {working_dir} '
            f'--html coverage-report'
        )

        try:
            subprocess.run(jacoco_command, shell=True, check=True, cwd=working_dir)
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Warning", f"Error generating coverage report: {str(e)}")
            fuzzing_successful = False

        # Generate dynamic analysis report
        report_path = analyzer.generate_report(working_dir)

        if fuzzing_successful:
            QMessageBox.information(self, "Success", 
                                "Fuzzing & Analysis Completed!\n"
                                f"Coverage report: {os.path.join(working_dir, 'coverage-report')}\n"
                                f"Analysis report: {report_path}")

    def run_analysis(self):
        """Run code analysis using SpotBugs"""
        if not self.main_class_path:
            QMessageBox.critical(self, "Error", "Please select a main class first!")
            return

        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        tools_dir = os.path.join(current_script_dir, "tools")
        spotbugs_jar = os.path.join(tools_dir, "spotbugs/spotbugs.jar")

        working_dir = os.path.dirname(self.main_class_path)
        main_class = self.main_class_path.replace('.java', '.class')
        
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = os.path.join(working_dir, f"analysis_result_{timestamp}.txt")
        
        # Construct SpotBugs command
        analyze_command = f'java -jar "{spotbugs_jar}" -textui "{main_class}"'
        
        try:
            # Run analysis and capture output
            result = subprocess.run(analyze_command, shell=True, capture_output=True, text=True, cwd=working_dir)
            
            # Save results to file
            with open(result_file, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\nErrors:\n" + result.stderr)
            
            QMessageBox.information(self, "Success", 
                                f"Analysis completed!\nResults saved to: {result_file}")
            
            # Optionally update generated files list
            self.update_generated_files_list(working_dir)

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Error during analysis: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = TestCaseGenerator()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()