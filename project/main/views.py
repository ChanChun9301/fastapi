import requests
from django.shortcuts import render

FASTAPI_URL = "http://localhost:8000"  # адрес твоего FastAPI сервиса

def course_list(request):
    response = requests.get(f"{FASTAPI_URL}/courses/")
    courses = response.json()
    return render(request, "list.html", {"courses": courses})

def course_detail(request, course_id):
    response = requests.get(f"{FASTAPI_URL}/courses/{course_id}")
    course = response.json()
    return render(request, "detail.html", {"course": course})

def index(request):
    context = {
        
    }
    return render(request,'index.html',context)