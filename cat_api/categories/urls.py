from django.urls import path
from .views import *

app_name = 'categories'

urlpatterns = [
    path('category/', CategoryAPIView.as_view()),
    path('category/<int:id>/', SingleCategoryAPIView.as_view()),
    path('category/level/<int:level>/', request_by_level_view),
    path('category/parent/<int:parent_id>/', request_by_parent_view),
    path('category/<int:first_id>/similar/<int:second_id>', SimilarityCategoryView.as_view()),
]
