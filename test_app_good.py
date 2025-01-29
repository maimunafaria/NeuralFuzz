from datetime import datetime
import os
import re
import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QComboBox, QLabel, QLineEdit, QMessageBox,
                           QFileDialog, QListWidget, QHBoxLayout, QGridLayout,
                           QFrame, QProgressDialog)
from PyQt6.QtCore import QThread, pyqtSignal, QRunnable, QThreadPool, Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from HTMLDynamicAnalyzer import HTMLDynamicAnalyzer
from PDFDynamicAnalyzer import PDFDynamicAnalyzer
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QTabWidget, QTextEdit, QTableWidget, 
                           QTableWidgetItem)


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

class StyledButton(QPushButton):
    def __init__(self, text, color="#2196F3"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(color, 1.1)};
            }}
            QPushButton:pressed {{
                background-color: {self.adjust_color(color, 0.9)};
            }}
        """)

    def adjust_color(self, color, factor):
        # Convert hex to RGB, adjust, and convert back
        color = color.lstrip('#')
        r, g, b = [int(color[i:i+2], 16) for i in (0, 2, 4)]
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

class TestCaseGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Test Case Generator")
        self.setFixedSize(1200, 800)  
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 4px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #dddddd;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #2196F3;
                color: black;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #dddddd;
                border-radius: 4px;
                background-color: white;
                min-width: 150px;
                color: black;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #e0e0e0;
                selection-color: black;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #dddddd;
                border-radius: 4px;
                padding: 4px;
                color: black;
            }
            QListWidget::item {
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
                color: black;
            }
        """)

        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QGridLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.setCentralWidget(main_widget)

        # Initialize variables
        self.main_class_path = ""
        self.additional_files = []

        # Create layout sections
        self.create_source_selection_section(main_layout)
        self.create_test_generation_section(main_layout)
        self.create_action_section(main_layout)

    def create_source_selection_section(self, main_layout):
        # Create a frame for the section
        source_frame = QFrame()
        source_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        source_layout = QVBoxLayout(source_frame)
        source_layout.setSpacing(16)

        # Main class selection
        main_class_layout = QHBoxLayout()
        main_class_label = QLabel("Main Class:")
        self.main_class_entry = QLineEdit()
        select_main_btn = StyledButton("Browse", "#4CAF50")
        select_main_btn.clicked.connect(self.select_main_class)
        
        main_class_layout.addWidget(main_class_label)
        main_class_layout.addWidget(self.main_class_entry)
        main_class_layout.addWidget(select_main_btn)

        # Additional files section
        additional_files_label = QLabel("Additional Files:")
        self.additional_files_list = QListWidget()
        add_files_btn = StyledButton("Add Additional Files", "#4CAF50")
        add_files_btn.clicked.connect(self.select_additional_files)

        # Compile command section
        compile_layout = QHBoxLayout()
        compile_label = QLabel("Compile Command:")
        self.compile_command_entry = QLineEdit()
        self.compile_command_entry.setPlaceholderText("javac {selected_file}")
        compile_layout.addWidget(compile_label)
        compile_layout.addWidget(self.compile_command_entry)

        # Add all components to source layout
        source_layout.addLayout(main_class_layout)
        source_layout.addWidget(additional_files_label)
        source_layout.addWidget(self.additional_files_list)
        source_layout.addWidget(add_files_btn)
        source_layout.addLayout(compile_layout)

        # Add frame to main layout
        main_layout.addWidget(source_frame, 0, 0, 1, 2)
    def show_error_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: black;
                min-width: 300px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 6px 20px;
                border: none;
                border-radius: 4px;
            }
        """)
        msg.exec()
    def create_test_generation_section(self, main_layout):
        # Create a frame for the section
        test_frame = QFrame()
        test_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        test_layout = QVBoxLayout(test_frame)
        test_layout.setSpacing(16)

        # File type selection
        file_type_layout = QHBoxLayout()
        file_type_label = QLabel("File Type:")
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["HTML", "PDF"])
        file_type_layout.addWidget(file_type_label)
        file_type_layout.addWidget(self.file_type_combo)
        file_type_layout.addStretch()

        # Test case count
        test_case_layout = QHBoxLayout()
        test_case_label = QLabel("Number of Test Cases:")
        self.test_case_input = QLineEdit()
        test_case_layout.addWidget(test_case_label)
        test_case_layout.addWidget(self.test_case_input)
        test_case_layout.addStretch()

        # Generate button
        generate_btn = StyledButton("Generate Test Cases", "#2196F3")
        generate_btn.clicked.connect(self.generate_test_cases)

        # Add components to test layout
        test_layout.addLayout(file_type_layout)
        test_layout.addLayout(test_case_layout)
        test_layout.addWidget(generate_btn)
        test_layout.addStretch()

        # Add frame to main layout
        main_layout.addWidget(test_frame, 1, 0)

    def create_action_section(self, main_layout):
        # Create a frame for the section
        action_frame = QFrame()
        action_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        action_layout = QVBoxLayout(action_frame)
        action_layout.setSpacing(16)

        # Generated files list
        generated_files_label = QLabel("Generated Files:")
        self.generated_files_list = QListWidget()

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # Add spacing between buttons
        buttons = [
            ("Open Output Directory", "#607D8B", self.open_output_directory),
            ("Compile Software", "#FF9800", self.compile_software),
            ("Fuzz", "#9C27B0", self.run_fuzzing),
            ("Analyze", "#E91E63", self.run_analysis),
        ]

        for text, color, handler in buttons:
            btn = StyledButton(text, color)
            btn.clicked.connect(handler)
            btn.setFixedWidth(180)  # Fixed width for consistent button sizes
            button_layout.addWidget(btn)

        # Add components to action layout
        action_layout.addWidget(generated_files_label)
        action_layout.addWidget(self.generated_files_list)
        action_layout.addLayout(button_layout)

        # Add frame to main layout
        main_layout.addWidget(action_frame, 1, 1)

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
            self.show_error_message("In Progress", "Test case generation is already running.")
            return

        # Validate inputs
        try:
            count = int(self.test_case_input.text())
            if count <= 0:
                self.show_error_message("Error", "Please enter a positive number of test cases")
                return
        except ValueError:
            self.show_error_message( "Error", "Please enter a valid number of test cases")
            return

        # Validate main class is selected
        if not self.main_class_path:
            self.show_error_message( "Error", "Please select a main class first")
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
        self.show_error_message("Success", "Test cases generated successfully!")

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
        self.show_error_message(self, "Error", error_msg)

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
            self.show_error_message( "Warning", f"Directory not found: {source_dir}")
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
                self.show_error_message("Info", "No generated files found.")
        
        except Exception as e:
            self.show_error_message( "Error", f"Error listing files: {str(e)}")

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
               self.show_error_message("Error", f"File not found: {file_path}")
        except Exception as e:
            self.show_error_message("Error", f"Could not open file: {str(e)}")

    def open_output_directory(self):
        """
        Open the output directory based on the selected file type
        """
        # Determine the output directory based on file type
        if not self.main_class_path:
            self.show_error_message("Warning", "Please select a main class first")
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
            self.show_error_message("Error", f"Could not open directory: {str(e)}")


    def compile_software(self):
        """Compile the selected Java files"""
        # Validate main class selection
        if not self.main_class_path:
            self.show_error_message("Error", "Please select a main class first!")
            return

        # Get compile command
        compile_cmd = self.compile_command_entry.text().strip()
        if not compile_cmd:
            self.show_error_message("Error", "No compile command entered!")
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
            self.show_error_message("Success", "Compilation Successful!")
            
            # Enable fuzzing and analysis buttons
            # self.fuzzing_btn.setEnabled(True)
            # self.analysis_btn.setEnabled(True)

        except subprocess.CalledProcessError as e:
            self.show_error_message("Error", f"Compilation error: {str(e)}")
            
            # Disable fuzzing and analysis buttons
            # self.fuzzing_btn.setEnabled(False)
            # self.analysis_btn.setEnabled(False)

    def run_fuzzing(self):
        """Run fuzzing process"""
        if not self.main_class_path:
            self.show_error_message("Error", "Please select a main class first!")
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
            self.show_error_message("Error", f"Directory not found: {generated_dir}")
            return

        # Get test files
        test_files = [
            os.path.join(generated_dir, f) 
            for f in os.listdir(generated_dir) 
            if f.endswith(file_extension)
        ]

        if not test_files:
            self.show_error_message("Error", f"No {file_type} files found in the directory.")
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
                self.show_error_message("Warning", f"Error during fuzzing: {str(e)}")
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
            self.show_error_message( "Warning", f"Error generating coverage report: {str(e)}")
            fuzzing_successful = False

        # Generate dynamic analysis report
        report_path = analyzer.generate_report(working_dir)

        if fuzzing_successful:
            self.show_error_message( "Success", 
                                "Fuzzing & Analysis Completed!\n"
                                f"Coverage report: {os.path.join(working_dir, 'coverage-report')}\n"
                                f"Analysis report: {report_path}")

    def run_analysis(self):
        """Run code analysis using SpotBugs"""
        if not self.main_class_path:
            self.show_error_message("Error", "Please select a main class first!")
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
            
            self.show_error_message("Success", 
                                f"Analysis completed!\nResults saved to: {result_file}")
            
            # Optionally update generated files list
            self.update_generated_files_list(working_dir)

        except subprocess.CalledProcessError as e:
            self.show_error_message("Error", f"Error during analysis: {str(e)}")


def main():
    app = QApplication(sys.argv)
    # Set application-wide font
    app.setFont(QFont('Segoe UI', 10))
    window = TestCaseGenerator()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()