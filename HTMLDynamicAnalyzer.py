import psutil
import time
from datetime import datetime


class HTMLDynamicAnalyzer:
    def __init__(self):
        self.issues = []
        self.tag_stack = []
        self.ids = set()
        self.start_time = None
        
    def start_analysis(self):
        self.start_time = time.time()
        self.issues.clear()
        self.tag_stack.clear()
        self.ids.clear()
        
    def check_html_structure(self, line, line_number):
        # Check for opening tags
        opening_tags = self._find_tags(line, "<", ">")
        for tag in opening_tags:
            if not tag.startswith("/"):  # Opening tag
                self.tag_stack.append((tag.split()[0], line_number))
                
                # Check for duplicate IDs
                if 'id="' in tag:
                    id_value = tag.split('id="')[1].split('"')[0]
                    if id_value in self.ids:
                        self.issues.append(f"Duplicate ID '{id_value}' found at line {line_number}")
                    self.ids.add(id_value)
        
        # Check for closing tags
        closing_tags = self._find_tags(line, "</", ">")
        for tag in closing_tags:
            tag = tag.strip("/")
            if self.tag_stack:
                last_tag, last_line = self.tag_stack[-1]
                if tag == last_tag:
                    self.tag_stack.pop()
                else:
                    self.issues.append(f"Mismatched tags: Expected {last_tag} but found {tag} at line {line_number}")
            else:
                self.issues.append(f"Unexpected closing tag {tag} at line {line_number}")
        
        # Check for DOCTYPE
        if line_number == 1 and not "<!DOCTYPE" in line.upper():
            self.issues.append("Missing DOCTYPE declaration")
        
        # Check for required elements
        if line_number == len(line):  # Last line
            if not any("</body>" in l for l in line):
                self.issues.append("Missing </body> tag")
            if not any("</html>" in l for l in line):
                self.issues.append("Missing </html> tag")

    def _find_tags(self, line, start_marker, end_marker):
        tags = []
        start = 0
        while True:
            start_idx = line.find(start_marker, start)
            if start_idx == -1:
                break
            end_idx = line.find(end_marker, start_idx)
            if end_idx == -1:
                break
            tag = line[start_idx + len(start_marker):end_idx].strip()
            tags.append(tag)
            start = end_idx + 1
        return tags

    def generate_report(self, output_dir):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{output_dir}/html_dynamic_analysis_{timestamp}.txt"
        
        with open(report_path, 'w') as f:
            f.write("HTML Dynamic Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            
            # Report unclosed tags
            if self.tag_stack:
                f.write("Unclosed Tags:\n")
                f.write("-" * 30 + "\n")
                for tag, line_number in self.tag_stack:
                    f.write(f"- {tag} opened at line {line_number} was never closed\n")
                f.write("\n")
            
            # Report other issues
            f.write("Found Issues:\n")
            f.write("-" * 30 + "\n")
            if self.issues:
                for issue in self.issues:
                    f.write(f"- {issue}\n")
            else:
                f.write("No issues found.\n")
        
        return report_path