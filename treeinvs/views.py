from django.shortcuts import render
from django.contrib import messages # add this
from .utils import loadcsv

def etl(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        try:
            # Call the utility function
            raw_size, added, skipped, num_missing = loadcsv(csv_file)

            if (len(skipped) > 0):
                messages.success(request, f"Import Complete: {added}/{raw_size} trees saved, {num_missing} items at row [{skipped}] skipped due to missing data.")
            else:
                messages.success(request, f"Import Complete: {added}/{raw_size} trees saved, no missing data.")

        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
            
    return render(request, 'treeinvs/etl.html')