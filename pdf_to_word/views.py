from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import fitz
from docx import Document
import io
# Create your views here.

@login_required
def pdf_to_word(request):
    if request.method == 'POST' and 'pdf_file' in request.FILES:
        pdf_file = request.FILES['pdf_file']

        #Procesar el archivo PDF
        text_content = extract_text(pdf_file)

    #Crear el documento Word y agregar el contenido extraido
        document = Document()
        document.add_paragraph(text_content)

    #Guardar el documento Word en memoria
        output_docx = io.BytesIO()
        document.save(output_docx)

    #Crear una respuesta HTTP con el archivo docx
        responce = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        responce['Content-Disposition'] = 'attachment; filename=output.docx'
        output_docx.seek(0)
        responce.write(output_docx.read())

        return responce
    
    return render(request, 'pdf_to_word.html')

def extract_text(pdf_file):
    #Utiliza PyMuPDF para extraer texto del PDF
    pdf_document = fitz.open(stream=pdf_file.read(), filetype='pdf')
    text_content = ''

    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text_content += page.get_text()

    return text_content