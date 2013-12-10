from django.conf.urls import patterns, include, url

from .views import HomePageView, FormView, FormHorizontalView, FormInlineView, PaginationView, JobsView, HoustonView, AustinView, FortWorthView, DallasView, ElPasoView, SanAntonView

from django.contrib import admin
admin.autodiscover()

from safetexas import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'safetexas.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),

    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^form$', FormView.as_view(), name='form'),
    url(r'^form_horizontal$', FormHorizontalView.as_view(), name='form'),
    url(r'^form_inline$', FormInlineView.as_view(), name='form'),
    url(r'^pagination$', PaginationView.as_view(), name='pagination'),
    
    url(r'^jobs$', JobsView.as_view(), name='jobs'),
    
    
    #url(r'^city$', CityView.as_view(), name='city'),
    url(r'^city/houston$', HoustonView.as_view(), name='houston'),
    url(r'^city/san_antonio$', SanAntonView.as_view(), name='san_antonio'),
    url(r'^city/dallas$', DallasView.as_view(), name='dallas'),
    url(r'^city/austin$', AustinView.as_view(), name='austin'),
    url(r'^city/el_paso$', ElPasoView.as_view(), name='el_paso'),
    url(r'^city/fort_worth$', FortWorthView.as_view(), name='fort_worth'),

    url(r'^tweets/(?P<city_name>.*)/(?P<class_name>.*)$', views.tweets, name='tweets'),
)
