=============================
关联视频网站和bgm.tv条目
=============================

目前支持的网站
==============

.. autoclass:: app.video_website_spider.SupportWebsite
   :members:


通过视频网站查询对应条目

``bangumi_id`` 在不同网站中


针对bgm.tv条目获取视频网站播放地址和反向查询

根据条目id获取播放地址
=======================

具体相应见OpenAPI文档

.. http:get:: /bgm.tv/api.v0/subject/player/{subject_id}

   会返回目前记录中的各个网站的播放地址, 不包括单集播放地址

   :param subject_id: bgm对应的条目id
   :type subject_id: int



.. http:get:: /bgm.tv/api.v0/ep/player/{ep_id}

   :param ep_id: bgm对应的单集id
   :type ep_id: int



提交数据
==========

bilibili
--------

提交条目体播放地址
~~~~~~~~~~~~~~~~~~~~

可以针对条目提交合集的首页(``https://www.bilibili.com/bangumi/media/md{media_id}/``)
或者其中任何一集的地址(``https://www.bilibili.com/bangumi/play/ep{ep_id}``)

.. warning::

   还有一个 ``https://www.bilibili.com/bangumi/play/ss{season_id}/`` 这样的地址,
   我还没完工, 暂时还不能提交

提交单集播放地址
~~~~~~~~~~~~~~~~~

只能提交具体单集的地址 ``https://www.bilibili.com/bangumi/play/ep{ep_id}``

爱奇艺
------

提交条目体播放地址
~~~~~~~~~~~~~~~~~~~~

合集的播放地址为 ``https://www.iqiyi.com/a_19rrh1ss1p.html`` 以 ``a_`` 开头,
``a_19rrh1ss1p`` 为视频id

提交单集播放地址
~~~~~~~~~~~~~~~~~

单集的播放地址为 ``https://www.iqiyi.com/v_19rro8bme0.html`` 以 ``v_`` 开头,
``v_19rro8bme0`` 为视频id
