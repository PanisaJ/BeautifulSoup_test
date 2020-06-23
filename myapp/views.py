from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
import requests 
from .models import Webpage, Article, Tag
import threading

from urllib.parse import urljoin

# Note: program will add data following number input and don't add duplicated article,  
#       (save only non-duplicated data)

#should call auto_added when data has existed in DB (blognone, techtalkthai)
def auto_added():
    threading.Timer(300, auto_added).start()
    message = ""
    blognone_count = update_blognone()
    techtalkthai_count = update_techtalkthai()
    
    if blognone_count > 0:
        message = "have " + str(blognone_count) + " news from blognone. "
    if techtalkthai_count > 0:
        message = message + "have " + str(techtalkthai_count) + " news from techtalkthai."
    
    if message:
        notify_message(message) 


def index(request):
    auto_added()
    web_list = Webpage.objects.all
    article_list = Article.objects.all().order_by('-id')
    context = {'web_list' : web_list, 'article_list' : article_list }
    return render(request, 'myapp/index.html', context)

def get_input(request):
    context = {}
    if request.POST.get('num') and request.POST.get('web') :
        user_number = int(request.POST.get('num')) 
        url = request.POST.get('web')
        
        if(url == Webpage.objects.get(pk=3).webpage_url):
            setup_url_blognone(user_number)
        else:
            setup_url_tech(user_number)
    else:
        context['error_message'] = "You didn't insert some input."
        
    context['web_list'] = Webpage.objects.all 
    return render(request, 'myapp/index.html', context)

def setup_url_blognone(user_number):
    url = Webpage.objects.get(web_text='blognone').webpage_url
    soup = setup_soup(url)
    page = 0
    added_count = 0
    # use added_count for counting  because Article.objects.all().count() didn't update immediately
    while added_count < user_number:
        remind_number = user_number - added_count
        #if not first time change url
        if (page > 0) :
            #set new soup for next page if number of data less than user's number. 
            soup = setup_soup(url + "?page=" + str(page))
        added_count = save_data_blognone(soup, url, remind_number, added_count)
        page += 1

def setup_url_tech(user_number):
    url = Webpage.objects.get(web_text='techtalkthai').webpage_url
    soup = setup_soup(url)
    # defind page is 1 because second page start url at /page/2/
    page = 1
    added_count = 0
    while added_count < user_number:
        remind_number = user_number - added_count
        #if not first time change url
        if (page > 1) :
            #set new soup for next page if number of data less than wanted. 
            soup = setup_soup(url + "/page/" + str(page) + "/")
        added_count = save_data_techtalkthai(soup, url, remind_number, added_count)
        page += 1

def save_data_blognone(soup, url, number, count):

    for index, title in enumerate(soup.find_all("h2", {"itemprop": "name"})): 
        url_link = urljoin(url, title.find('a').get('href'))
    
        # Add new one if it didn't exist.
        article, article_created = Article.objects.get_or_create(
            article_text=title.find('a').get('title'),
            article_url=url_link,
            Webpage=Webpage.objects.get(webpage_url=url),
        )
        if article_created: 
            # loop following index for each article.
            for tags in soup.find_all("span", {"class" : "terms"})[index]:
                for t in tags.find_all('a'):

                    tag, tag_created = Tag.objects.get_or_create(
                        tag_text=t.text,
                    )
                    tag =  Tag.objects.get(tag_text=t.text) 
                    article.tag.add(tag)
            count += 1 
        if count >= number:
            break  
    return count

def save_data_techtalkthai(soup, url, number, count):
    for title in soup.find_all("h2", {"class": "post-box-title"}):
        url_link = title.find('a').get('href')
        article, article_created = Article.objects.get_or_create(
            article_text=title.find('a').text,
            article_url=url_link,
            Webpage=Webpage.objects.get(webpage_url=url),
        )
        # open new link to get article's tag.
        if article_created :
            soup = setup_soup(url_link)
            get = soup.find("span", {"class" : "post-cats"})
            for t in get.find_all('a'):
                # if this tag didn't exist.
                tag, tag_created = Tag.objects.get_or_create(
                    tag_text=t.text,
                )
                tag =  Tag.objects.get(tag_text=t.text) 
                article.tag.add(tag)
            count += 1 
        if count >= number:
            break  
    return count

