from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path("", views.upload, name = "upload"),
    path('download_excel/', views.download_excel, name='download_excel'),
    path('graph/', views.view_graph, name='view_graph'),
    path('graph/download/', views.download_graph, name='download_graph'),
    path('history/', views.history, name='history'),
    path('download_excel/<int:prediction_id>/', views.download_excel_prediction, name='download_excel_prediction'),
    path('graph/<int:prediction_id>/', views.view_graph_prediction, name='view_graph_prediction'),
    path('graph/download/<int:prediction_id>/', views.download_graph_prediction, name='download_graph_prediction'),
    path('delete/<int:prediction_id>/', views.delete_prediction, name='delete_prediction'), # new url path added
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)