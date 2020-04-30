# 前言

基于Djangi搭建的web网站。(Python3.6+Pycharm2019.2+Mysql8.0+Djang3.0)

> 🔥 ：项目目前提供基础web网站功能，后续会持续更新。

1. 认证授权
2. 日志打印
3. 异常处理
4. 事务
5. 参数校验
6. 文件操作
7. 服务器静态资源访问
8. ssh连接服务器执行命令
9. 用户管理
9. 企业管理
-------

目前的项目结构如下：

```
[-] xxx
  ├──[-] django_web-web-auth      // token简单加密解密及认证和授权 。
  ├──[-] django_web-web-common    // 全局异常声明及异常处理，自定义日志处理，格式转换工具 。
  ├──[-] django_web-web.admin     // 后台管理系统数据显示。
  ├──[-] django_web-web.models    // 数据库表定义。
  ├──[-] django_web-web.urls      // 路由。
  ├──[-] django_web-web.views     // 视图。
```

## 使用的主要框架
| 框架 | 说明 |  版本 |
| --- | --- | --- |
| [Django](https://www.djangoproject.com/) | 主框架 | 3.0.5 |
| [paramiko](http://www.paramiko.org/) | 使用使用SSHv2协议连接服务器 | 2.7.1 |
| [pymysql](https://pypi.org/project/PyMySQL/) | 连接mysql数据库 | 0.9.3 |
| [djangorestframework](https://www.django-rest-framework.org/) | 可以帮我们快速开发出一个遵循restful规范的程序 | 3.11.0 |

#### 搭建django项目流程
#####
    1.创建项目命令：django-admin startproject FirstDjango
    2.创建应用命令：python manage.py startapp booktest
    3.执行python manage.py makemigrations生成迁移，生成sql脚本
    4.执行迁移,根据迁移文件创建表：python manage.py migrate
    5.创建超级管理员：python manage.py createsuperuser
    6.启动服务：python manage.py runserver
    7.浏览器输入：http://127.0.0.1:8000/admin，使用自己创建的超级管理员登录（这是后台管理系统）
    8.浏览器输入http://127.0.0.1:8000/sys/login使用初始账户admin,admin登录，之后所有请求带上登录生成的token即可
    
