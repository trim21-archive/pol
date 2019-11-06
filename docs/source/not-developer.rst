非开发者使用的API
=================

markdown转BBCode
------------------

`<https://www.trim21.cn/md2bbc>`_

.. warning::

   由于bbcode不支持行内代码，所以行内代码会被转换为粗体

导出在看番剧的可订阅日历
---------------------------

``https://www.trim21.cn/api.v1/calendar/bgm.tv/{user_id}``

将 ``{user_id}`` 替换为你的user_id, 在个人主页的网址中可以找到.

根据 ``https://api.bgm.tv/user/{user_id}/collection?cat=watching`` 生成,
所以不会排除已完结的番剧和未开播的番剧
