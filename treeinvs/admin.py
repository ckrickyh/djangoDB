from django.contrib import admin # Use standard admin here
from leaflet.admin import LeafletGeoAdmin
from .models import TreeInventory, TreePhotoUrl

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin

from django.urls import path
from admin_numeric_filter.admin import NumericFilterModelAdmin, SliderNumericFilter
from .views import import_tree_csv

from django.utils.html import format_html

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
    list_display = ('tree_id', 'species_name', 'dbh', 'height', 'spread', 'display_photos', 'import_date')
    list_filter = (('dbh', DBHSliderFilter), ('height', HeightSliderFilter), 'lu_hmd', 'species_name')
    search_fields = ('tree_id', 'species_name', 'road_name')

    list_per_page = 100

    def display_photos(self, obj):
        # Fetch all related photos using the related_name 'photos'
        urls = obj.photos.all()
        if not urls:
            return "No Photos"
        
        # Create a string of clickable links
        links = [format_html('<a href="{}" target="_blank">Photo {}</a>', p.url, i+1) 
                 for i, p in enumerate(urls)]
        return format_html(", ".join(links))

    display_photos.short_description = 'Photo Links'

    # Custom urls for admin actions
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # Note: Ensure the 'name' matches what you use elsewhere
            path('import_process/', self.admin_site.admin_view(import_tree_csv), name='import_process'),
        ]
        return custom_urls + urls
    
class TreePhotoUrlAdmin(admin.ModelAdmin):
    list_display = 'tree_tag', 'url'
    
    # search using the linked tree_id (using double underscore) and url
    search_fields = 'tree_tag__tree_id', 'url'

    list_per_page = 100

# Register the model
admin.site.register(TreeInventory, TreeInventoryAdmin)
admin.site.register(TreePhotoUrl, TreePhotoUrlAdmin)