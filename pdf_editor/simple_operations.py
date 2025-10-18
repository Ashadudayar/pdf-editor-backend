import fitz  # PyMuPDF
import os
from datetime import datetime
from django.conf import settings


class SimplePDFEditor:
    """Simple PDF operations using PyMuPDF"""
    
    def __init__(self):
        # Ensure output directories exist
        self.output_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs', 'edited')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def merge_pdfs(self, pdf_paths):
        """
        Merge multiple PDFs into one
        
        Args:
            pdf_paths: List of paths to PDF files
            
        Returns:
            str: Path to merged PDF
        """
        try:
            result = fitz.open()
            
            for pdf_path in pdf_paths:
                print(f"  📄 Opening: {pdf_path}")
                pdf = fitz.open(pdf_path)
                result.insert_pdf(pdf)
                pdf.close()
            
            # Save merged PDF
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"merged_{timestamp}.pdf"
            output_path = os.path.join(self.output_dir, output_filename)
            
            result.save(output_path)
            result.close()
            
            print(f"✅ Merged {len(pdf_paths)} PDFs into: {output_filename}")
            return output_path
            
        except Exception as e:
            print(f"❌ Merge error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def find_and_replace(self, input_path, find_text, replace_text):
        """
        Find and replace text in PDF
        
        Args:
            input_path: Path to input PDF
            find_text: Text to find
            replace_text: Text to replace with
            
        Returns:
            str: Path to edited PDF
        """
        try:
            pdf = fitz.open(input_path)
            replacements = 0
            
            for page in pdf:
                # Search for text
                text_instances = page.search_for(find_text)
                
                for inst in text_instances:
                    # Add redaction annotation
                    page.add_redact_annot(inst, replace_text)
                    replacements += 1
                
                # Apply redactions
                page.apply_redactions()
            
            if replacements > 0:
                # Save edited PDF
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = os.path.basename(input_path)
                name_without_ext = os.path.splitext(filename)[0]
                output_filename = f"{name_without_ext}_{timestamp}_edited.pdf"
                output_path = os.path.join(self.output_dir, output_filename)
                
                pdf.save(output_path)
                pdf.close()
                
                print(f"✅ Replaced {replacements} instance(s). Saved: {output_filename}")
                return output_path
            else:
                pdf.close()
                print(f"⚠️ Text '{find_text}' not found in PDF")
                return None
                
        except Exception as e:
            print(f"❌ Find/Replace error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def split_pdf(self, input_path, mode='all', start_page=None, end_page=None, pages_list=None):
        """
        Split PDF into multiple files
        
        Args:
            input_path: Path to input PDF
            mode: 'all', 'range', or 'extract'
            start_page: Start page number (1-indexed)
            end_page: End page number (1-indexed)
            pages_list: List of page numbers to extract
            
        Returns:
            list: Paths to split PDF files
        """
        try:
            pdf = fitz.open(input_path)
            output_files = []
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if mode == 'all':
                # Split into individual pages
                for page_num in range(len(pdf)):
                    new_pdf = fitz.open()
                    new_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)
                    
                    output_filename = f"page_{page_num + 1}_{timestamp}.pdf"
                    output_path = os.path.join(self.output_dir, output_filename)
                    
                    new_pdf.save(output_path)
                    new_pdf.close()
                    output_files.append(output_path)
                    
            elif mode == 'range' and start_page and end_page:
                # Extract page range
                new_pdf = fitz.open()
                new_pdf.insert_pdf(pdf, from_page=start_page-1, to_page=end_page-1)
                
                output_filename = f"pages_{start_page}-{end_page}_{timestamp}.pdf"
                output_path = os.path.join(self.output_dir, output_filename)
                
                new_pdf.save(output_path)
                new_pdf.close()
                output_files.append(output_path)
                
            elif mode == 'extract' and pages_list:
                # Extract specific pages
                new_pdf = fitz.open()
                for page_num in pages_list:
                    new_pdf.insert_pdf(pdf, from_page=page_num-1, to_page=page_num-1)
                
                output_filename = f"extracted_{timestamp}.pdf"
                output_path = os.path.join(self.output_dir, output_filename)
                
                new_pdf.save(output_path)
                new_pdf.close()
                output_files.append(output_path)
            
            pdf.close()
            print(f"✅ Split complete. Created {len(output_files)} file(s)")
            return output_files
            
        except Exception as e:
            print(f"❌ Split error: {str(e)}")
            import traceback
            traceback.print_exc()
            return []