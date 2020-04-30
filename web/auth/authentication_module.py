# @Time : 2020/4/27 22:39 
# @Author : lixiang
# @File : authentication_module.py 
# @Software: PyCharm
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission

from rest_framework.exceptions import NotAuthenticated, PermissionDenied
# get_token生成加密token,out_token解密token
from web.models import User, roleToResource, Resource, UserToken, userToRole
from web.auth.rc4_decode import rc4_decode_main

secretkey = "ZlOWJhY2Q5NjMyMWU3NTdiYjAyYzY2Ng=="
expire = 3600

# 存储在前端的token解密比对
class TokenAuth2(BaseAuthentication):
    def authenticate(self,request):
        if request.method == 'GET':
            token = request.GET.get("token")
        else:
            token=request.data.get("token")
        print(token)
        token_obj=rc4_decode_main(secretkey,token)
        user_token = UserToken.objects.filter(accName=token_obj).first()
        if token_obj:
            #print(time.mktime(user_token.created) )
            # if user_token.created + 3600 < int(time.time()):
            #     raise NotAuthenticated("用户信息已过期，请重新登录")
            return
        else:
            raise NotAuthenticated("你没有登入")


class IsAuthenticate2(BasePermission):
    def has_permission(self, request, permissionCode):
        if request.method == 'GET':
            token = request.GET.get("token")
        else:
            token=request.data.get("token")
        print(token)
        accName = rc4_decode_main(secretkey, token)
        curruser = User.objects.filter(accName = accName).first()
        user_to_role = userToRole.objects.filter(user_id = curruser.id)
        for u_to_r in user_to_role:
            roleToResourceS = roleToResource.objects.filter(role_id=u_to_r.role_id)
            for roleToRes in roleToResourceS:
                permission = Resource.objects.get(id=roleToRes.resource_id)
                if permissionCode == permission.perms:
                    return
        raise PermissionDenied("你没有权限")