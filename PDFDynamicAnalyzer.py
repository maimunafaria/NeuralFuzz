import psutil
import time
from datetime import datetime

class PDFDynamicAnalyzer:
    def __init__(self):
        self.issues = []
        self.start_time = None
        self.memory_snapshots = []
        
    def start_analysis(self):
        self.start_time = time.time()
        self.issues.clear()
        self.memory_snapshots.clear()
        
    def check_pdf_structure(self, line, line_number):
        # Memory usage snapshot
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.memory_snapshots.append(current_memory)
        
        # Stream length check
        if "stream" in line:
            if "Length" in line:
                try:
                    declared_length = int(line.split("Length")[1].split()[0])
                    # Store for later validation with actual stream
                    self.current_stream_length = declared_length
                except:
                    self.issues.append(f"Invalid stream length declaration at line {line_number}")
        
        # Dictionary marker matching
        if "<<" in line or ">>" in line:
            open_count = line.count("<<")
            close_count = line.count(">>")
            if open_count != close_count:
                self.issues.append(f"Unmatched dictionary markers at line {line_number}")
        
        # Object reference validation
        if " R" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "R" and i >= 2:
                    try:
                        obj_num = int(parts[i-2])
                        gen_num = int(parts[i-1])
                        if obj_num <= 0:
                            self.issues.append(f"Invalid object number in reference at line {line_number}")
                    except:
                        self.issues.append(f"Malformed object reference at line {line_number}")
        
        # Memory leak detection (threshold: 1GB)
        if current_memory > 1000:  # 1GB
            self.issues.append(f"Potential memory leak detected at line {line_number}")

    def generate_report(self, output_dir):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{output_dir}/pdf_dynamic_analysis_{timestamp}.txt"
        
        with open(report_path, 'w') as f:
            f.write("PDF Dynamic Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("Memory Usage Analysis:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Peak Memory Usage: {max(self.memory_snapshots):.2f} MB\n")
            f.write(f"Average Memory Usage: {sum(self.memory_snapshots)/len(self.memory_snapshots):.2f} MB\n\n")
            
            f.write("Found Issues:\n")
            f.write("-" * 30 + "\n")
            if self.issues:
                for issue in self.issues:
                    f.write(f"- {issue}\n")
            else:
                f.write("No issues found.\n")
        
        return report_path