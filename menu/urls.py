from django.urls import path
from .views import MenuDetailView, HomePageView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('<path:url>', MenuDetailView.as_view(), name='menu-detail'),
]
