import requests
import pandas
from bs4 import BeautifulSoup
from pyecharts import Bar,Geo

def send_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    url = requests.get(url, headers=headers).text
    html = BeautifulSoup(url, 'lxml')
    return html

def city_food(html):
    food = [k.text for k in html.find('ol', {'class': 'list-rank'}).find_all('h3')]
    food_count = [int(k.text) for k in html.find('ol', {'class': 'list-rank'}).find_all('span',{'class':'trend'})]
    # food = [ k.find('h3') for k in html.find_all('li',{'class':'rank-item'})]
    # food_count =[k.find('span',{'class':'trend'}).text for k in html.find_all('li', {'class': 'rank-item'})]
    return pandas.DataFrame({'food':food[0:len(food_count)],'food_count':food_count})

def city_place(html):
    place =[i.text.split('\n')[2] for i in  html.find('div',{'class':'row-top5'}).find_all('h3')]
    place_count = [int(i.text.replace(' 条点评','')) for i in html.find_all('span',{'class':'rev-total'})]
    return pandas.DataFrame({'place':place[0:len(place_count)],'place_count':place_count})

def city_tag(html):
    tag = [i.find('a').text.split(' ')[-3] for i in html.find_all('li',{'class':'impress-tip'})]
    tag_count = [int(i.find('a').text.split(' ')[-2]) for i in html.find_all('li', {'class': 'impress-tip'}) if i.find('a').text.split(' ')[-2] !='']
    return pandas.DataFrame({'tag':tag[0:len(tag_count)],'tag_count':tag_count})

city = pandas.read_excel('mafengwo.xlsx')
city_base = []
city_count = []
for i in range(0,city.shape[0]):
    k = city.iloc[i]
    html_food = send_url('http://www.mafengwo.cn/cy/'+str(k['id'])+'/gonglve.html')
    html_place = send_url('http://www.mafengwo.cn/jd/' + str(k['id']) + '/gonglve.html')
    html_tag = send_url('http://www.mafengwo.cn/xc/' + str(k['id']) + '/gonglve.html')

    city_base.append(k['city'])
    city_count.append(city_tag(html_tag)['tag_count'].sum()+city_food(html_food)['food_count'].sum()+city_place(html_place)['place_count'].sum())

    if len(city_base) == 10:
        print('ok')
        break

attr = city_base
v1 = city_count
# bar = Bar("游记总数量TOP10")
# bar.add("游记总数", attr, v1, is_stack=True)
# bar.render('游记总数量TOP10.html')

geo = Geo('全国城市旅游热力图', title_color="#fff",
          title_pos="center", width=1200,
          height=600, background_color='#404a59')
# attr, value = geo.cast(data)
geo.add("", attr, v1, visual_range=[0, 30000], visual_text_color="#fff",
        symbol_size=15, is_visualmap=True,is_roam=False)
geo.render('蚂蜂窝游记热力图.html')
