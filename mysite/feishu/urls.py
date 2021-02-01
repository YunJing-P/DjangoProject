from django.urls import path
from . import views
from .apis import Api
from django.views.decorators.csrf import csrf_exempt

app_name = 'feishu'
urlpatterns = [
    path('', views.index, name='index'),
    path('token/', Api.update_token),
    path('api/', csrf_exempt(Api.as_view())),
]