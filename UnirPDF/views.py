from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import PyPDF2
import os

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET': 
        return render(request, 'signup.html', {
            'form': UserCreationForm()
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('join_PDFs')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form' : UserCreationForm(),
                    'error': "El usuario ya existe"
                })
            
        return render(request, 'signup.html', {
            'form': UserCreationForm(),
            'error': 'Las contraseñas no coinciden'
        })
    
@login_required
def signout(request):
    logout(request)
    return redirect("home")

def signin(request):
    if request.method == 'GET':
        return render(request, "signin.html" ,{
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, "signin.html" ,{
            'error': 'Usuario o Contraseña Incorrectos'
        })
        else:
            login(request, user)
            return redirect('join_PDFs')
        
@login_required
def join_PDF(request):

    #Verifica que vengan ambos PDF en la respuesta del formulario
    if request.method == 'POST' and 'pdf_file1' in request.FILES and 'pdf_file2' in request.FILES:
        pdf_file1 = request.FILES['pdf_file1']
        pdf_file2 = request.FILES['pdf_file2']

        # Guardar los PDF en el servidor
        pdf_path1 = f'Archivos/{pdf_file1.name}'
        pdf_path2 = f'Archivos/{pdf_file2.name}'

        #Se cargan los archivos
        with open(pdf_path1, 'wb') as destino:
            for chunk in pdf_file1.chunks():
                destino.write(chunk)

        with open(pdf_path2, 'wb') as destino:
            for chunk in pdf_file2.chunks():
                destino.write(chunk)

        # Unir los archivos PDF
        merged_pdf_path = f'Archivos/merged_pdf.pdf'
        pdf_writer = PyPDF2.PdfWriter()

        with open(pdf_path1, 'rb') as pdf_file1, open(pdf_path2, 'rb') as pdf_file2:
            pdf_reader1 = PyPDF2.PdfReader(pdf_file1)
            pdf_reader2 = PyPDF2.PdfReader(pdf_file2)

            for page_num in range(len(pdf_reader1.pages)):
                page = pdf_reader1.pages[page_num]
                #Añade todas las paginas de X.PDF al nuevo PDF
                pdf_writer.add_page(page)

            for page_num in range(len(pdf_reader2.pages)):
                page = pdf_reader2.pages[page_num]
                pdf_writer.add_page(page)

        # Eliminar los archivos PDF individuales en el servidor
        os.remove(pdf_path1)
        os.remove(pdf_path2)

        with open(merged_pdf_path, 'wb') as merged_pdf:
            pdf_writer.write(merged_pdf)

        # Devolver el archivo PDF unido al usuario
        with open(merged_pdf_path, 'rb') as merged_pdf:
            response = HttpResponse(merged_pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(merged_pdf_path)}"'
            return response
        
    return render(request, 'join_pdfs.html')
