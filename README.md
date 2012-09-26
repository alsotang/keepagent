KeepAgent
=

[GoAgent](https://github.com/goagent/goagent)'s code is dirty and messy, so let's KeepAgent.

使用方法
==

**目前只有源文件形式的Python版本**

1. 把server文件夹里面的app.yaml里面的application字段改为你的appid，并部署上传。
1. 在浏览器中导入client目录下的CA.crt，再将config.py中的appid改为你的appid。
1. 打开keepagent.py，将浏览器的代理端口设置为7808，即可。
