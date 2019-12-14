
from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^states$', views.states, name='states'),
    url(r'^bandwidth', views.bandwidth, name='bandwidth'),
    url(r'^kafka_consumers$', views.kafka_consumers, name='kafka_consumers'),
    url(r'^activate$', views.service_activate, name='service_activate'),
    url(r'^deactivate$', views.service_deactivate, name='service_deactivate'),
    url(r'^status', views.service_status, name='service_status'),
    url(r'^tru_remote_settings$', views.tru_device_settings, name='tru_remote_settings'),
]
