import requests
from bs4 import BeautifulSoup
from time import perf_counter
import sys
import asyncio
#from requests_html import HTML
#from requests_html import HTMLSession
#session = HTMLSession()
#import datetime
#import os



headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}


def searchProductAmazon(product):
    product = product.replace(' ', '+')
    urlamazon = f'https://www.amazon.in/s?k={product}&ref=nb_sb_noss'
    r = requests.get(urlamazon, headers=headers, timeout=(3.5,5))
    #time.sleep(1.5)
    soup = BeautifulSoup(r.content,'lxml')
    results = soup.find_all('div', {'data-component-type': 's-search-result'})
    print(len(results))

    def extractRecords(item):
        title_link = item.h2.a
        link = 'https://amazon.in' + title_link.get('href')

        title = title_link.span.text
        try:
            image = item.find('div', 'a-section aok-relative s-image-square-aspect').img['src']
        except AttributeError:
            image = item.find('div', 'a-section aok-relative s-image-fixed-height').img['src']
        try:
            price_parent = item.find('span', 'a-price')
            price = price_parent.find('span','a-offscreen').text
            price = price.replace(",","")
            price = price.replace(".","")
            price = int(price.strip("₹ ,.")) #strip does not remove , or . between number chars.
        except AttributeError as attr:
            #print("item no.: ",i)
            return
            # WE ABSOLUTELY NEED PRICES, so if an entry does not have prices we go to next
        
        try:
            #rating = item.find('span','a-declarative').a.i.span.text
            #print(rating)
            #rating = item.find('i','a-icon-star-small').span.text
            #print(title)
            rating = item.find('div','a-row a-size-small')
            rating = rating.span.get('aria-label')
            rating = rating[:3]
            rating = float(rating)
            #print(rating)

            review_count = item.find('span', {'class':'a-size-base','dir':'auto'}).text
            review_count = ''.join(c for c in review_count if c.isdigit())
            review_count = int(review_count)
            #print(review_count)

        except AttributeError as attr:

##            print(attr)
##            exc_type, exc_value, traceback = sys.exc_info()
##            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
##            print(exc_type, fname, exc_tb.tb_lineno)

##            _, _, traceback = sys.exc_info()
##            if traceback.tb_lineno == 52:
##                print("rating not found")
##            elif traceback.tb_lineno == 56:
##                print("review not found")

            rating = 0
            review_count = 0
           # If a product does not have ratings then give it blank value because we can still use it.
        
        result = (title,link,image,rating,review_count,price)
        return result
        
    if len(results)==0:
        return None
    else:
        amazonList = []
        for i in range(len(results)):
            item = results[i]
            result = extractRecords(item)
            if result != None:
                amazonList.append(result)

    return amazonList

def searchProductFlipkart(product):
    product = product.replace(' ', '%20')
    urlflipkart = f'https://www.flipkart.com/search?q={product}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&sort=relevance'
    r = requests.get(urlflipkart, headers=headers)
    #time.sleep(1)
    soup = BeautifulSoup(r.text,'html.parser')
    
    results = soup.find_all('div',style='width:100%')
    if len(results)==0:
        results = soup.find_all('div',style='width:25%')
    print(len(results))

    def extractRecords(item):
        title_link = item.find('a','s1Q9rs')     
        #print("title link:",title_link)
        
        if title_link==None:
            title_link = item.find('a','_1fQZEK')
            #print(title_link)
            title = title_link.find('div','_4rR01T').text
        else:
            title = title_link.text
            
        
        link = 'https://flipkart.com'+title_link.get('href')
        image = item.find('img', '_396cs4')['src']

        try:
            price = item.find('div', '_30jeq3').text
            price = price.replace(",", "")
            price = price.replace(".","")
            price = int(price.strip("₹ ,."))
        except AttributeError as attr:
            print("item no.: ",i)
            return
            # WE ABSOLUTELY NEED PRICES, so if an entry does not have prices we go to next
        
        try:
            rating_parent = item.find('div', 'gUuXy-')
            rating = rating_parent.find('div','_3LWZlK').text
            rating = float(rating)
            rating_count = rating_parent.find('span', '_2_R_DZ').text
            #print(rating_count)
            rating_count = rating_count.strip('( ) ')

            temp=0
            for i in rating_count:
                if i=="R":
                    temp=rating_count.index(i)
                    rating_count = rating_count[0:temp]
                    break
            #print(rating_count)
            rating_count=''.join(c for c in rating_count if c.isdigit())
            rating_count = int(rating_count)
            # If a product has equal price then we sort by rating_count
            #print(rating_count)
        except AttributeError as attr:
            rating = 0
            rating_count = 0
           # If a product does not have ratings then give it blank value because we can still use it.
        
        result = (title,link,image,rating,rating_count,price)
        return result
        
    if len(results)==0:
        return None
    else:
        flipkartList = []
        for i in range(len(results)):
            item = results[i]
            result = extractRecords(item)
            if result != None:
                flipkartList.append(result)

    return flipkartList

