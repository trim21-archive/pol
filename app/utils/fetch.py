from bs4 import BeautifulSoup, element
import requests


# return a requests session, which include cookies. you can use it to get html directly
def login(student_ID: str, password: str):
    s = requests.session()
    s.get('http://bkjws.sdu.edu.cn')
    data = {
        'j_username': student_ID,
        'j_password': password
    }
    r6 = s.post('http://bkjws.sdu.edu.cn/b/ajaxLogin', data=data)
    if r6.text == '"success"':
        requests.utils.add_dict_to_cookiejar(s.cookies, data)
        return s
    else:
        return False


# use session to get lesson html
def get_lessen_html(student_ID: str, password: str):
    s = login(student_ID=student_ID, password=password)
    if s:
        r3 = s.get('http://bkjws.sdu.edu.cn/f/xk/xs/bxqkb')
        return r3.text
    else:
        return False
