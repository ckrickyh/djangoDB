# # Register your models here.
# from django.contrib.gis import admin
# from .models import TreeInventory
# from leaflet.admin import LeafletGeoAdmin
# class TreeInventoryAdmin(admin.GISModelAdmin):
#     list_display = ('tree_id', 'species_name', 'dbh', 'height', 'import_date')
    
#     list_filter = ('species_name', 'import_date')
    
#     search_fields = ('tree_id', 'species_name', 'road_name')

    
#     # 4. Map settings (Optional but helpful)
#     # Default to OpenStreetMap for the geometry field widget
#     gis_widget_kwargs = {
#         'attrs': {
#             'default_zoom': 12,
#             'default_lon': 114.1694, # Center of HK
#             'default_lat': 22.3193,
#         }
#     }

#     list_per_page = 50

# admin.site.register(TreeInventory, TreeInventoryAdmin)


from django.contrib import admin # Use standard admin here
from leaflet.admin import LeafletGeoAdmin
from .models import TreeInventory

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.contrib.gis.geos import Point

# class TreeInventoryAdmin(LeafletGeoAdmin): # Changed inheritance here

#     # 1. Fields to display in the list view
#     list_display = ('tree_id', 'species_name', 'dbh', 'height', 'import_date')
#     # 2. Add filters on the right sidebar
#     list_filter = ('species_name', 'import_date')
#     # 3. Add a search bar
#     search_fields = ('tree_id', 'species_name', 'road_name')
#     # 4. Pagination
#     list_per_page = 50
#     # This CSS hides the overlay checkbox so users can't turn off labels
#     class Media:
#             css = {
#                 'all': ('css/hide_leaflet_selector.css',)
#             }


class TreeInventoryResource(resources.ModelResource):
    class Meta:
        model = TreeInventory
        import_id_fields = ('objectid',) # Unique identifier for updates
        # Optional: define exactly which fields to import
        fields = ('objectid', 'tree_id', 'species_name', 'dbh', 'height', 'road_name', 'easting', 'northing')

    def before_save_instance(self, instance, using_transactions, dry_run):
        """
        Convert Easting/Northing columns into a Geometry Point during import
        """
        if instance.easting and instance.northing:
            try:
                # Create point (Using HK 1980 Grid SRID 2326)
                pnt = Point(float(instance.easting), float(instance.northing), srid=2326)
                
                # Transform to WGS84 (SRID 4326) for the Leaflet Map
                pnt.transform(4326)
                
                instance.geometry = pnt
            except Exception as e:
                print(f"Error transforming coordinates for tree {instance.tree_id}: {e}")
        return instance

# 2. The Admin handles the Interface (Buttons + Map)
class TreeInventoryAdmin(ImportExportModelAdmin, LeafletGeoAdmin):
    resource_class = TreeInventoryResource
    list_display = ('tree_id', 'species_name', 'dbh', 'height', 'import_date')
    list_filter = ('species_name', 'import_date')
    search_fields = ('tree_id', 'species_name', 'road_name')
    list_per_page = 50

    class Media:
        css = {
            'all': ('css/hide_leaflet_selector.css',)
        }

# Register the model
admin.site.register(TreeInventory, TreeInventoryAdmin)