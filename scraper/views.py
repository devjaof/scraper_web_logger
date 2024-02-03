from django.shortcuts import render
from bs4 import BeautifulSoup
from django.contrib import messages

import requests

def home(request):
    return render(request, 'base.html')

def scrape(request):
    if request.method == 'POST':

        url = request.POST['url']

        keywords = ["covid"]

        html = requests.get(url).content

        soup = BeautifulSoup(html, 'html.parser')

        a_tags = soup.find_all('a', href=True)

        pdf_links = []

        for a in a_tags:
            if ".pdf" in a['href']:
                pdf_links.append(a['href'])


        for pdf_url in pdf_links:
            messages.info(request, f"Fetched URL: {pdf_url}")
                        

        return render(request, 'base.html')
    else:
        return render(request, 'base.html')

