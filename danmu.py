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


def get_comments(av, index=None):
    # f = open(av + '.txt', 'w')
    if index:
        filename = 'bilibili_av{}_part{}.json'.format(av, index)
        url = 'http://bilibili.com/video/av{}/index_{}.html'.format(av, index)
    else:
        filename = 'bilibili_av{}.json'.format(av)
        url = 'http://bilibili.com/video/av' + str(av)
    html = requests.get(url, headers=head)
    selector = etree.HTML(html.text)
    content = selector.xpath("//html")
    for each in content:
        title = each.xpath('//div[@class="v-title"]/h1/@title')
        print('title', title)
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
                return comments_time_list, int(max_second), title[0], filename
            else:
                print('error')
        else:
            print('video not found!')


def process_time(comments_time_list, max_second, title, filename):
    max_minute = int(decimal.Decimal(max_second / 60).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_CEILING))
    print('total_minute', max_minute)
    print('total_second', max_second)
    freqs = Counter(comments_time_list)
    # print(freqs)
    f = open('flare2.json', 'w')
    # backup data in f2
    f2 = open(filename, 'w')
    flare = dict()
    children_level_one = []
    for i in range(max_minute):
        child_one = dict()
        children_level_two = []
        child_one['name'] = 'min:' + str(i)
        child_one['children'] = children_level_two
        children_level_one.append(child_one)
        start_second = i * 60
        for j in range(start_second, start_second + 60):
            child_two = dict()
            child_two['name'] = format_time(j)
            child_two['size'] = freqs.get(j, 0)
            children_level_two.append(child_two)
    highlight_1s = get_max_highlight_ns(max_second, freqs, 1)
    highlight_ns = get_max_highlight_ns(max_second, freqs, 5)
    flare['children'] = children_level_one
    flare['name'] = title
    flare['highlight_1s'] = highlight_1s
    flare['highlight_ns'] = highlight_ns
    json_dump = json.dumps(flare, indent=4)
    # print(json_dump)
    f.writelines(json_dump)
    f2.writelines(json_dump)


def get_max_highlight_ns(max_second, freqs, n):
    max_start_index = 0
    max_end_index = min(n - 1, max_second)
    max_sum = 0
    current_sum = 0
    for i in range(n):
        max_sum += freqs.get(i, 0)
        current_sum += freqs.get(i, 0)
    for i in range(n, max_second):
        current_sum = current_sum + freqs.get(i, 0) - freqs.get(i - n, 0)
        if current_sum > max_sum:
            max_sum = current_sum
            max_start_index = i - n + 1
            max_end_index = i
    if n == 1:
        highlight_ns = '最高能1秒:{}, 弹幕数:{}'.format(format_time(max_start_index), max_sum)
    else:
        highlight_ns = '最高能{}秒区间:{}-{}, 平均弹幕数:{}'.format(n, format_time(
            max_start_index), format_time(max_end_index), max_sum / n)
    print(highlight_ns)
    return highlight_ns


def format_time(total_second):
    minute = total_second // 60
    second = total_second % 60
    return '{}:{:02d}'.format(minute, second)


if __name__ == '__main__':
    # av = raw_input('input av:')
    av = '3133255'
    part = '6'
    comments_time_list, max_second, title, filename = get_comments(av, part)
    # comments_time_list = list(range(2800))
    # max_second = len(comments_time_list)
    process_time(comments_time_list, max_second, title, filename)
