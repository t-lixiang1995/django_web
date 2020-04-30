# @Time : 2020/4/28 11:11 
# @Author : lixiang
# @File : urls.py 
# @Software: PyCharm
from django.urls import path,re_path

from django.views.static import serve

from web.views import AuthLogin, Users, nav, currentUser, delUser, getUser, addUser, editUser, addEnterprise, \
    editEnterprise, delEnterprise, getEnterprise, Enterprises, downLoad, upLoad

urlpatterns = [
    path('sys/login', AuthLogin.as_view()),
    path('sys/menu/nav', nav.as_view()),
    # 服务器静态图片展示
    re_path(r'^imgs/(?P<path>.*)$', serve, {'document_root':'C:/Users/pcitc/PycharmProjects/django_web/imgs'}),
    # 文件操作相关接口
    re_path(r'^sys/download/(?P<file_name>.*)$', downLoad.as_view()),
    path('sys/upload',upLoad.as_view()),
    # 用户管理相关接口
    path('modules/usermanage/list',Users.as_view()),
    path('modules/usermanage/curuserInfo',currentUser.as_view()),
    path('modules/usermanage/delete',delUser.as_view()),
    path('modules/usermanage/info',getUser.as_view()),
    path('modules/usermanage/save',addUser.as_view()),
    path('modules/usermanage/update',editUser.as_view()),
    # 企业管理相关接口
    path('modules/enterprise/save',addEnterprise.as_view()),
    path('modules/enterprise/update',editEnterprise.as_view()),
    path('modules/enterprise/delete',delEnterprise.as_view()),
    path('modules/enterprise/info',getEnterprise.as_view()),
    path('modules/enterprise/list',Enterprises.as_view()),
]