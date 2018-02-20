from django.conf.urls import url
from . import views

app_name = "Apis"
urlpatterns = [
	url(r'edit-device-detail/(?P<device_id>[-\w]+)$', views.edit_device_detail_post, name='edit_device_detail_post'),
    url(r'get-values/(?P<device_id>[-\w]+)/(?P<ability>\w+)/$', views.get_values, name='get_values'),
	url(r'get-screenshot/(?P<screen_id>\d+)/$', views.get_screenshot, name='get_screenshot'),
]
