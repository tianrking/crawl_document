### JSRPC服务



![image-20211112143036503](C:\Users\Tuling\AppData\Roaming\Typora\typora-user-images\image-20211112143036503.png)





开源点：https://github.com/virjar/sekiro



#### 一键安装服务端



#### docker安装

更新APT源

```python
sudo apt-get update
```

安装 apt 依赖包，用于通过HTTPS来获取仓库

```python
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
```

设置稳定仓库

```python
sudo add-apt-repository \
   "deb [arch=amd64] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/ \
  $(lsb_release -cs) \
  stable"
```

docker安装

```python
sudo apt-get install docker-ce
```



+ 搭建sekiro容器

```python
sudo docker run --restart=always --name sekiro-server -p 5600:5600 -p 5601:5601 -p 5602:5602 -p 5603:5603 -d registry.cn-beijing.aliyuncs.com/virjar/sekiro-server:latest
```



下面这样就是成功了

![图片](https://mmbiz.qpic.cn/mmbiz_png/icBZkwGO7uH7vcSuwicBqBuPKxB4ljiaGVuxzW5PFq0owicYO7s7XpiadOk3tUeFo5wedHdgd4H4U9dcH1CdqX5kDCQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)





**3.测试 sekiro 服务是否开启**

浏览器访问**ip:5602**,有这个界面就是成功了，失败原因大部分就是服务器防火墙没有设置开启5600，5601，5602，5603端口

![image-20211112145450609](C:\Users\Tuling\AppData\Roaming\Typora\typora-user-images\image-20211112145450609.png)



### 测试使用

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>

<script src="http://file.virjar.com/sekiro_web_client.js?_=123">
</script>
<script>
        function guid() {
            function S4() {
                  return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
            }
            return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
        }

        var client = new SekiroClient("ws://101.200.62.28:5603/websocket?group=test&clientId="+guid());
        client.registerAction("clientTime",function(request, resolve,reject ){
            resolve(""+new Date());
        })

</script>
</body>
</html>

```

**表示注入成功**

![image-20211112150546090](C:\Users\Tuling\AppData\Roaming\Typora\typora-user-images\image-20211112150546090.png)



**服务端调用测试**

```python
# encoding: utf-8
"""
@author: 夏洛
@QQ: 1972386194
@file: tests.py
"""
import requests
data = {"group": "test",
        "action": "clientTime",
        }
res = requests.get("http://101.200.62.28:5601/asyncInvoke",params=data )
print(res.text)
```

**测试效果**

![image-20211112150630088](C:\Users\Tuling\AppData\Roaming\Typora\typora-user-images\image-20211112150630088.png)



### 案例1

**可以扣JS代码**

```js
/*
  Copyright (C) 2020 virjar <virjar@virjar.com> for https://github.com/virjar/sekiro

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/


function SekiroClient(wsURL) {
    this.wsURL = wsURL;
    this.handlers = {};
    this.socket = {};
    this.base64 = false;
    // check
    if (!wsURL) {
        throw new Error('wsURL can not be empty!!')
    }
    this.webSocketFactory = this.resolveWebSocketFactory();
    this.connect()
}

SekiroClient.prototype.resolveWebSocketFactory = function () {
    if (typeof window === 'object') {
        var theWebSocket = window.WebSocket ? window.WebSocket : window.MozWebSocket;
        return function (wsURL) {

            function WindowWebSocketWrapper(wsURL) {
                this.mSocket = new theWebSocket(wsURL);
            }

            WindowWebSocketWrapper.prototype.close = function () {
                this.mSocket.close();
            };

            WindowWebSocketWrapper.prototype.onmessage = function (onMessageFunction) {
                this.mSocket.onmessage = onMessageFunction;
            };

            WindowWebSocketWrapper.prototype.onopen = function (onOpenFunction) {
                this.mSocket.onopen = onOpenFunction;
            };
            WindowWebSocketWrapper.prototype.onclose = function (onCloseFunction) {
                this.mSocket.onclose = onCloseFunction;
            };

            WindowWebSocketWrapper.prototype.send = function (message) {
                this.mSocket.send(message);
            };

            return new WindowWebSocketWrapper(wsURL);
        }
    }
    if (typeof weex === 'object') {
        // this is weex env : https://weex.apache.org/zh/docs/modules/websockets.html
        try {
            console.log("test webSocket for weex");
            var ws = weex.requireModule('webSocket');
            console.log("find webSocket for weex:" + ws);
            return function (wsURL) {
                try {
                    ws.close();
                } catch (e) {
                }
                ws.WebSocket(wsURL, '');
                return ws;
            }
        } catch (e) {
            console.log(e);
            //ignore
        }
    }
    //TODO support ReactNative
    if (typeof WebSocket === 'object') {
        return function (wsURL) {
            return new theWebSocket(wsURL);
        }
    }
    // weex 鍜� PC鐜鐨剋ebsocket API涓嶅畬鍏ㄤ竴鑷达紝鎵€浠ュ仛浜嗘娊璞″吋瀹�
    throw new Error("the js environment do not support websocket");
};

SekiroClient.prototype.connect = function () {
    console.log('sekiro: begin of connect to wsURL: ' + this.wsURL);
    var _this = this;
    // 涓峜heck close锛岃
    // if (this.socket && this.socket.readyState === 1) {
    //     this.socket.close();
    // }
    try {
        this.socket = this.webSocketFactory(this.wsURL);
    } catch (e) {
        console.log("sekiro: create connection failed,reconnect after 2s");
        setTimeout(function () {
            _this.connect()
        }, 2000)
    }

    this.socket.onmessage(function (event) {
        _this.handleSekiroRequest(event.data)
    });

    this.socket.onopen(function (event) {
        console.log('sekiro: open a sekiro client connection')
    });

    this.socket.onclose(function (event) {
        console.log('sekiro: disconnected ,reconnection after 2s');
        setTimeout(function () {
            _this.connect()
        }, 2000)
    });
};

SekiroClient.prototype.handleSekiroRequest = function (requestJson) {
    console.log("receive sekiro request: " + requestJson);
    var request = JSON.parse(requestJson);
    var seq = request['__sekiro_seq__'];

    if (!request['action']) {
        this.sendFailed(seq, 'need request param {action}');
        return
    }
    var action = request['action'];
    if (!this.handlers[action]) {
        this.sendFailed(seq, 'no action handler: ' + action + ' defined');
        return
    }

    var theHandler = this.handlers[action];
    var _this = this;
    try {
        theHandler(request, function (response) {
            try {
                _this.sendSuccess(seq, response)
            } catch (e) {
                _this.sendFailed(seq, "e:" + e);
            }
        }, function (errorMessage) {
            _this.sendFailed(seq, errorMessage)
        })
    } catch (e) {
        console.log("error: " + e);
        _this.sendFailed(seq, ":" + e);
    }
};

SekiroClient.prototype.sendSuccess = function (seq, response) {
    var responseJson;
    if (typeof response == 'string' ) {
        try {
            responseJson = JSON.parse(response);
        } catch (e) {
            responseJson = {};
            responseJson['data'] = response;
        }
    } else if (typeof response == 'object') {
        responseJson = response;
    } else {
        responseJson = {};
        responseJson['data'] = response;
    }

    if (typeof response == 'string' ) {
         responseJson = {};
        responseJson['data'] = response;
    }

    if (Array.isArray(responseJson)) {
        responseJson = {
            data: responseJson,
            code: 0
        }
    }

    if (responseJson['code']) {
        responseJson['code'] = 0;
    } else if (responseJson['status']) {
        responseJson['status'] = 0;
    } else {
        responseJson['status'] = 0;
    }
    responseJson['__sekiro_seq__'] = seq;
    var responseText = JSON.stringify(responseJson);
    console.log("response :" + responseText);


    if (responseText.length < 1024 * 6) {
        this.socket.send(responseText);
        return;
    }

    if (this.base64) {
        responseText = this.base64Encode(responseText)
    }

    //澶ф姤鏂囪鍒嗘浼犺緭
    var segmentSize = 1024 * 5;
    var i = 0, totalFrameIndex = Math.floor(responseText.length / segmentSize) + 1;

    for (; i < totalFrameIndex; i++) {
        var frameData = JSON.stringify({
                __sekiro_frame_total: totalFrameIndex,
                __sekiro_index: i,
                __sekiro_seq__: seq,
                __sekiro_base64: this.base64,
                __sekiro_is_frame: true,
                __sekiro_content: responseText.substring(i * segmentSize, (i + 1) * segmentSize)
            }
        );
        console.log("frame: " + frameData);
        this.socket.send(frameData);
    }
};

SekiroClient.prototype.sendFailed = function (seq, errorMessage) {
    if (typeof errorMessage != 'string') {
        errorMessage = JSON.stringify(errorMessage);
    }
    var responseJson = {};
    responseJson['message'] = errorMessage;
    responseJson['status'] = -1;
    responseJson['__sekiro_seq__'] = seq;
    var responseText = JSON.stringify(responseJson);
    console.log("sekiro: response :" + responseText);
    this.socket.send(responseText)
};

SekiroClient.prototype.registerAction = function (action, handler) {
    if (typeof action !== 'string') {
        throw new Error("an action must be string");
    }
    if (typeof handler !== 'function') {
        throw new Error("a handler must be function");
    }
    console.log("sekiro: register action: " + action);
    this.handlers[action] = handler;
    return this;
};

SekiroClient.prototype.encodeWithBase64 = function () {
    this.base64 = arguments && arguments.length > 0 && arguments[0];
};

SekiroClient.prototype.base64Encode = function (s) {
    if (arguments.length !== 1) {
        throw "SyntaxError: exactly one argument required";
    }

    s = String(s);
    if (s.length === 0) {
        return s;
    }

    function _get_chars(ch, y) {
        if (ch < 0x80) y.push(ch);
        else if (ch < 0x800) {
            y.push(0xc0 + ((ch >> 6) & 0x1f));
            y.push(0x80 + (ch & 0x3f));
        } else {
            y.push(0xe0 + ((ch >> 12) & 0xf));
            y.push(0x80 + ((ch >> 6) & 0x3f));
            y.push(0x80 + (ch & 0x3f));
        }
    }

    var _PADCHAR = "=",
        _ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
        _VERSION = "1.1";//Mr. Ruan fix to 1.1 to support asian char(utf8)

    //s = _encode_utf8(s);
    var i,
        b10,
        y = [],
        x = [],
        len = s.length;
    i = 0;
    while (i < len) {
        _get_chars(s.charCodeAt(i), y);
        while (y.length >= 3) {
            var ch1 = y.shift();
            var ch2 = y.shift();
            var ch3 = y.shift();
            b10 = (ch1 << 16) | (ch2 << 8) | ch3;
            x.push(_ALPHA.charAt(b10 >> 18));
            x.push(_ALPHA.charAt((b10 >> 12) & 0x3F));
            x.push(_ALPHA.charAt((b10 >> 6) & 0x3f));
            x.push(_ALPHA.charAt(b10 & 0x3f));
        }
        i++;
    }

    switch (y.length) {
        case 1:
            var ch = y.shift();
            b10 = ch << 16;
            x.push(_ALPHA.charAt(b10 >> 18) + _ALPHA.charAt((b10 >> 12) & 0x3F) + _PADCHAR + _PADCHAR);
            break;

        case 2:
            var ch1 = y.shift();
            var ch2 = y.shift();
            b10 = (ch1 << 16) | (ch2 << 8);
            x.push(_ALPHA.charAt(b10 >> 18) + _ALPHA.charAt((b10 >> 12) & 0x3F) + _ALPHA.charAt((b10 >> 6) & 0x3f) + _PADCHAR);
            break;
    }
    return x.join("");
};


 function guid() {
            function S4() {
                  return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
            }
            return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
        }

        var client = new SekiroClient("ws://101.200.62.28:5603/websocket?group=xl&clientId="+guid());
         client.registerAction("xl1",function(request, resolve,reject ){
             // 创建请求参数
    let sDataParams = {
        "tag_id": request['t_id'],
        "page": request['page']
    };
    // 创建ajax请求
    $.ajax({
      // 请求地址
      url: "/api/",  // url尾部需要添加/
      // 请求方式
      type: "GET",
      data: sDataParams,
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res['status'] === 0) {
          iTotalPage = res.data.total_pages;  // 后端传过来的总页数
            resolve(res);
          // if (iPage === 1) {
          //   $(".news-list").html("")
          // }
        // // 需要修改 href  接收后台传来的id号 响应详情页  /news/${one_news.id}/

        } else {
          // 登录失败，打印错误信息
          console.log('服务器错误')
        }
      })
      .fail(function () {
        console.log('服务器超时，请重试！');
      });
        });
```



### 案例2

**暴露X头条数据**

[Tampermonkey](https://links.jianshu.com/go?to=https%3A%2F%2Ftampermonkey.net%2F)是一款免费的浏览器扩展和最为流行的用户脚本管理器，它适用于 Chrome, Microsoft Edge, Safari, Opera Next, 和 Firefox。
 以上是油猴官网给出的介绍。它可以让用户自行在添加脚本，并在开启对应页面时应用。如果你了解"**脚本注入**"，你可以把它认为是一个给自己注入脚本的一个工具。



```js
// ==UserScript==
// @name         toutiao
// @namespace    https://www.toutiao.com/
// @version      0.1
// @description  toutiao hook
// @author       artio
// @match        https://www.toutiao.com/*
// @grant        none
// @require      https://sekiro.virjar.com/sekiro-doc/assets/sekiro_web_client.js
// ==/UserScript==

(function () {
    'use strict';
    function guid() {
        function S4() {
            return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
        }

        return (S4() + S4() + "-" + S4() + "-" + S4() + "-" + S4() + "-" + S4() + S4() + S4());
    }

    var client = new SekiroClient("wss://www.artio.top/websocket?group=ws-group-toutiao&clientId=" + guid());

    /* 自定义函数 */

    client.registerAction("toutiao", function (request, resolve, reject) {
        var url = request['url'];
        if (!url){
            reject("url 不能为空")
        }
        resolve({"signature": window.byted_acrawler.sign({url}), "cookie": document.cookie})
    })
})();
```



 **python代码编写**

```python
# encoding: utf-8
"""
@author: 夏洛
@QQ: 1972386194
@file: 案例1.py
"""
import urllib3,requests
urllib3.disable_warnings()

