from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from django.shortcuts import render, get_object_or_404

import feedparser
import collections

from .forms import ContactForm, GenerateForm

from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Avg
from django.shortcuts import render_to_response
from django.template import RequestContext
from safetexas.models import Payment
from qsstats import QuerySetStats

from pprint import pprint as pp

import safetexas.settings

from datetime import datetime, timedelta
import json
import os

def read_data(filename):
    data = []
    try:
	with open(filename) as f:
	    for line in f:
		data.append(json.loads((line.strip()).encode('utf-8')))
    
    except:
	print "Failed to read json data!"
	return
        
    return data

def check_date(tweets):
	
    stat = { }
    
    one_year = 0
    six_month = 0
    three_month = 0
    one_month = 0
    one_week = 0
    one_day = 0
	
    stat['recent'] = []
    
    for tweet in tweets:
	
	date_str = tweet['date']
	date = datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y')
    
	one_year_ago = datetime.now() - timedelta(days=30*12)
	six_month_ago = datetime.now() - timedelta(days=30*6)
	three_month_ago = datetime.now() - timedelta(days=30*3)
	month_ago = datetime.now() - timedelta(days=30)
	week_ago = datetime.now() - timedelta(days=7)
	day_ago = datetime.now() - timedelta(days=1)
    
	# Date is within..........
	if date > one_year_ago:
	    one_year += 1
	if date > six_month_ago:
	    six_month += 1
	if date > three_month_ago:
	    three_month += 1
	if date > month_ago:
	    one_month += 1
	if date > week_ago:
	    one_week += 1
	if date > day_ago:
	    one_day += 1
    
    stat['total'] = len(tweets)
    stat['last_year'] = one_year 
    stat['last_six'] = six_month
    stat['last_three'] = three_month
    stat['last_month'] = one_month
    stat['last_week'] = one_week
    stat['last_day'] = one_day
	
    tweets.sort(key=lambda x: datetime.strptime(x['date'], '%a %b %d %H:%M:%S %Y'), reverse=True)
	
    i = 0
    for i in range(0,10):
	stat['recent'].append(tweets[i])
        
    return stat 

def city_data(city):
    cities = [ city ]
    classes = [ "accident", "crime_drugs", "crime_finance", "crime_gen", "crime_homicide", "crime_sex", "disaster", "misc" ]
    stat_keys = [ "last_day", "last_month", "last_six", "last_three", "last_week", "last_year" ]
    crime_keys = [ "crime_drugs", "crime_finance", "crime_gen", "crime_homicide", "crime_sex" ]
    
    stats = { }
    totals = { }

    for city in cities:
	totals[city] = 0
	stats[city] = { }
	stats[city]['crimes'] = { }
	for c in classes:
	    stats[city][c] = { }
	for stat_key in stat_keys:
	    stats[city]['crimes'][stat_key] = 0
	    stats[city]['crimes']['total'] = 0
	    
    BASE_DIR =  os.path.dirname(os.path.dirname(__file__))
    
    # READ ALL CITY JSON FILES
    for city in cities:
	for c in classes:
	    tweetFile = BASE_DIR + "/safetexas/tweets/" + city + "_" + c + ".json"
	    data = read_data(tweetFile)
	    totals[city] += len(data)
	    stats[city][c] = check_date(data)
    
    # CALCULATE CRIME TOTALS
    crimes = [ ]
    for city in cities:
	for crime_key in crime_keys:
	    if crime_key is "crime_drugs":
		crime_str = "Drugs"
	    elif crime_key is "crime_finance":
		crime_str = "Financial"
	    elif crime_key is "crime_homicide":
		crime_str = "Homicide"
	    elif crime_key is "crime_gen":
		crime_str = "General"	
	    elif crime_key is "crime_sex":
		crime_str = "Sexual"
		    
	    crimes.append([ crime_str, stats[city][crime_key]['total'] ])
	    stats[city]['crimes']['total'] += stats[city][crime_key]['total']
		
	    for stat_key in stat_keys:
		stats[city]['crimes'][stat_key] += stats[city][crime_key][stat_key]
		
    classes = [ ]
    classes.append([ "Crimes", stats[city]['crimes']['total'] ])
    classes.append([ "Disaster", stats[city]['disaster']['total'] ])
    classes.append([ "Accident", stats[city]['accident']['total'] ])
    
    context = {}
    context['classes'] = classes
    context['crimes'] = crimes
	
    context['city'] = stats[city]
    context['totals'] = totals[city]
    
    if city is "dallas":
	context['bg'] = "http://media-cdn.tripadvisor.com/media/photo-s/01/70/fb/0c/dallas-skyline-texas.jpg"
	context['title'] = "Dallas"
    elif city is "austin":
	context['bg'] = "http://www.evolvernetwork.org/wp-content/uploads/2012/07/austin.jpg"
	context['title'] = "Austin"
    elif city is "el_paso":
	context['bg'] = "http://makeuponlinetraining.com/wp-content/uploads/2012/10/el-paso3.jpg"
	context['title'] = "El Paso"
    elif city is "san_antonio":
	context['bg'] = "http://a1.cdn-hotels.com/images/themedcontent/en_GB/San%20Antonio_Neighbourhoods.jpg"
	context['title'] = "San Antonio"
    elif city is "fort_worth":
	context['bg'] = "http://cowgirlintraining.files.wordpress.com/2012/02/downtown.jpg"
	context['title'] = "Fort Worth"	    
    elif city is "houston":
	context['bg'] = "http://www.houstonproperties.com/images/houston-downtown-night.jpg"
	context['title'] = "Houston"
	    
    return context


