# 部署文档

## 环境依赖

* python3.7+
* node.js
* gitbook (可选，用于文档项目)
* thrift
* mysql

## 依赖包安装

以下命令都是从项目根目录开始，下同。

```
pip install -r requirements.txt
cd Web
npm install
```

## 开发模式部署

### 计算服务

```
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/DCServer
cd DCServer
python3 CalcServer.py
```

### 后端服务

第一次运行要初始化

```
cd DCServerDjango
python3 manage.py migrate
python3 manege.py collectstatic
```

```
cd DCServerDjango
python3 manage.py runserver 0.0.0.0:6566
```

### 前端服务

```
cd Web
npm run dev
```

### 文档服务

```
cd Document
gitbook serve
```

## 生产环境部署

### 计算服务

同上
```
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/DCServer
cd DCServer
python3 CalcServer.py
```

### 后端服务

采用uwsgi部署，并使用nginx反向代理。

配置文件依环境而异，下面是一个例子。
```
[uwsgi]
env = PYTHONPATH=$PYTHONPATH:/home/wuxian/repos/DiachronicCorpus:/home/wuxian/repos/DiachronicCorpus/DCServer
# Django-related settings
# the django project directory (full path)
chdir = /home/wuxian/repos/DiachronicCorpus/DCServerDjango
# Django's wsgi file
module = DCServerDjango.wsgi
# process-related settings
# master
master = true
# maximum number of worker processes
processes = 6

threads = 24
enable-threads = True
max-requests = 6000
buffer-size = 65536

socket=%(chdir)/prod.sock
# ... with appropriate permissions - may be needed
chmod-socket = 664

# clear environment on exit
disable-logging = true
vacuum  = true
stats = %(chdir)/logs/uwsgi/uwsgi.status
pidfile = %(chdir)/logs/uwsgi/uwsgi.pid
daemonize = %(chdir)/logs/uwsgi/uwsgi.log
env=LC_ALL=zh_CN.UTF-8
```

```
cd DCServerDjango
uwsgi --ini prod_config.ini
```

然后在nginx中配置相应的server。

```
server {
        listen 6567;
        charset utf-8;
        location /static/ {
            autoindex on;
            alias /home/wuxian/repos/DiachronicCorpus/DCServerDjango/collectedstatic/;
        }
        location / {
                uwsgi_pass unix:///home/wuxian/repos/DiachronicCorpus/DCServerDjango/prod.sock;
                include /home/wuxian/repos/DiachronicCorpus/DCServerDjango/uwsgi_params;
                uwsgi_read_timeout 300;
        }
}
```

### 前端服务

```
cd Web
npm run build
```

下面要用nginx提供服务，主页地址为dist/index.html。

```
server {
        listen 7070;
        server_name localhost;


        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
        root html;
        }


        root /home/wuxian/repos/DiachronicCorpus/Web/dist;
        index index.html;


        location / {
        try_files $uri $uri/ @router;
        index index.html;
        }


        location @router {
        rewrite ^.*$ /index.html last;
        }
}
```

### 文档服务

```
cd Document
gitbook build
```

nginx配置如下

```
server {
        listen 4000;
        server_name localhost;


        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
        root html;
        }


        root /home/wuxian/repos/DiachronicCorpus/Document/_book;
        index index.html;


        location / {
        try_files $uri $uri/ @router;
        index index.html;
        }


        location @router {
        rewrite ^.*$ /index.html last;
        }
}
```