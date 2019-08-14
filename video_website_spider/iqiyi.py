from urllib import parse


def get_ep_id_from_url(url: str):
    # 'http://www.iqiyi.com/v_19rro8bme0.html'
    url_obj: parse.ParseResult = parse.urlparse(url)
    return url_obj.path.split('/')[-1].replace('v_', '').replace('.html', '')


def get_bangumi_id_from_url(url: str):
    url_obj: parse.ParseResult = parse.urlparse(url)
    return url_obj.path.split('/')[-1].replace('a_', '').replace('.html', '')
