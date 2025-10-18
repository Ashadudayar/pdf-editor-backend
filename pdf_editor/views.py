from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.http import FileResponse
from django.http import HttpResponse
from django.conf import settings
from .models import PDFDocument
from .serializers import PDFDocumentSerializer
from .simple_operations import SimplePDFEditor
import os
import fitz  
from datetime import datetime
from django.core.files import File


class PDFDocumentViewSet(viewsets.ModelViewSet):
    queryset = PDFDocument.objects.all()
    serializer_class = PDFDocumentSerializer
    
    def create(self, request):
        """Upload PDF"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)
        
        print(f"📤 Uploading: {file.name}")
        
        document = PDFDocument.objects.create(
            title=file.name,
            original_file=file
        )
        
        serializer = self.get_serializer(document, context={'request': request})
        return Response(serializer.data, status=201)
    
    @action(detail=True, methods=['get'])
    def page_count(self, request, pk=None):
        """Get the number of pages in a PDF"""
        try:
            document = self.get_object()
            pdf_path = document.original_file.path
            
            pdf_doc = fitz.open(pdf_path)
            count = len(pdf_doc)
            pdf_doc.close()
            
            print(f"📄 Page count: {count}")
            
            return Response({'page_count': count}, status=200)
            
        except Exception as e:
            print(f"❌ Error getting page count: {str(e)}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def split_range(self, request, pk=None):
        """Extract a range of pages from PDF"""
        try:
            document = self.get_object()
            start_page = int(request.data.get('start_page', 1))
            end_page = int(request.data.get('end_page', 1))
            
            print(f"✂️ Splitting pages {start_page}-{end_page}")
            
            input_path = document.original_file.path
            pdf_doc = fitz.open(input_path)
            
            # Validate page range
            if start_page < 1 or end_page > len(pdf_doc) or start_page > end_page:
                pdf_doc.close()
                return Response({
                    'error': f'Invalid page range. Document has {len(pdf_doc)} pages.'
                }, status=400)
            
            # Create new PDF with selected pages (pages are 0-indexed)
            new_pdf = fitz.open()
            new_pdf.insert_pdf(pdf_doc, from_page=start_page-1, to_page=end_page-1)
            
            # Save
            output_filename = f"pages_{start_page}-{end_page}.pdf"
            output_relative_path = os.path.join('pdfs', 'split', output_filename)
            output_absolute_path = os.path.join(settings.MEDIA_ROOT, output_relative_path)
            
            os.makedirs(os.path.dirname(output_absolute_path), exist_ok=True)
            
            new_pdf.save(output_absolute_path)
            new_pdf.close()
            pdf_doc.close()
            
            print(f"✅ Split file saved")
            
            return Response({
                'message': f'Extracted pages {start_page}-{end_page}',
                'split_file': f'/media/{output_relative_path}'
            }, status=200)
            
        except Exception as e:
            import traceback
            print(f"❌ Error: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def extract_pages(self, request, pk=None):
        """Extract specific pages from PDF"""
        try:
            document = self.get_object()
            pages = request.data.get('pages', [])
            
            if not pages:
                return Response({'error': 'Please provide page numbers'}, status=400)
            
            print(f"✂️ Extracting pages: {pages}")
            
            input_path = document.original_file.path
            pdf_doc = fitz.open(input_path)
            
            # Validate pages
            max_pages = len(pdf_doc)
            invalid_pages = [p for p in pages if p < 1 or p > max_pages]
            if invalid_pages:
                pdf_doc.close()
                return Response({
                    'error': f'Invalid pages: {invalid_pages}. Document has {max_pages} pages.'
                }, status=400)
            
            # Create new PDF with selected pages
            new_pdf = fitz.open()
            for page_num in pages:
                new_pdf.insert_pdf(pdf_doc, from_page=page_num-1, to_page=page_num-1)
            
            # Save
            output_filename = f"extracted_pages.pdf"
            output_relative_path = os.path.join('pdfs', 'split', output_filename)
            output_absolute_path = os.path.join(settings.MEDIA_ROOT, output_relative_path)
            
            os.makedirs(os.path.dirname(output_absolute_path), exist_ok=True)
            
            new_pdf.save(output_absolute_path)
            new_pdf.close()
            pdf_doc.close()
            
            print(f"✅ Extracted {len(pages)} pages")
            
            return Response({
                'message': f'Extracted {len(pages)} pages',
                'extracted_file': f'/media/{output_relative_path}'
            }, status=200)
            
        except Exception as e:
            import traceback
            print(f"❌ Error: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def split_all(self, request, pk=None):
        """Split PDF into individual pages"""
        try:
            document = self.get_object()
            
            print(f"✂️ Splitting into individual pages")
            
            input_path = document.original_file.path
            pdf_doc = fitz.open(input_path)
            
            file_paths = []
            
            # Create separate PDF for each page
            for page_num in range(len(pdf_doc)):
                new_pdf = fitz.open()
                new_pdf.insert_pdf(pdf_doc, from_page=page_num, to_page=page_num)
                
                output_filename = f"page_{page_num + 1}.pdf"
                output_relative_path = os.path.join('pdfs', 'split', output_filename)
                output_absolute_path = os.path.join(settings.MEDIA_ROOT, output_relative_path)
                
                os.makedirs(os.path.dirname(output_absolute_path), exist_ok=True)
                
                new_pdf.save(output_absolute_path)
                new_pdf.close()
                
                file_paths.append(f'/media/{output_relative_path}')
            
            pdf_doc.close()
            
            print(f"✅ Split into {len(file_paths)} files")
            
            return Response({
                'message': f'Split into {len(file_paths)} files',
                'files': file_paths,
                'count': len(file_paths)
            }, status=200)
            
        except Exception as e:
            import traceback
            print(f"❌ Error: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'], url_path='find_replace')
    def find_replace(self, request, pk=None):
        """Find and replace text"""
        document = self.get_object()
        find_text = request.data.get('find_text', '')
        replace_text = request.data.get('replace_text', '')
        
        if not find_text:
            return Response({'error': 'Please provide text to find'}, status=400)
        
        try:
            input_path = document.original_file.path
            original_name = os.path.basename(input_path)
            name_without_ext = os.path.splitext(original_name)[0]
            output_filename = f"{name_without_ext}_edited.pdf"
            
            output_relative_path = os.path.join('pdfs', 'edited', output_filename)
            output_absolute_path = os.path.join(settings.MEDIA_ROOT, output_relative_path)
            os.makedirs(os.path.dirname(output_absolute_path), exist_ok=True)
            
            print(f"🔍 Find: '{find_text}' | Replace: '{replace_text}'")
            
            pdf_document = fitz.open(input_path)
            replacements_made = 0
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text_instances = page.search_for(find_text)
                
                if text_instances:
                    for inst in text_instances:
                        page.add_redact_annot(inst, text=replace_text, fill=(1, 1, 1))
                        replacements_made += 1
                    page.apply_redactions()
            
            pdf_document.save(output_absolute_path)
            pdf_document.close()
            
            document.edited_file.name = output_relative_path
            document.save()
            
            print(f"✅ Replaced {replacements_made} instance(s)")
            
            serializer = self.get_serializer(document)
            return Response({
                'message': f'Successfully replaced {replacements_made} instance(s)',
                'replacements': replacements_made,
                **serializer.data
            }, status=200)
            
        except Exception as e:
            import traceback
            print(f"❌ Error: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """Download PDF"""
        try:
            document = self.get_object()
            
            if document.edited_file and document.edited_file.name:
                file_to_download = document.edited_file
            else:
                file_to_download = document.original_file
            
            file_path = file_to_download.path
            
            if not os.path.exists(file_path):
                return Response({'error': 'File not found'}, status=404)
            
            print(f"📥 Downloading: {file_path}")
            
            file_handle = open(file_path, 'rb')
            response = FileResponse(file_handle, as_attachment=True)
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            
            return response
            
        except Exception as e:
            import traceback
            print(f"❌ Download error: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': str(e)}, status=500)
    
    # Add this import at the top if not already there


# Add this new viewset method to your PDFDocumentViewSet class
    @action(detail=True, methods=['post'])
    def rotate(self, request, pk=None):
        """
        Rotate PDF pages
        Body: {
            "angle": 90,  # 90, 180, 270, or -90
            "pages": "all" or "1,3,5" or "1-5"
        }
        """
        document = self.get_object()
        angle = int(request.data.get('angle', 90))
        pages_input = request.data.get('pages', 'all')
        
        print(f"🔄 Rotating pages by {angle}° for document: {document.title}")
        
        try:
            # Open the PDF
            pdf = fitz.open(document.original_file.path)
            total_pages = len(pdf)
            
            # Determine which pages to rotate
            if pages_input.lower() == 'all':
                pages_to_rotate = list(range(total_pages))
                print(f"🔄 Rotating ALL {total_pages} pages")
            else:
                pages_to_rotate = []
                
                # Parse page numbers (e.g., "1,3,5" or "1-5")
                for part in pages_input.split(','):
                    part = part.strip()
                    if '-' in part:
                        # Handle range (e.g., "1-5")
                        start, end = map(int, part.split('-'))
                        pages_to_rotate.extend(range(start - 1, end))
                    else:
                        # Handle single page
                        pages_to_rotate.append(int(part) - 1)
                
                print(f"🔄 Rotating pages: {[p + 1 for p in pages_to_rotate]}")
            
            # Rotate the specified pages
            for page_num in pages_to_rotate:
                if 0 <= page_num < total_pages:
                    page = pdf[page_num]
                    page.set_rotation(angle)
                    print(f"  ✓ Rotated page {page_num + 1} by {angle}°")
            
            # Save the rotated PDF
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"rotated_{timestamp}.pdf"
            output_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', 'edited', output_filename)
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            pdf.save(output_path)
            pdf.close()
            
            # Create new document for rotated file
            with open(output_path, 'rb') as f:
                rotated_doc = PDFDocument.objects.create(
                    title=output_filename,
                    original_file=File(f, name=output_filename)
                )
            
            print(f"✅ Rotated PDF saved: {output_filename}")
            
            # Return download URL instead of media URL
            download_url = request.build_absolute_uri(
                f'/api/documents/{rotated_doc.id}/download/'
            )
            
            return Response({
                'message': f'Successfully rotated pages by {angle}°',
                'edited_file': download_url,
                'pages_rotated': len(pages_to_rotate),
                'document_id': str(rotated_doc.id)
            })
            
        except Exception as e:
            print(f"❌ Error rotating PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Failed to rotate PDF: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def debug_media(self, request):
        """Debug endpoint to check media configuration"""
        media_root = settings.MEDIA_ROOT
        media_url = settings.MEDIA_URL
        debug = settings.DEBUG
        
        # Check if media folder exists
        media_exists = os.path.exists(media_root)
        
        # List files in media/pdfs/edited if exists
        edited_path = os.path.join(media_root, 'pdfs', 'edited')
        files = []
        if os.path.exists(edited_path):
            files = os.listdir(edited_path)
        
        return Response({
            'MEDIA_ROOT': media_root,
            'MEDIA_URL': media_url,
            'DEBUG': debug,
            'media_folder_exists': media_exists,
            'edited_files': files,
            'edited_path': edited_path,
        })

    @action(detail=True, methods=['get'], url_path='download_original')
    def download_original(self, request, pk=None):
        """Download the original PDF file"""
        document = self.get_object()
        file_path = document.original_file.path
        
        print(f"📥 Downloading original: {file_path}")
        
        if os.path.exists(file_path):
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/pdf'
            )
            filename = os.path.basename(file_path)
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        else:
            print(f"❌ File not found: {file_path}")
            return Response({'error': 'File not found'}, status=404)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download the edited PDF file"""
        document = self.get_object()
        
        # Use edited file if exists, otherwise original
        if document.edited_file:
            file_path = document.edited_file.path
        else:
            file_path = document.original_file.path
        
        print(f"📥 Downloading edited: {file_path}")
        
        if os.path.exists(file_path):
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/pdf'
            )
            filename = os.path.basename(file_path)
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        else:
            print(f"❌ File not found: {file_path}")
            return Response({'error': 'File not found'}, status=404)

    @action(detail=False, methods=['post'])
    def merge(self, request):
        """Merge multiple PDF files"""
        document_ids = request.data.get('document_ids', [])
        
        if not document_ids or len(document_ids) < 2:
            return Response({
                'error': 'Please provide at least 2 documents to merge'
            }, status=400)
        
        print(f"🔗 Merging {len(document_ids)} PDFs")
        
        try:
            # Get all documents
            documents = PDFDocument.objects.filter(id__in=document_ids)
            
            if documents.count() != len(document_ids):
                return Response({
                    'error': 'Some documents not found'
                }, status=404)
            
            # Get file paths in the order provided
            pdf_paths = []
            for doc_id in document_ids:
                doc = documents.get(id=doc_id)
                pdf_paths.append(doc.original_file.path)
                print(f"  📄 Adding: {doc.title}")
            
            # Use SimplePDFEditor to merge
            editor = SimplePDFEditor()
            output_path = editor.merge_pdfs(pdf_paths)
            
            if output_path:
                # Create new document for merged PDF
                with open(output_path, 'rb') as f:
                    merged_doc = PDFDocument.objects.create(
                        title=f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        original_file=File(f, name=os.path.basename(output_path))
                    )
                
                print(f"✅ Merged PDF created: {merged_doc.title}")
                
                # Return download URL
                download_url = request.build_absolute_uri(
                    f'/api/documents/{merged_doc.id}/download/'
                )
                
                return Response({
                    'message': f'Successfully merged {len(document_ids)} PDFs',
                    'merged_file': download_url,
                    'document_id': str(merged_doc.id)
                })
            else:
                return Response({
                    'error': 'Failed to merge PDFs'
                }, status=500)
                
        except Exception as e:
            print(f"❌ Merge error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'])
    def split(self, request, pk=None):
        """Split PDF into multiple files or extract pages"""
        document = self.get_object()
        mode = request.data.get('mode', 'all')
        start_page = request.data.get('start_page')
        end_page = request.data.get('end_page')
        pages_str = request.data.get('pages', '')
        
        print(f"✂️ Split mode: {mode}")
        
        try:
            editor = SimplePDFEditor()
            
            if mode == 'range':
                # Page range mode
                output_files = editor.split_pdf(
                    document.original_file.path,
                    mode='range',
                    start_page=int(start_page),
                    end_page=int(end_page)
                )
            elif mode == 'extract':
                # Extract specific pages
                pages_list = [int(p.strip()) for p in pages_str.split(',') if p.strip()]
                output_files = editor.split_pdf(
                    document.original_file.path,
                    mode='extract',
                    pages_list=pages_list
                )
            else:
                # Split all pages
                output_files = editor.split_pdf(
                    document.original_file.path,
                    mode='all'
                )
            
            if output_files:
                # Create document records for each split file
                split_docs = []
                for file_path in output_files:
                    with open(file_path, 'rb') as f:
                        split_doc = PDFDocument.objects.create(
                            title=os.path.basename(file_path),
                            original_file=File(f, name=os.path.basename(file_path))
                        )
                        split_docs.append({
                            'id': str(split_doc.id),
                            'title': split_doc.title,
                            'download_url': request.build_absolute_uri(
                                f'/api/documents/{split_doc.id}/download/'
                            )
                        })
                
                print(f"✅ Split complete! Created {len(split_docs)} file(s)")
                
                return Response({
                    'message': f'Successfully split into {len(split_docs)} file(s)',
                    'files': split_docs
                })
            else:
                return Response({
                    'error': 'Failed to split PDF'
                }, status=500)
                
        except Exception as e:
            print(f"❌ Split error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=500)