# -*-coding:utf8-*-

from lxml import etree
import requests
import re

head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'
}


def get_comments(av):
    f = open(av + '.txt', 'w')
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
                for comment_each in comment_content:
                    #comments = comment_each.xpath('//d/text()')
                    comments_p = comment_each.xpath('//@p')
                    # f.writelines(comment + '\n')
                    for comment_p_each in comments_p:
                        cnt += 1
                        comment_time = comment_p_each.split(',')[0]
                        comment_time_float = float(comment_time)
                        f.writelines(str(cnt) + ':' + ' ' + str(comment_time_float) + '\n')
                        comments_time_list.append(comment_time_float)
                print('done fetching comments, total comments:', cnt)
                return comments_time_list
            else:
                print('error')
        else:
            print('video not found!')


if __name__ == '__main__':
    # av = raw_input('input av:')
    av = '3133255'
    get_comments(av)
