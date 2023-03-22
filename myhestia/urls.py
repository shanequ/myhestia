"""myhestia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from core.views import upload, view_file
from django.conf.urls import include, url
from django.views.static import serve
from django.conf.urls.static import static
from login.views import login_view, login_check, login_out


#
# common URL
#
urlpatterns = [

    url(r'^admin/', admin.site.urls),

    #
    #  media file
    #
    url(r'^media/(?P<path>.*)$', serve, {'document_root': 'media/'}),

    #
    # file upload, download
    #
    url(r'^upload/$', upload, name='upload'),
    url(r'^view-file/(?P<file_uuid>[a-fA-F0-9]{32})/$', view_file, name='view_file'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_URL)


#
# APP URL
#
urlpatterns += [

    #
    # index page
    #
    url(r'^$', login_view, name='index'),

    #
    # login/logout
    #
    url(r'^login/$', login_view, name='login'),
    url(r'^login_check/$', login_check, name='login_check'),
    url(r'^logout/$', login_out, name='logout'),

    #
    # dashboard
    #
    url(r'^home/', include('core.urls')),

    # agent
    url(r'^agent/', include('agent.urls')),

    # client
    url(r'^client/', include('clientdb.urls')),

    # matter
    url(r'^matter/', include('matters.urls')),

    # project
    url(r'^project/', include('project.urls')),

    # notification template
    url(r'^n-template/', include('n_template.urls')),

    #
    url(r'^report/', include('my_report.urls')),

    # bill
    url(r'^bill/', include('my_bill.urls')),

]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]