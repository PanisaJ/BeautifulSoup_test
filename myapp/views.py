from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
import requests 

from urllib.parse import urljoin

def index(request):
    return render(request, 'myapp/index.html')

def get_input(request):
    if request.POST.get('num') and request.POST.get('web') :
        n = int(request.POST.get('num')) 
        url = request.POST.get('web')
        if(url == "https://www.blognone.com/node"):
            data = setup_url_blognone(url, n)
        else:
            data = setup_url_tech(url, n)
        return render(request, 'myapp/index.html', {'data' : data})
    else:
        return render(request, 'myapp/index.html', {'error_message': "You didn't insert some input."})

def setup_url_blognone(url, n):
    data = {}
    soup = setup_soup(url)
    count = 0
    while len(data) < n:
        remind_number = n - len(data)
        #if not first time change url
        if (count > 0) :
            #set new soup for next page if number of data less than wanted. 
            soup = setup_soup(url + "?page=" + str(count))
        data = find_data_blognone(soup, url, remind_number, data)
        count += 1
    return data

def setup_url_tech(url, n):
    data = {}
    soup = setup_soup(url)
    count = 1
    while len(data) < n:
        remind_number = n - len(data)
        #if not first time change url
        if (count > 1) :
            #set new soup for next page if number of data less than wanted. 
            soup = setup_soup(url + "/page/" + str(count) + "/")
        data = find_data_techtalkthai(soup, url, remind_number, data)
        count += 1
    return data

def find_data_blognone(soup, url, number, data):
    # keep number for set index of tags is start the same index of title dictionary.
    keep_start_index = len(data) + 1
    for title in soup.find_all("h2", {"itemprop": "name"}, limit=number):
        url_link = urljoin(url, title.find('a').get('href'))
        data[len(data)+1] = {'url_link' : url_link, 'title' : title.find('a').get('title')}

    for index, tags in enumerate(soup.find_all("span", {"class" : "terms"}, limit=number)):
        data[index + keep_start_index]["tags"] = [tag.text for tag in tags.find_all('a')]
    return data

def find_data_techtalkthai(soup, url, number, data):
    keep_start_index = len(data) + 1
    
    for title in soup.find_all("h2", {"class": "post-box-title"}, limit=number):
        url_link = title.find('a').get('href')
        data[len(data)+1] = {'url_link' : url_link, 'title' : title.find('a').text}

    for i, index in enumerate(range(keep_start_index, len(data)+1)):
        soup = setup_soup(data[index]["url_link"])
        get = soup.find("span", {"class" : "post-cats"})
        data[i + keep_start_index]["tags"] = [tag.text for tag in get.find_all('a')]
    return data

def setup_soup(url):
    r = requests.get(url)
    return BeautifulSoup(r.content, "lxml")