def searchProductSnapdeal(product):
    product = product.replace(" ", "%20")
    urlsnapdeal = f"https://www.snapdeal.com/search?keyword={product}&santizedKeyword=&catId=&categoryId=0&suggested=false&vertical=&noOfResults=20&searchState=&clickSrc=go_header&lastKeyword=&prodCatId=&changeBackToAll=false&foundInAll=false&categoryIdSearched=&cityPageUrl=&categoryUrl=&url=&utmContent=&dealDetail=&sort=rlvncy"
    r = requests.get(urlsnapdeal, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find_all('div', {'class': 'col-xs-6'})
    print(len(results))

    def extractRecords(item):
        try:
            title_link = item.find("div",{"class":"product-desc-rating"}).a
            link = title_link.get('href')
            title = title_link.p.text
            #print(title)
        except AttributeError:
            return
        try:
            image = item.find('div', 'product-tuple-image').picture.img['src']
        except (AttributeError, KeyError):
            image = item.find('div', 'product-tuple-image').picture.source.get('srcset')
        try:
            price_parent = title_link.find('span',{'class':'lfloat product-price'})
            price = price_parent.get('display-price')
            price = price.replace(",","")
            price = price.replace(".","")
            price = int(price.strip("₹ ,.")) #strip does not remove , or . between number chars.
        except AttributeError as attr:
            #print("item no.: ",i)
            return
            # WE ABSOLUTELY NEED PRICES, so if an entry does not have prices we go to next
        
        try:

            rating_parent = title_link.find('div',{"class":"clearfix rating av-rating"})
            rating = rating_parent.find('div',{"class": "filled-stars"}).get('style')
            #print(rating)
            rating = rating[6:-3]
            rating = int(float(rating))*5/100
            #print(rating)
            rating_count = rating_parent.p.text
            rating_count = rating_count[1:-1]
            rating_count = float(rating_count)
            #print("rating count: ",rating_count)

        except AttributeError as attr:
            rating_count = 0
            rating = 0
           # If a product does not have ratings then give it blank value because we can still use it.
        
        result = (title,link,image,rating,rating_count,price)
        return result
        
    if len(results) == 0:
        return None
    else:
        snapdealList = []
        for i in range(len(results)):
            item = results[i]
            result = extractRecords(item)
            if result != None:
                snapdealList.append(result)

    return snapdealList


if __name__ == "__main__":
    
    product = input() # Takes search term as input. Ex: input('peanut butter crunchy') searches for peanut butter crunchy on all 3 platforms and presents the results.
    
    start1 = perf_counter()
    priceAmazon = searchProductAmazon(product)
    end1 = perf_counter()
    print("Elapsed time: ", end1 - start1)
    print("Search results from Amazon: ", priceAmazon)

    start2 = perf_counter()
    priceFlipkart = searchProductFlipkart(product)
    end2 = perf_counter()
    print("Elapsed time: ", end2-start2)
    print("Price at flipkart: ", priceFlipkart)

    start3 = perf_counter()
    priceSnapdeal = searchProductSnapdeal(product)
    end3 = perf_counter()
    print("Elapsed time: ", end3-start3)
    print("Price at Snapdeal: ", priceSnapdeal)


    print("Total elapsed time: ", end3-start1)


