# 历时语料库后端教程项目
## 初始化项目
```shell
django-admin startproject DCServerTutorial
django-admin startapp entry_editor
```

## 修改settings.py
在`INSTALLED_APPS`中加入`rest_framework`和我们刚刚创建的`entry_editor`。

## 模型定义与数据库
在`entry_editor/models.py`中加入`EntryEditor`对象的定义。

```shell
python3 manage.py makemigrations
python3 manage.py migrate
```

此时我们使用的是sqlite作为数据库后端。如果想要采用其他数据库（比如mysql），需要在settings.py中做相应的改动。

## Serializer定义
默认的Django环境是没有Serializer这个概念的，所以我们需要手动创建这个文件。

因为我们希望在List和Retrieve时采用不同的序列化器，所以我们创建了两个。分别是`EntryEditorSerializer`和`EntryEditorListSerializer`。

区别在于，前者对`cells`中的内容也做了序列化，而后者无需显示这个字段。

## ViewSet定义
在`entry_editor/views.py`中定义一个视图，用来完成我们对EntryEditor的各种操作。

在目前的简化版系统中，我们只需要支持create, retrieve, list, update和destroy动作就可以了。

不用担心，这些动作都是在ModelViewSet中定义好的，我们只需要继承这个ViewSet，并且重写一些业务逻辑即可。

在这里我们还加入了简单的对于filter、queryset、serializer_class的设置。

## 简单说下View
在上一步，我们直接跳过了原生Django中对view的定义，以及对GenericViewSet的介绍。在这里还是做一个简单的补充。

简单来说，一个View就对应着我们访问的一个（多个）HTTP动词+一个URL pattern。而由于RESTful API对于资源和动词的定义，只要我们的业务是符合框架的定义的，就可以采用默认的view来简化开发。

可以看到，在ViewSet中，我们先通过成员变量将一个viewset与一个model建立起了联系，也与一个（多个）序列化器建立了联系。这样一来，ModelViewSet将会为我们加入许多默认的动作。（django rest framework是通过mixin的方式扩展一个基类的动作的）。

## URL注册
最后，我们只需要将viewset注册进来就可以访问了。

为了单独管理每个app的url，我们首先在`entry_editor`中再创建一个`urls.py`，并将viewset注册进来。

最后在全局的`urls.py`中将每个app的url再引入进来就可以了。

## 运行测试服务器

```shell
python3 manage.py runserver
```
在默认端口8000可以访问到我们的网站了。但是因为我们没有主页，所以返回的是404的页面。因为是开发模式，我们可以看到所有合法的URL，访问entryeditor即可。

DRF为我们提供了一个简单的可视化页面用来查看各种API并且测试它们。

## 小结
这一次我们创建了一个最简化的系统。遵循这个教程走下来，你可以对DRF是如何将网络请求与数据库操作建立起联系的。

后续我们将会介绍更多内容，包括自定义动作、登录设置、权限认证、前后端协同、swagger的使用等。