def get_sig(url):
    data = {
        "group": "ws-group-toutiao",
        "action": "toutiao",
        "url": url
    }
    res = requests.post(url="https://www.artio.top/asyncInvoke", data=data, verify=False)
    resp = res.json()['data']
    if "?" in url:
        url += "&_signature={}".format(resp['signature'])
    else:
        url += "?_signature={}".format(resp['signature'])
    return url

url = get_sig('https://www.toutiao.com/api/pc/list/feed?channel_id=0&min_behot_time=1636703275&refresh_count=2&category=pc_profile_recommend')
print(url)

session = requests.session()
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
    "cache-control": "no-cache",
    "cookie": "csrftoken=76b07f1ddde794047ce1a9596b8d9cd5; tt_webid=6998060616079427085; MONITOR_DEVICE_ID=9a97434e-0921-4314-87e1-d8993030de95; passport_csrf_token_default=40a1bb3ba2efeb0e5e36f94c99727f0f; passport_csrf_token=40a1bb3ba2efeb0e5e36f94c99727f0f; s_v_web_id=verify_kvjkv9pc_hDvLCeuF_Udln_4D3v_8eLo_o9jlFRWlp8il; MONITOR_WEB_ID=6998060616079427085; _tea_utm_cache_2018=undefined; __ac_nonce=0618e1783005398094567; __ac_signature=_02B4Z6wo00f01Kj2HvQAAIDBg3xFMi6qJcCo0hpAAEu4sbmUaB8mgClKNH7BVI7zQAILlm9g6al1RhnpqK27dyGnxPme6zz-z1vg.d8QlZJpcmGk5PXUliFYDS27XCl0nDUdJ8XU2xO.SiIRa0; ttwid=1%7CJH6gxT3CCOAVW55PX_5q_ckRprSB_FKBNcFtLOeV1ys%7C1636702085%7Cc561194815f706ef718da803b578da0b40553adc4e09dd3413b3f1ee4654f649; tt_scid=8bYQjCVcxNz6qPABuRQdIFseSpa7NC2ly4wbfFx3XblQ7sz77NZeuc33KRvIfoT22e9c",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Chromium\";v=\"94\", \"Google Chrome\";v=\"94\", \";Not A Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
}
res = session.get(url,headers=headers)
if res.status_code == 200:
    if res.json().get('message') == 'success':
        items = res.json().get('data')
        for i in items:
            title = i.get('title')
            print(title)

```



### 作业

使用RPC技术重写上节课案例16题

提供数据截图便可











