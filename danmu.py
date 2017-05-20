# -*-coding:utf8-*-

from lxml import etree
import requests
import re
from collections import Counter
import decimal
import json

head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'
}


def get_comments(av):
    # f = open(av + '.txt', 'w')
    url = 'http://bilibili.com/video/av' + str(av)
    html = requests.get(url, headers=head)
    selector = etree.HTML(html.text)
    content = selector.xpath("//html")
    for each in content:
        title = each.xpath('//div[@class="v-title"]/h1/@title')
        if title:
            cid_html_1 = each.xpath('//div[@class="scontent"]/iframe/@src')
            cid_html_2 = each.xpath('//div[@class="scontent"]/script/text()')
            if cid_html_1 or cid_html_2:
                if cid_html_1:
                    cid_html = cid_html_1[0]
                else:
                    cid_html = cid_html_2[0]

                cids = re.findall(r'cid=.+&aid', cid_html)
                cid = cids[0].replace("cid=", "").replace("&aid", "")
                comment_url = 'http://comment.bilibili.com/' + str(cid) + '.xml'
                print('comment link', comment_url)
                comment_text = requests.get(comment_url, headers=head)
                comment_selector = etree.HTML(comment_text.content)
                comment_content = comment_selector.xpath('//i')
                cnt = 0
                comments_time_list = []
                max_second = 0
                for comment_each in comment_content:
                    # comments = comment_each.xpath('//d/text()')
                    comments_p = comment_each.xpath('//@p')
                    # f.writelines(comment + '\n')
                    for comment_p_each in comments_p:
                        cnt += 1
                        comment_time = comment_p_each.split(',')[0]
                        comment_time_float = float(comment_time)
                        # f.writelines(str(cnt) + ':' + ' ' + str(comment_time_float) + '\n')
                        comment_time_int = int(comment_time_float)
                        max_second = max(comment_time_int, max_second)
                        comments_time_list.append(comment_time_int)
                        # print('add time', comment_time_int)
                print('done fetching comments, total comments:', cnt)
                return comments_time_list, int(max_second)
            else:
                print('error')
        else:
            print('video not found!')


def process_time(comments_time_list, max_second):
    max_minute = int(decimal.Decimal(max_second / 60).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_CEILING))
    print('max_minute', max_minute)
    print('max_second', max_second)
    freqs = Counter(comments_time_list)
    # print(freqs)
    f = open('flare2.json', 'w')
    flare = dict()
    flare['name'] = 'flare'
    children_level_one = []
    for i in range(max_minute):
        child_one = dict()
        children_level_two = []
        child_one['name'] = 'min:' + str(i)
        child_one['children'] = children_level_two
        children_level_one.append(child_one)
        start_second = i * 60
        for j in range(start_second, start_second + 60):
            if freqs.get(j):
                child_two = dict()
                child_two['name'] = '{}:{}'.format(str(i), j - start_second)
                child_two['size'] = freqs.get(j)
                children_level_two.append(child_two)
    flare['children'] = children_level_one
    json_dump = json.dumps(flare, indent=4)
    # print(json_dump)
    f.writelines(json_dump)


if __name__ == '__main__':
    # av = raw_input('input av:')
    av = '3133255'
    comments_time_list, max_second = get_comments(av)
    # comments_time_list = list(range(2800))
    # max_second = len(comments_time_list)
    process_time(comments_time_list, max_second)
