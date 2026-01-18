import re
import pdfplumber

class ResumeParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.text = self._extract_text()
    
    def _extract_text(self):
        text = ""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except:
            # Fallback to pdfminer3 if pdfplumber fails
            from pdfminer3.layout import LAParams
            from pdfminer3.pdfpage import PDFPage
            from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
            from pdfminer3.converter import TextConverter
            import io
            
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            
            with open(self.file_path, 'rb') as fh:
                for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                    page_interpreter.process_page(page)
                text = fake_file_handle.getvalue()
            
            converter.close()
            fake_file_handle.close()
        
        return text
    
    def get_extracted_data(self):
        name = self._extract_name()
        email = self._extract_email()
        mobile = self._extract_mobile()
        skills = self._extract_skills()
        pages = self._count_pages()
        
        return {
            'name': name or 'Unknown',
            'email': email or 'Not found',
            'mobile_number': mobile or 'Not found',
            'skills': skills,
            'no_of_pages': pages
        }
    
    def _extract_name(self):
        lines = self.text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 2 and len(line.split()) <= 4:
                if re.match(r'^[A-Za-z\s]+$', line) and not any(word in line.lower() for word in ['resume', 'cv', 'curriculum']):
                    return line
        return "Resume Holder"
    
    def _extract_email(self):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, self.text)
        return emails[0] if emails else None
    
    def _extract_mobile(self):
        phone_patterns = [
            r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+\d{1,3}\s?\d{10}',
            r'\d{10}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, self.text)
            if phones:
                return ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        return None
    
    def _extract_skills(self):
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'node', 'django', 'flask',
            'html', 'css', 'sql', 'mysql', 'postgresql', 'mongodb', 'git', 'docker',
            'kubernetes', 'aws', 'azure', 'machine learning', 'data science', 'tensorflow',
            'keras', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'c++', 'c#', 'php',
            'ruby', 'swift', 'kotlin', 'android', 'ios', 'flutter', 'react native',
            'vue', 'express', 'spring', 'hibernate', 'bootstrap', 'jquery', 'typescript'
        ]
        
        found_skills = []
        text_lower = self.text.lower()
        
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))[:10]
    
    def _count_pages(self):
        try:
            with pdfplumber.open(self.file_path) as pdf:
                return len(pdf.pages)
        except:
            from pdfminer3.pdfpage import PDFPage
            with open(self.file_path, 'rb') as fh:
                pages = list(PDFPage.get_pages(fh))
                return len(pages)