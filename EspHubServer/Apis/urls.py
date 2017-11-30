from django.conf.urls import url
from . import views

app_name = "Apis"
urlpatterns = [
    url(r'edit-device-detail$', views.edit_device_detail_post, name='edit_device_detail_post'),
]
