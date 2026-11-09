from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_calificacion, name='crear'),
    path('editar/<int:pk>/', views.editar_calificacion, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_calificacion, name='eliminar'),
]
