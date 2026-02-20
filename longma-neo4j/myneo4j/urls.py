from django.conf.urls import url

from .views import *

urlpatterns = [

    url(r"^$", index, name="index"),
    url(r"^index$", index, name="index"),
    url(r"^tree$", tree, name="tree"),
]
