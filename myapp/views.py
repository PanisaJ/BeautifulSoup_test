from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
import requests 

from urllib.parse import urljoin

def index(request):
    return render(request, 'myapp/index.html')

def get_article(request):
    if request.POST.get('num') and request.POST.get('web') :
        print(request.POST.get('web'))
        n = int(request.POST.get('num')) 
        data = {}
        url = request.POST.get('web')
        soup = setup_soup(url)
        count = 0
        while len(data) < n:
            remind_number = n - len(data)
            #if not first time change url
            if (count > 0) :
                #set new soup for next page if number of data less than wanted. 
                soup = setup_soup(url + "?page=" + str(count))
            data = find_data(soup, url, remind_number, data)
            count += 1
        return render(request, 'myapp/index.html', {'data' : data})
    else:
        return render(request, 'myapp/index.html', {'error_message': "You didn't insert some input."})
    

def find_data(soup, url, number, data):
    keep_start_index = len(data) + 1
    for title in soup.find_all("h2", {"itemprop": "name"}, limit=number):
        url_link = urljoin(url, title.find('a').get('href'))
        data[len(data)+1] = {'url_link' : url_link, 'title' : title.find('a').get('title')}

    for index, tags in enumerate(soup.find_all("span", {"class" : "terms"}, limit=number)):
        data[index + keep_start_index]["tags"] = [tag.text for tag in tags.find_all('a')]
    return data

def setup_soup(url):
    r = requests.get(url)
    return BeautifulSoup(r.content, "lxml")