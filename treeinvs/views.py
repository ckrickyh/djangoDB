from django.shortcuts import render, redirect
from django.contrib import messages # add this
from .utils import loadcsv

from django.core.serializers import serialize
from django.http import HttpResponse
from .models import TreeInventory, TreePhotoUrl

import csv
from django.http import StreamingHttpResponse
from datetime import datetime

from django.http import StreamingHttpResponse
from django.contrib.gis.db.models.functions import Transform
from django.db.models import Func, F
from django.db import models

from django.contrib.admin.views.main import ChangeList # Import this => For custom admin changelist view

from django.db import connection
import io

def import_tree_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        try:
        
            raw_size, added, skipped, num_missing, duplicatedRows = loadcsv(csv_file)

            if len(skipped) > 0:
                msg = f"Import Complete: {added}/{raw_size} trees saved, {num_missing} items skipped at row [{skipped}]. Duplicated Rows: {duplicatedRows}."
            else:
                msg = f"Import Complete: {added}/{raw_size} trees saved, no missing data. Duplicated Rows: {duplicatedRows}."
            
            messages.success(request, msg)

            # 2. DYNAMIC REDIRECT
            # If the request comes from the Admin URL, go back to Admin
            if 'admin' in request.path:
                return redirect('admin:treeinvs_treeinventory_changelist')
            
            # Otherwise, stay on your custom ETL page
            return render(request, 'treeinvs/etl.html')

        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
            if 'admin' in request.path:
                return redirect('admin:treeinvs_treeinventory_changelist')
            
    # Default return for GET requests
    return render(request, 'treeinvs/etl.html')

#=== CSV EXPORT VIEW ===#

# Define raw PostGIS coordinate extractors
class RawX(Func):
    function = 'ST_X'
    output_field = models.FloatField()

class RawY(Func):
    function = 'ST_Y'
    output_field = models.FloatField()

class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        return value

def export_trees_csv(request):
    # 0. Clean the parameters to handle the 'list' issue
    params = request.GET.copy()
    for key in params:
        # Some filters might pass a list, we take the first item
        if isinstance(params[key], list):
            params[key] = params[key][0]

    # 1. Get the base queryset
    queryset = TreeInventory.objects.all()

    # 2. Apply Admin Filters from the URL
    for key, value in params.items():
        if key not in ['page', 'o', 'ot'] and value: # Only filter if value exists
            try:
                queryset = queryset.filter(**{key: value})
            except Exception:
                # Skip invalid filters to prevent crashing the export
                continue

    # 3. Annotate with transformed coordinates
    # FIX: Call .annotate directly on the queryset
    trees = queryset.annotate(
        geom_2326=Transform('geometry', 2326),
        geom_4326=Transform('geometry', 4326),
    ).annotate(
        hk_e=RawX(F('geom_2326')),
        hk_n=RawY(F('geom_2326')),
        wgs_lat=RawY(F('geom_4326')),
        wgs_lon=RawX(F('geom_4326'))
    ).values_list(
        'tree_id', 'species_name', 'dbh', 'height', 
        'hk_e', 'hk_n', 'wgs_lat', 'wgs_lon'
    ).order_by('tree_id').iterator(chunk_size=5000)

    # 4. Generator
    def csv_generator():
        echo = Echo()
        writer = csv.writer(echo)
        
        yield writer.writerow([
            'Tree ID', 'Species', 'DBH (mm)', 'Height (m)', 
            'HK80_Easting', 'HK80_Northing', 'WGS84_Latitude', 'WGS84_Longitude'
        ])
        
        for tree in trees:
            yield writer.writerow(tree)

    # 5. Response
    response = StreamingHttpResponse(csv_generator(), content_type='text/csv')
    filename = f"treeInventoryExport_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# === import tree photo ===
def import_tree_photos(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, "No file uploaded")
            return redirect('treeinvs:importCsv')

        try:
            # 1. Access the raw cursor from Django's connection
            with connection.cursor() as cursor:
                # 2. Get the underlying psycopg2 cursor
                # In Django, cursor.cursor is the actual psycopg2 object
                raw_cursor = cursor.cursor
                
                # 3. Handle the file upload
                # We wrap the uploaded file in a TextIOWrapper to ensure it's readable by copy_expert
                content = csv_file.read().decode('utf-8')
                csv_data = io.StringIO(content)
                
                # 4. Execute the High-Speed COPY
                # Note: 'tree_tag_id' is the column name Django creates for your ForeignKey
                sql = """
                    COPY treeinvs_treephotourl (tree_tag_id, url) 
                    FROM STDIN WITH CSV HEADER DELIMITER ','
                """
                raw_cursor.copy_expert(sql, csv_data)
                
            messages.success(request, "Fast bulk import completed successfully!")
            
        except Exception as e:
            messages.error(request, f"Database Error: {e}")
            
        return redirect('treeinvs:importCsv')

    return redirect('treeinvs:importCsv')

# === other  ===
def tree_map_view(request):
    """Renders the main map page"""
    return render(request, 'treeinv/map.html')

def tree_data(request):
    """Returns the tree points as GeoJSON for the map"""
    trees = TreeInventory.objects.all()
    geojson = serialize('geojson', trees, geometry_field='geometry', fields=('tree_id', 'species_name', 'dbh'))
    return HttpResponse(geojson, content_type='application/json')