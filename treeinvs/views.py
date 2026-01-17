from django.shortcuts import render
from django.contrib import messages # add this
from .utils import loadcsv

from django.core.serializers import serialize
from django.http import HttpResponse
from .models import TreeInventory

import csv
from django.http import HttpResponse
from .models import TreeInventory

def import_tree_csv(request):
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

def export_trees_csv(request):
    # 1. Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tree_inventory_export.csv"'

    writer = csv.writer(response)
    
    # 2. Write the Header Row
    writer.writerow([
        'OBJECTID', 'TREE_ID', 'SPECIES_NAME', 'DBH', 
        'HEIGHT', 'SPREAD', 'ROAD_NAME', 'EASTING', 
        'NORTHING', 'IMPORT_DATE'
    ])

    # 3. Write Data Rows
    # Use .values_list() for better performance with large datasets
    trees = TreeInventory.objects.all().values_list(
        'objectid', 'tree_id', 'species_name', 'dbh', 
        'height', 'spread', 'road_name', 'easting', 
        'northing', 'import_date'
    )

    for tree in trees:
        writer.writerow(tree)

    return response


def tree_map_view(request):
    """Renders the main map page"""
    return render(request, 'treeinv/map.html')

def tree_data(request):
    """Returns the tree points as GeoJSON for the map"""
    trees = TreeInventory.objects.all()
    geojson = serialize('geojson', trees, geometry_field='geometry', fields=('tree_id', 'species_name', 'dbh'))
    return HttpResponse(geojson, content_type='application/json')