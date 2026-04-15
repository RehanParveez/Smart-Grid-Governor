from django.contrib import admin
from prioritization.models import PriorityWeight, FeedPriorScore

# Register your models here.
@admin.register(PriorityWeight)
class PriorityWeightAdmin(admin.ModelAdmin):
  list_display = ['factor_name', 'weight_value', 'description']
  
@admin.register(FeedPriorScore)
class FeedPriorScoreAdmin(admin.ModelAdmin):
  list_display = ['feeder', 'final_score', 'rank_in_zone', 'calculated_at']