# TITLES DEFINED HERE

def load_titles():
    titles = [ 
	# ladder jobs
	"systems engineer", 
	"systems administrator",
	"information technology",
	"software applications",
	"microcomputer/lan administrator",
	"network analyst",
	"network engineer",
	"security analyst",
	"database administrator",
	"it policy",
	
	# non-ladder jobs
	"applications development",
	"computer systems",
	"engineering senior",
	"eis senior",
	"information services",
	"information technology/lan",
	"workstation support",
	"microcomputer coordinator",
	"microcomputer specialist",
	"network group",
	"network/system administrator",
	"network/systems engineer",
	"network/systems manager",
	"programmer/analyst",
	"database/systems administrator",
	"lead eis",
	"systems analyst",
	"visualization systems",
	"lead security",
	"technology training",
	"video network",
	"web and information designer",
	"website administrator",
	"website designer",
	
	# possibly non-IT jobs
	"distance education",
	"eis functional"
	] 
	
    return titles
    
class HomePageView(TemplateView):
    template_name = 'safetexas/layout.html'

class FormView(FormView):
    template_name = 'safetexas/form.html'
    form_class = ContactForm
class FormHorizontalView(FormView):
    template_name = 'safetexas/form_horizontal.html'
    form_class = ContactForm
class FormInlineView(FormView):
    template_name = 'safetexas/form_inline.html'
    form_class = ContactForm

class PaginationView(TemplateView):
    template_name = 'safetexas/pagination.html'

    def get_context_data(self, **kwargs):
        context = super(PaginationView, self).get_context_data(**kwargs)
        lines = []
        for i in range(10000):
            lines.append(u'Line %s' % (i + 1))
        paginator = Paginator(lines, 10)
        page = self.request.GET.get('page')
        try:
            show_lines = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            show_lines = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            show_lines = paginator.page(paginator.num_pages)
        context['lines'] = show_lines
        return context
           
class JobsView(TemplateView):
    template_name = 'safetexas/jobs.html'
    
    def get_context_data(self, **kwargs):
	context = super(JobsView, self).get_context_data(**kwargs)
	
	# https://jobpath.tamu.edu/all_jobs.atom
	f = feedparser.parse('https://jobpath.tamu.edu/all_jobs.atom') 
	titles = load_titles()
	num_entries =  len(f.entries)    
    
	jobs = { } 
    
	count = 0
	bookmark_count = 0
	for i in range(0, num_entries):
	
	    title = f.entries[i].title
	    link = f.entries[i].link
	    
	    date = f.entries[i].published_parsed
	    year = date.tm_year
	    month = date.tm_mon
	    day = date.tm_mday
	    
	    key = year + (1000*month) + (20*day)
	    while key in jobs.keys(): 
		key += 1
	    

	    date_str = str(month) +"/"+ str(day) +"/"+ str(year)
	    
	    jobs[key] = dict(title = title, date = date_str, link = link, bookmark = False)
	    count += 1
	
	    if any(word in f.entries[i].title.lower() for word in titles):
		jobs[key]['bookmark'] = True
		bookmark_count += 1

	od = collections.OrderedDict(sorted(jobs.items(), reverse=True))
	
	context['jobs'] = od
	context['num_it_jobs'] = bookmark_count
	context['num_jobs'] = num_entries
	return context
        
