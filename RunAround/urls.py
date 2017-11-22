
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from pages import views as page_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', page_views.home, name='home'),
    url(r'^map/', page_views.map, name='map'),
    url(r'^phone/', page_views.phone, name='phone')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
