from django.shortcuts import render
from .algorithm import main

# Create your views here.
def file_picker(request):
    return render(request, "filepicker.html", {})

def cluster(request):
    clusters = main("../books.csv", "title")
    context_dict = {
        "clusters": clusters
    }
    return render(request, "cluster.html", context_dict)