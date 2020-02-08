# Pol

[![Join the chat at https://gitter.im/pol-chat/community](https://badges.gitter.im/pol-chat/community.svg)](https://gitter.im/pol-chat/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

基于[fastapi](https://github.com/tiangolo/fastapi)的API server

后端使用mysql和redis

文档详情见[https://trim21.github.io/pol/](https://trim21.github.io/pol/)

## convert markdown to bbcode

<https://www.trim21.cn/md2bbc>

由于bbcode不支持行内代码，所以将其转换为粗体

## 在看番剧的iCalendar格式日历

`https://www.trim21.cn/api.v1/calendar/bgm.tv/{user_id}`

根据`https://api.bgm.tv/user/{user_id}/collection?cat=watching`生成，
所以不会排除已完结的番剧和未开播的番剧

todo:

- [ ] qq
- [ ] youku
- [ ] acfun


Start worker:

```bash
python -m celery worker -A app.worker -l info -c 5
```

Start Server:

```bash
gunicorn -c /etc/gunicorn.py app.fast:app
```
