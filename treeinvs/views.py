from django.shortcuts import render
from django.contrib import messages # add this
from .utils import loadcsv

def etl(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        try:
            # Call the utility function
            added, skipped = loadcsv(csv_file)
            messages.success(request, f"Import Complete: {added} trees saved, {skipped} rows skipped due to missing data.")
        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
            
    return render(request, 'treeinvs/etl.html')