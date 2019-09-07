==========
用户认证
==========

目前有两个授权的api, 一个是我用户脚本使用的(并没有在文档中表明), 另一个是给客户端使用的.

客户端将用户转跳到 `/auth/api.v1/bgm.tv_auth <#get--auth-api.v1-bgm.tv_auth>`_,
在用户使用bgm.tv授权后会转跳到
`/auth/api.v1/bgm.tv_oauth_callback <#get--auth-api.v1-bgm.tv_oauth_callback>`_

.. note::

    每个session的起始有效期为30天, 每次这个session被用于进行身份认证时,
    会延长14天的session过期时间

.. openapi:: ./openapi.json
   :format: markdown
   :paths:
      /auth/api.v1/bgm.tv_auth


.. openapi:: ./openapi.json
   :format: markdown
   :paths:
      /auth/api.v1/bgm.tv_oauth_callback
