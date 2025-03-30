from django.shortcuts import render
import requests
from django.http import JsonResponse
# Create your views here.

def getData(api_url):
    try:
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()        
            return data
        else:
            data = [{"id": "Error", "name": "Error"}]        
            return data
    
    except requests.exceptions.RequestException as e:
        return e


def Courses(request):
    api_url = "http://127.0.0.1:8080/api/courses/"
    courses = getData(api_url)
    #return JsonResponse(courses, safe=False)
    return render(request, "courses.html", {"courses": courses})

def Home(request):
    api_url1 = "http://127.0.0.1:8080/api/courses/"
    courses = getData(api_url1)
    api_url2 = "http://127.0.0.1:8080/api/lecturers/"
    lecturers = getData(api_url2)

    context = {
        "courses": courses,
        "lecturers": lecturers,
    }
    return render(request, "home.html", context)
    
    
