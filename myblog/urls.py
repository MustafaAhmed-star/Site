 
from django.contrib import admin
from django.urls import path,include
from django.contrib.sitemaps.views import sitemap
from nblog.sitemaps import PostSitemap

sitemaps= {
    'posts':PostSitemap
}


urlpatterns = [
     #path('admin/', include('admin_volt.urls')),
    path("admin/", admin.site.urls),
    path('blog/',include('nblog.urls',namespace='nblog')),
    path('sitemap.xml',sitemap,{'sitemaps':sitemaps},name='django.contrib.sitemaps.views.sitemap')
]
