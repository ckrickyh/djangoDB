from django.shortcuts import render

def etl(request):
    return render(request, 'treeinvs/etl.html')