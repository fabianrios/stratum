from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    path('<which>/<coords>', cache_page(60 * 15)(views.index), name='index'),
    path('thirty_days/<which>/<where>', cache_page(60 * 60 * 12)(views.thirty_days), name='thirty_days'),
    path('everywhere/<which>/', cache_page(60 * 60 * 12)(views.everywhere), name='everywhere'),
    path('full_archive/<which>/<where>/<fr>/<until>', cache_page(60 * 60 * 12)(views.full_archive), name='full_archive'),
]