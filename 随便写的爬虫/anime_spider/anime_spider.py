# 迷之网络问题，迷之解决……
# TODO：添加对多种图片格式的支持，目前只支持jpg
import os
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import img2pdf
import bs4
import requests
import urllib3

lock = threading.Lock()
tag_address = {}  # 章节_页数:图片真实地址
comic_number = 0
dirname = "H:\\"
comic_name = ''


class Http404Exception(Exception):
    pass


def input_and_search():
    # from urllib import parse
    # https://so.kukudm.com/search.asp?kw=%C5%AE%D3%D1
    pass


def get_chapters_addr(content_url):
    requests.DEFAULT_RETRIES = 50
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    with requests.session() as req:
        req.keep_alive = False
        res = req.get(content_url, verify=False)
        res.encoding = 'gbk'
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        temp = soup.find_all("a")
        tempp = []
        for i in temp:
            t = str(i)
            if "comic3" in t:
                tempp.append(i)
        # print(tempp)
        r = r'http:.*htm'
        temppp = []  # 最终得到的章节地址
        for ii in tempp:
            temppp.append((re.findall(r, str(ii))[0]))

        comic_name_cn = str(soup.find_all(colspan="2")[6].next).replace("漫画", "")

        return list(temppp), comic_name_cn


def get_pic_addr(html, chp, page):
    domain = "http://comic3.kkkkdm.com/comiclist/" + str(comic_number) + '/'
    middle = html.split('/')[5]
    url = domain + middle + "/" + str(page) + '.htm'
    try:
        time.sleep(0.1)
        r = requests.get(url)
        if r.status_code == 404:
            raise Http404Exception
        r.encoding = 'gbk'
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        temp_string = str(soup.find_all(language="javascript")[2])
        # print(temp_string)
        rr = r'newkuku.*?jpg\'>'
        ans = re.findall(rr, temp_string)
        rrr = r'newkuku.*jpg'
        anss = re.findall(rrr, ans[0])[0]  # 图片真实地址的低位
        print("获得" + str(chp) + "章" + str(page) + "页图片地址")
        return anss
    except Http404Exception:
        print(str(chp) + "章" + str(page - 1) + "页是当前章节最后一页")
        return None
    except:
        with open("html_error.log", "w+") as error:
            error.writelines(str(chp) + "章" + str(page) + "页未知错误\n")
        return -1


def get_and_process_pic(pic_addr, chp, page):
    pic_domain = "http://s4.kukudm.com/"
    pic_url = pic_domain + pic_addr

    header = {
        'Host': 'v2.kukudm.com',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) '
                      'Version/11.0 Mobile/15A5341f Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    requests.DEFAULT_RETRIES = 10
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        r = requests.get(pic_url, verify=False, stream=True)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        else:
            pass

        # 通过检测返回体前部是否是jpg幻数判断是否爬取成功
        if r.content[0:3] != b'\xff\xd8\xff':
            raise Http404Exception
        with open(dirname + str(chp) + '_' + str(page) + ".jpg", "wb") as pic:  # FIXED:无法自动创建新的文件夹存放图片
            pic.write(r.content)
        print("success")
    except Http404Exception:
        lock.acquire()
        tag = str(chp) + '_' + str(page)
        tag_address[tag] = pic_url
        with open("err.txt", 'a', encoding='gbk') as e:
            e.writelines(tag + '\n' + tag_address[tag] + '\n')
        lock.release()
    except requests.exceptions.HTTPError:
        with open("html_error.log", "w+") as error:
            error.write(str(chp) + "_" + str(page))
    finally:
        return


if __name__ == '__main__':
    # ------------控制参数-------------
    max_workers = 10  # 线程并发数量
    # url = str(input("输入要爬取到的漫画目录页url:\n"))
    # comic_number = url.split('/')[4]
    url = "http://comic.kkkkdm.com/comiclist/2333/"  # 要爬取的漫画目录页
    comic_number = url.split('/')[4]
    # ------------控制参数-------------

    start_time = time.time()

    # 通过漫画目录页爬取章节地址
    chp_addrs, name = get_chapters_addr(url)
    dirname = dirname + name + '\\'


    # 多线程爬取
    def a(chp):
        page = 0
        while 1:
            page = page + 1
            print(str(chp + 1), "章", str(page), "页开始")
            if os.path.exists(dirname + str(chp + 1) + '_' + str(page) + ".jpg"):
                print(str(chp + 1), "章", str(page), "页已有")
                continue
            else:
                addr = get_pic_addr(chp_addrs[chp], chp + 1, page)
                if addr is None:
                    break
                elif addr is -1:
                    continue
                else:
                    get_and_process_pic(addr, chp + 1, page)

        print(str(chp), "章爬完")
        return


    chps = []
    for i in range(0, chp_addrs.__len__()):
        chps.append(i)
    # a(chps[0])
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        pool.map(a, chps)  # FIXED:无法自动退出线程池

    # 将爬取到的图片制作成PDF文件以便阅读
    with open(dirname + name + ".pdf", "wb") as f:
        imgs = []
        for chp in range(1, 54):
            page = 1
            while 1:
                fname = str(chp) + '_' + str(page) + '.jpg'
                if os.path.exists(dirname + fname):
                    imgs.append(dirname + fname)
                    page = page + 1
                else:
                    break
        f.write(img2pdf.convert(imgs))

    print("全部完成，用时", end='')
    print((time.time() - start_time) / 60, end='')
    print("分")
