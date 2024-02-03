from django.shortcuts import render
from bs4 import BeautifulSoup
from django.contrib import messages
from io import BytesIO
from PyPDF2 import PdfReader

import requests

def home(request):
    return render(request, 'base.html')

def scrape(request):
    if request.method == 'POST':
        url = request.POST['url']
        
        if not url:
            messages.error(request, "Please enter a URL")
            return render(request, 'base.html')
        
        messages.info(request, f"Starting search on: {url}")

        keywords = request.POST['keywords']

        if isinstance(keywords, str) and keywords:
            keywords = keywords.split(',')
            messages.info(request, f"Searching for keywords: {keywords}")

        html = requests.get(url).content

        soup = BeautifulSoup(html, 'html.parser')

        a_tags = soup.find_all('a', href=True)

        pdf_links = []

        for a in a_tags:
            if ".pdf" in a['href']:
                pdf_links.append(a['href'])


        for pdf_url in pdf_links:
            messages.info(request, f"Pdf link found: {pdf_url}")

            if keywords:
                results = search_pdf_for_keywords(pdf_url, keywords)
                messages.info(request, f"{results}");


        messages.info(request, "Search complete")
        return render(request, 'base.html', {'results': results})
    else:
        return render(request, 'base.html')


def search_pdf_for_keywords(url, keywords, ignore_whitespace=True):
    with requests.get(url, stream=True) as response:
        if response.status_code != 200:
            raise ValueError(f"Error downloading PDF: {response.status_code}")

        # otimizacao para ler o pdf em chunks
        with BytesIO() as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
            f.seek(0)

            reader = PdfReader(f)

            results = {keyword: [] for keyword in keywords}
            for page_num in range(len(reader.pages)):
                if page_num >= 20:
                    break

                page = reader.pages[page_num]
                text = page.extract_text()

                for keyword in keywords:
                    match_indices = [i for i in range(len(text) - len(keyword) + 1) if text[i:i+len(keyword)].lower() == keyword.lower()]

                    if match_indices:
                        for i in match_indices:
                            results[keyword].append((page_num + 1, text[i:i+len(keyword)]))
                            break

    return results

