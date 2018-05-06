from django.conf.urls import url
from . import  views

urlpatterns = [
    #url(r'^login$', views.login, name='login'),
    url(r'^$', views.handle, name='homepage'),
    url(r'^processRequest', views.BNYBackEndPost),
    url(r'^getModels', views.getModels),
    url(r'^getOverlaps', views.getOverlaps),
    url(r'^manualProcessNode', views.manualProcessNode),
    url(r'^manualProcessRelationship', views.manualProcessEdge),
    url(r'^fileUpload', views.fileUpload)
    ]
