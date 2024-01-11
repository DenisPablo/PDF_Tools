from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import PyPDF2
import os
# Create your views here.

@login_required
def cut_pdf(request):
    if request.method == 'POST' and 'pdf_file' in request.FILES:
        pdf_file = request.FILES['pdf_file']

        #Obtener el rango de paginas a recortar
        start_page = int(request.POST.get('start_page',1))
        end_page = int(request.POST.get('end_page', 1))

        #Validar el rango de paginas
        if start_page < 1 or end_page < start_page:
            return render(request, 'cut_pdf.html', {
                'error': 'El rango seleccionado no es valido'
            })
        
        #Procesar el archivo PDF
        pdf_path = f'Archivos/{pdf_file.name}'
        with open(pdf_path, 'wb') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
    
        #Recortar las paginas del PDF
        cropped_pdf_path = f'Archivos/cropped_pdf.pdf'
        pdf_writer = PyPDF2.PdfWriter()

        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            for page_num in range(start_page - 1, min(end_page, len(pdf_reader.pages))):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)

        # Cerrar el objeto PdfWriter y escribir en el archivo recortado
        with open(cropped_pdf_path, 'wb') as cropped_pdf_file:
            pdf_writer.write(cropped_pdf_file)

        #Elimina el archivo PDF original en el servidor
        os.remove(pdf_path)

        #Guardar el nuevo PDF recortado
        with open(cropped_pdf_path, 'rb') as cropped_pdf:
            responce = HttpResponse(cropped_pdf.read(), content_type='application/pdf')
            responce['Content-Disposition'] = f'attachment; filename={os.path.basename(cropped_pdf_path)}'
            os.remove(cropped_pdf_path)
            return responce
        
    return render(request,'cut_pdf.html')