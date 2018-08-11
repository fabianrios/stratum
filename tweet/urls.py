from django.urls import path

from . import views

urlpatterns = [
    path('<which>/<coords>', views.index, name='index'),
    path('thirty_days/<which>/<where>', views.thirty_days, name='thirty_days'),
    path('full_archive/<which>/<where>/<fr>/<until>', views.full_archive, name='full_archive'),
]