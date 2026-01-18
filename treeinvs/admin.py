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

from django.urls import path
from admin_numeric_filter.admin import NumericFilterModelAdmin, SliderNumericFilter
from .views import import_tree_csv

class BaseSliderFilter(SliderNumericFilter):
    MAX_DECIMALS = 0  # No decimals for whole numbers

    def queryset(self, request, queryset):
        # Extract values from the GET parameters manually to ensure they are floats, not lists
        val_from = request.GET.get(f'{self.parameter_name}_from')
        val_to = request.GET.get(f'{self.parameter_name}_to')

        if val_from and val_to:
            try:
                # Convert the strings to floats directly
                return queryset.filter(**{
                    f'{self.parameter_name}__range': (float(val_from), float(val_to))
                })
            except (ValueError, TypeError):
                return queryset
        return queryset
    
class DBHSliderFilter(BaseSliderFilter):
    STEP = 10

class HeightSliderFilter(BaseSliderFilter):
    STEP = 1

# 1. DEFINE THE RESOURCE FIRST
class TreeInventoryResource(resources.ModelResource):
    class Meta:
        model = TreeInventory
        import_id_fields = ('objectid',)

    def before_save_instance(self, instance, using_transactions, dry_run):
        # your coordinate transformation logic here...
        return instance

class TreeInventoryAdmin(NumericFilterModelAdmin, LeafletGeoAdmin):
    list_display = ('tree_id', 'species_name', 'dbh', 'height', 'spread', 'import_date')

    list_filter = (('dbh', DBHSliderFilter), ('height', HeightSliderFilter), 'lu_hmd', 'species_name')

    search_fields = ('tree_id', 'species_name', 'road_name')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # Note: Ensure the 'name' matches what you use elsewhere
            path('import-process/', self.admin_site.admin_view(import_tree_csv), name='import_process'),
        ]
        return custom_urls + urls
   

# Register the model
admin.site.register(TreeInventory, TreeInventoryAdmin)