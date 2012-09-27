KeepAgent
=

[GoAgent](https://github.com/goagent/goagent)'s code is dirty and messy, so let's KeepAgent.

KeepAgent只专注GAE平台以及HTTP代理，希望以简洁而不失效率的代码，让初学HTTP协议或是对于Python有兴趣的同学可以从中借鉴和学习。

**[注意]以下内容几乎都是为KeepAgent Python版本而写**

简易使用方法
==

1. 把server文件夹里的app.yaml里的application字段改为你的appid，并部署至GAE。
1. 在浏览器中导入client目录下的CA.crt，再将config.py中的appid改为你的appid。
1. 运行keepagent.py，将浏览器的代理端口设置为7808，即可。

安全性
===

由于https连接比较消耗资源影响速度，而使用KeepAgent的朋友大部分都是直接在与自己搭建server端打交道的，所以KeepAgent内置了AES对称加密的机制，使机密内容得到加密但速度不受太大影响。KeepAgent只会自动加密https请求，对于http请求不进行加密。

设置方法：

1. 下载并编译安装[pycrypto 2.6](https://www.dlitz.net/software/pycrypto/)
2. 打开client/lib.py，为crypt_key赋值一个32字节的字符串。（可以通过运行client/cipher.py来获得一个随机32字节的字符串）
3. 重新上传server文件夹至GAE。即可。