class AustinView(TemplateView):
    template_name = 'safetexas/city.html'  
    def get_context_data(self, **kwargs):
	context = super(AustinView, self).get_context_data(**kwargs)
	city = "austin"
	data = city_data(city)
	context['classes'] = data['classes']
	context['crimes'] = data['crimes']
	context['city'] = data['city']
	context['city_name'] = city
	context['totals'] = data['totals']
	context['title'] = data['title']
	context['bg'] = data['bg']
	return context
	
class DallasView(TemplateView):
    template_name = 'safetexas/city.html'  
    def get_context_data(self, **kwargs):
	context = super(DallasView, self).get_context_data(**kwargs)
	city = "dallas"
	data = city_data(city)
	context['classes'] = data['classes']
	context['crimes'] = data['crimes']
	context['city'] = data['city']
	context['city_name'] = city
	context['totals'] = data['totals']
	context['title'] = data['title']
	context['bg'] = data['bg']
	return context

class SanAntonView(TemplateView):
    template_name = 'safetexas/city.html'  
    def get_context_data(self, **kwargs):
	context = super(SanAntonView, self).get_context_data(**kwargs)
	city = "san_antonio"
	data = city_data(city)
	context['classes'] = data['classes']
	context['crimes'] = data['crimes']
	context['city'] = data['city']
	context['city_name'] = city
	context['totals'] = data['totals']
	context['title'] = data['title']
	context['bg'] = data['bg']
	return context

class ElPasoView(TemplateView):
    template_name = 'safetexas/city.html'  
    def get_context_data(self, **kwargs):
	context = super(ElPasoView, self).get_context_data(**kwargs)
	city = "el_paso"
	data = city_data(city)
	context['classes'] = data['classes']
	context['crimes'] = data['crimes']
	context['city'] = data['city']
	context['city_name'] = city
	context['totals'] = data['totals']
	context['title'] = data['title']
	context['bg'] = data['bg']
	return context
	
class HoustonView(TemplateView):
    template_name = 'safetexas/city.html'  
    def get_context_data(self, **kwargs):
	context = super(HoustonView, self).get_context_data(**kwargs)
	city = "houston"
	data = city_data(city)
	context['classes'] = data['classes']
	context['crimes'] = data['crimes']
	context['city'] = data['city']
	context['city_name'] = city
	context['totals'] = data['totals']
	context['title'] = data['title']
	context['bg'] = data['bg']
	return context

class FortWorthView(TemplateView):
    
    template_name = 'safetexas/city.html'  
    def get_context_data(self, **kwargs):
	context = super(FortWorthView, self).get_context_data(**kwargs)
	city = "fort_worth"
	data = city_data(city)
	context['classes'] = data['classes']
	context['crimes'] = data['crimes']
	context['city'] = data['city']
	context['city_name'] = city
	context['totals'] = data['totals']
	context['title'] = data['title']
	context['bg'] = data['bg']
	return context

   
def tweets(request, city_name, class_name):

    BASE_DIR =  os.path.dirname(os.path.dirname(__file__))
    tweetFile = BASE_DIR + "/safetexas/tweets/" + city_name + "_" + class_name + ".json"
    
    data = read_data(tweetFile)
    data.sort(key=lambda x: datetime.strptime(x['date'], '%a %b %d %H:%M:%S %Y'), reverse=True)
    
    context = { }
    context['data'] = data
    
    if class_name.find('_') == -1:
	context['class_name'] = class_name.capitalize()
    else:
	cname = class_name.split('_')
	context['class_name'] = cname[0].capitalize() + " " + cname[1].capitalize()
    
    if city_name.find('_') == -1:
	context['city_name'] = city_name.capitalize()
    else:
	ciname = city_name.split('_')
	context['city_name'] = ciname[0].capitalize() + " " + ciname[1].capitalize()
    
    context['total'] = len(data)
    
    context['city'] = city_name
    context['class'] = class_name
    
    context['classes'] = { "accident" : "Accident", "crime_drugs" : "Crime/Drugs", "crime_finance" : "Crime/Finance", "crime_gen" : "Crime/General", "crime_homicide" : "Crime/Homicide", "crime_sex" : "Crime/Sex", "disaster": "Disaster", "misc" : "Misc" }
    

    return render(request, 'safetexas/tweets.html', {'tweets': context})