def setup_soup(url):
    r = requests.get(url)
    return BeautifulSoup(r.content, "lxml")

def search_data(request):
    article_list = Article.objects.all()
    context = {}
    context['web_list'] = Webpage.objects.all
    if request.GET['article']:
        article_list = article_list.filter(article_text__contains=request.GET['article'])

    if request.GET['selectweb'] != 'all':
        article_list = article_list.filter(Webpage__web_text=request.GET['selectweb'])

    context['selected_web'] = request.GET['selectweb']
    context['atricle_text'] = request.GET['article']
    context['article_list'] = article_list.order_by('-id')
    return render(request, 'myapp/index.html', context)

def update_blognone():
    url = Webpage.objects.get(web_text='blognone').webpage_url
    soup = setup_soup(url)
    page = 0
    count = 0
    not_lastest = True
    # if new data didn't exist in db then continue get data.
    while not_lastest:
        if (page > 0) :
            soup = setup_soup(url + "?page=" + str(page))
        not_lastest, count = save_data_blognone_for_update(soup, url, count)
        page += 1

    return count

def save_data_blognone_for_update(soup, url, count):
    for index, title in enumerate(soup.find_all("h2", {"itemprop": "name"})): 
        url_link = urljoin(url, title.find('a').get('href'))
    
        # Add new one if it didn't exist.
        article, article_created = Article.objects.get_or_create(
            article_text=title.find('a').get('title'),
            article_url=url_link,
            Webpage=Webpage.objects.get(webpage_url=url),
        )
        # article existed, don't add new tag. 
        if article_created: 
            # loop following index for each article.
            for tags in soup.find_all("span", {"class" : "terms"})[index]:
                for t in tags.find_all('a'):

                    tag, tag_created = Tag.objects.get_or_create(
                        tag_text=t.text,
                    )
                    tag =  Tag.objects.get(tag_text=t.text) 
                    article.tag.add(tag)
            count += 1
        else:
            return False, count
    return True, count

def update_techtalkthai():
    url = Webpage.objects.get(web_text='techtalkthai').webpage_url
    soup = setup_soup(url)
    page = 1
    count = 0
    not_lastest = True
    # use added_count for counting  because Article.objects.all().count() didn't update immediately
    while not_lastest:
        #if not first time change url
        if (page > 1) :
            #set new soup for next page if number of data less than user's number. 
            soup = setup_soup(url + "/page/" + str(page) + "/")
        not_lastest, count = save_data_techtalkthai_for_update(soup, url, count)
        page += 1

    return count

def save_data_techtalkthai_for_update(soup, url, count):

    for title in soup.find_all("h2", {"class": "post-box-title"}):
        url_link = title.find('a').get('href')

        article, article_created = Article.objects.get_or_create(
            article_text=title.find('a').text,
            article_url=url_link,
            Webpage=Webpage.objects.get(webpage_url=url),
        )
        # open new link to get article's tag.
        if article_created :
            soup = setup_soup(url_link)
            get = soup.find("span", {"class" : "post-cats"})
            for t in get.find_all('a'):
                # if this tag didn't exist.
                tag, tag_created = Tag.objects.get_or_create(
                    tag_text=t.text,
                )
                tag =  Tag.objects.get(tag_text=t.text) 
                article.tag.add(tag)
            count += 1
        else: 
            return False, count
    return True, count

def notify_message(message):
    payload = {'message':message}
    return line_notify(payload)

def line_notify(payload):
    url = 'https://notify-api.line.me/api/notify'
    access_token = 'blDPWJkFx9NfWPk1MSh4KqGIS5Zpa2iTVXbTwaTV5da'
    headers = {'content-type' : 'application/x-www-form-urlencoded', 'Authorization' : 'Bearer ' + access_token}
    return requests.post(url, headers=headers, data = payload) 
