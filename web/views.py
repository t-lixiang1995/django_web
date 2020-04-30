# @Time : 2020/4/28 11:12 
# @Author : lixiang
# @File : views.py 
# @Software: PyCharm
import os
import time

import paramiko
from datetime import datetime

from django.db import transaction
from django.http import HttpResponse, StreamingHttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from web.auth.authentication_module import TokenAuth2, IsAuthenticate2
from web.auth.rc4_decode import rc4_decode_main
from web.auth.rc4_encode import rc4_encde_main
from web.common.MyLogger import Logger
from web.common.errors import ValidationError, NotFoundError
from web.models import UserToken, Last_Online, Enterprise, User, userToRole, Role, roleToResource, Resource, Server

secretkey = "ZlOWJhY2Q5NjMyMWU3NTdiYjAyYzY2Ng=="

# 用户登录
class AuthLogin(APIView):
    @transaction.atomic
    def post(self,request):
        response={
            "code": 0,
            "msg": "success"
        }
        if 'accName' not in request.data or request.data.get("accName") is "":
            raise ValidationError("参数不能为空")
        accName = request.data.get("accName")
        if 'password' not in request.data or request.data.get("password") is "":
            raise ValidationError("参数不能为空")
        password = request.data.get("password")
        try:
            user=User.objects.filter(accName=accName,password=password).first()
            if user:
                sid = transaction.savepoint()  # 开启事务
                last_login = Last_Online.objects.filter(accName=accName).first()
                if last_login:
                    last_login.last_login_time = datetime.now()
                    last_login.login_count = last_login.login_count + 1
                    last_login.save()
                else:
                    new_last_login = Last_Online()
                    new_last_login.accName = accName
                    new_last_login.userName = user.userName
                    new_last_login.last_login_time = datetime.now()
                    new_last_login.login_count = 1
                    new_last_login.save()
                token=rc4_encde_main(secretkey,accName)
                #UserToken.objects.update_or_create(token=token,defaults={'accName':user.accName},)
                user_token = UserToken.objects.filter(accName=accName).first()
                if user_token:
                    user_token.token = token
                else:
                    new_user_token = UserToken()
                    new_user_token.accName = accName
                    new_user_token.token = token
                    new_user_token.save()
                try:
                    transaction.savepoint_commit(sid) # 提交
                except Exception as ie:
                    Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (accName, ie))
                    transaction.savepoint_rollback(sid) # 回滚
                response["msg"]="登入成功"
                response["token"]=token
                response["accName"]=user.accName
            else:
                response["msg"]="用户名或密码错误"
            return Response(response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[登录异常]accName:【%s】%s" % (accName, e))
            response["code"] = 500
            response["msg"] = "服务器未知错误"
            return Response(response), 500


#导航菜单
class nav(APIView):
    authentication_classes = [TokenAuth2]
    def get(self,request):
        api_response = {
            "code": 0,
            "msg": "success"
        }
        token = request.GET.get("token")
        accName = rc4_decode_main(secretkey, token)
        user = User.objects.filter(accName=accName).first()
        if not user:
            raise NotFoundError('该账户不存在')
        try:
            menuList = []
            location = []
            user_to_role = userToRole.objects.filter(user_id=user.id)
            for u_to_r in user_to_role:
                roleToResourceS = roleToResource.objects.filter(role_id=u_to_r.role_id)
                for roleToRes in roleToResourceS:
                    currResource = Resource.objects.filter(id = roleToRes.resource_id).first()
                    if currResource.type is 1:
                        menuList.append(currResource.name)
                        location.append(currResource.url)
            response = dict(menuList = menuList,location = location)
            api_response['result'] = response
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[获取菜单异常]accName:【%s】%s" % ('accName', e))
            api_response["code"] =  500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response),500


#获取当前登录用户信息
class currentUser(APIView):
    authentication_classes = [TokenAuth2]
    def get(self, request):
        IsAuthenticate2.has_permission(self, request, "modules:usermanage:info")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        token = request.GET.get("token")
        accName = rc4_decode_main(secretkey, token)
        user = User.objects.filter(accName=accName).first()
        if not user:
            raise NotFoundError('该账户不存在')
        try:
            data = []
            data.append(dict(accName=user.accName, userID=user.userID, userName=user.userName,
                            accAttr=user.accAttr, etpName=user.etpName, userDP=user.userDP,
                            userMail=user.userMail,userPhone=user.userPhone, userTel=user.userTel))
            response = dict(list=data)
            api_response['result'] = response
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[获取当前用户信息异常]accName:【%s】%s"  % (accName, e))
            api_response["code"] =  500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response),500


#删除指定用户
class delUser(APIView):
    authentication_classes = [TokenAuth2]
    @transaction.atomic
    def get(self, request):
        IsAuthenticate2.has_permission(self, request, "modules:usermanage:delete")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        if 'accName' not in request.GET or request.GET.get("accName") is "":
            raise ValidationError("accName参数不能为空")
        accName = request.GET.get("accName")
        sid = transaction.savepoint()  # 开启事务
        user = User.objects.filter(accName=accName).first()
        if not user:
            raise NotFoundError('删除失败，账户不存在')
        try:
            user.delete()
            try:
                transaction.savepoint_commit(sid) # 提交
            except Exception as ie:
                Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (accName, ie))
                transaction.savepoint_rollback(sid) # 回滚
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[删除用户异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response), 500


#获取指定用户信息
class getUser(APIView):
    authentication_classes = [TokenAuth2]
    def get(self, request):
        IsAuthenticate2.has_permission(self, request, "modules:usermanage:info")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        if 'accName' not in request.GET or request.GET.get("accName") is "":
            raise ValidationError("accName参数不能为空")
        accName = request.GET.get("accName")
        user = User.objects.filter(accName=accName).first()
        if not user:
            raise NotFoundError('该账户不存在')
        try:
            data = []
            data.append(dict(accName=user.accName, userID=user.userID, userName=user.userName,
                             accAttr=user.accAttr, etpName=user.etpName, userDP=user.userDP,
                             userMail=user.userMail, userPhone=user.userPhone, userTel=user.userTel))
            response = dict(list=data)
            api_response['result'] = response
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[获取指定用户信息异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response), 500


# 获取用户列表
class Users(APIView):
    authentication_classes = [TokenAuth2]
    def get(self,request):
        IsAuthenticate2.has_permission(self,request,"modules:usermanage:list")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        token = request.GET.get("token")
        try:
            accName = rc4_decode_main(secretkey, token)
            userList = []
            user_list=User.objects.all()
            for user in user_list:
                userList.append(dict(accName=user.accName, userName=user.userName,
                                userDP=user.userDP, etpName=user.etpName, createTime=user.create_date))
            api_response["data"]=userList
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[获取用户列表异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response), 500


# 新增用户
class addUser(APIView):
    authentication_classes = [TokenAuth2]
    @transaction.atomic
    def post(self, request):
        IsAuthenticate2.has_permission(self, request, "modules:usermanage:save")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        if 'token' not in request.data or request.data.get('token') is "":
            raise ValidationError("参数不能为空")
        token = request.data.get("token")
        if 'accName' not in request.data or request.data.get('accName') is "":
            raise ValidationError("参数不能为空")
        accName = request.data.get('accName')
        if 'password' not in request.data or request.data.get('password') is "":
            raise ValidationError("参数不能为空")
        password = request.data.get('password')
        if 'userID' not in request.data or request.data.get('userID') is "":
            raise ValidationError("参数不能为空")
        userID = request.data.get('userID')
        if 'userName' not in request.data or request.data.get('userName') is "":
            raise ValidationError("参数不能为空")
        userName = request.data.get('userName')
        if 'accAttr' not in request.data or request.data.get('accAttr') is "":
            raise ValidationError("参数不能为空")
        accAttr = request.data.get('accAttr')
        if 'etpName' not in request.data or request.data.get('etpName') is "":
            raise ValidationError("参数不能为空")
        etpName = request.data.get('etpName')
        if 'userDP' not in request.data or request.data.get('userDP') is "":
            raise ValidationError("参数不能为空")
        userDP = request.data.get('userDP')
        if 'userMail' not in request.data or request.data.get('userMail') is "":
            raise ValidationError("参数不能为空")
        userMail = request.data.get('userMail')
        if 'userPhone' not in request.data or request.data.get('userPhone') is "":
            raise ValidationError("参数不能为空")
        userPhone = request.data.get('userPhone')
        if 'userTel' not in request.data or request.data.get('userTel') is "":
            raise ValidationError("参数不能为空")
        userTel = request.data.get('userTel')
        try:
            status = (request.data.get('status') if ('status' in request.data) else 1)
            curr_user = rc4_decode_main(secretkey, token)
            create_user_id = curr_user
            create_date = (request.data.get('create_date') if ('create_date' in request.data) else datetime.now())
            remarks = (request.data.get('remarks') if ('remarks' in request.data) else "")
            sid = transaction.savepoint()  # 开启事务
            newUser = User()
            newUser.accName = accName
            newUser.userID = userID
            newUser.userName = userName
            newUser.userMail = userMail
            newUser.userPhone = userPhone
            newUser.userTel = userTel
            newUser.password = password
            newUser.status = status
            newUser.accAttr = accAttr
            newUser.etpName = etpName
            newUser.userDP = userDP
            newUser.create_date = create_date
            newUser.create_user_id = create_user_id
            newUser.remarks = remarks
            newUser.save()
            try:
                transaction.savepoint_commit(sid) # 提交
            except Exception as ie:
                Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (accName, ie))
                transaction.savepoint_rollback(sid) # 回滚
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[添加用户异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response), 500


# 修改用户信息
class editUser(APIView):
    authentication_classes = [TokenAuth2]
    @transaction.atomic
    def post(self, request):
        IsAuthenticate2.has_permission(self, request, "modules:usermanage:update")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        if 'accName' not in request.data or request.data.get('accName') is "":
            raise ValidationError("参数不能为空")
        accName = request.data.get('accName')
        sid = transaction.savepoint()  # 开启事务
        newUser = User.objects.filter(accName=accName).first()
        if not newUser:
            raise NotFoundError('该账户不存在')
        try:
            if ('userID' in request.data):
                newUser.userID = request.data.get('userID')
            if ('userName' in request.data):
                newUser.userName = request.data.get('userName')
            if ('userMail' in request.data):
                newUser.userMail = request.data.get('userMail')
            if ('userPhone' in request.data):
                newUser.userPhone = request.data.get('userPhone')
            if ('userTel' in request.data):
                newUser.userTel = request.data.get('userTel')
            if ('password' in request.data):
                newUser.password = request.data.get('password')
            if ('status' in request.data):
                newUser.status = request.data.get('status')
            if ('accAttr' in request.data):
                newUser.accAttr = request.data.get('accAttr')
            if ('etpName' in request.data):
                newUser.etpName = request.data.get('etpName')
            if ('userDP' in request.data):
                newUser.userDP = request.data.get('userDP')
            if ('create_date' in request.data):
                newUser.create_date = request.data.get('create_date')
            if ('create_user_id' in request.data):
                newUser.create_user_id = request.data.get('create_user_id')
            if ('remarks' in request.data):
                newUser.remarks = request.data.get('remarks')
            newUser.save()
            try:
                transaction.savepoint_commit(sid) # 提交
            except Exception as ie:
                Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (accName, ie))
                transaction.savepoint_rollback(sid) # 回滚
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[修改用户异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response), 500


# 新增企业
class addEnterprise(APIView):
    authentication_classes = [TokenAuth2]
    @transaction.atomic
    def post(self, request):
        IsAuthenticate2.has_permission(self, request, "modules:enterprise:save")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        if 'token' not in request.data or request.data.get('token') is "":
            raise ValidationError("参数不能为空")
        token = request.data.get("token")
        if 'etpName' not in request.data or request.data.get('etpName') is "":
            raise ValidationError("参数不能为空")
        etpName = request.data.get('etpName')
        if 'LDAPCode' not in request.data or request.data.get('LDAPCode') is "":
            raise ValidationError("参数不能为空")
        LDAPCode = request.data.get('LDAPCode')
        etpCode = LDAPCode + "_" + str(int(time.time() * 10))
        if 'serverInfolist' not in request.data or request.data.get('serverInfolist') is "":
            raise ValidationError("参数不能为空")
        serverInfolist = request.data.get('serverInfolist')
        for serverinfo in serverInfolist:
            if 'serverType' not in serverinfo or serverinfo.get('serverType') is "":
                raise ValidationError("参数不能为空")
            serverType = serverinfo.get('serverType')
        try:
            dhcpServerIP = (request.data.get('dhcpServerIP') if ('dhcpServerIP' in request.data) else "")
            TFTPServerIP = (request.data.get('TFTPServerIP') if ('TFTPServerIP' in request.data) else "")
            FTPServerIP = (request.data.get('FTPServerIP') if ('FTPServerIP' in request.data) else "")
            accName = rc4_decode_main(secretkey, token)
            createAdmin = accName
            createTime = (request.data.get('createTime') if ('createTime' in request.data) else datetime.now())
            sid = transaction.savepoint()  # 开启事务
            newenterprise = Enterprise()
            newenterprise.etpName = etpName
            newenterprise.LDAPCode = LDAPCode
            newenterprise.etpCode = etpCode
            newenterprise.dhcpServerIP = dhcpServerIP
            newenterprise.TFTPServerIP = TFTPServerIP
            newenterprise.FTPServerIP = FTPServerIP
            newenterprise.createAdmin = createAdmin
            newenterprise.createTime = createTime
            newenterprise.save()
            for serverinfo in serverInfolist:
                serverIP = (serverinfo.get('serverIP') if ('serverIP' in serverinfo) else "")
                serverUsername = (serverinfo.get('serverUsername') if ('serverUsername' in serverinfo) else "")
                serverPasswd = (serverinfo.get('serverPasswd') if ('serverPasswd' in serverinfo) else "")
                newServer = Server()
                newServer.etpCode = etpCode
                newServer.serverType = serverType
                newServer.serverIP = serverIP
                newServer.serverUsername = serverUsername
                newServer.serverPasswd = serverPasswd
                newServer.save()
            try:
                transaction.savepoint_commit(sid) # 提交
            except Exception as ie:
                Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (accName, ie))
                transaction.savepoint_rollback(sid) # 回滚
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[添加企业异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response), 500


# 修改企业信息
class editEnterprise(APIView):
    authentication_classes = [TokenAuth2]
    @transaction.atomic
    def post(self, request):
        IsAuthenticate2.has_permission(self, request, "modules:enterprise:update")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        if 'token' not in request.data or request.data.get('token') is "":
            raise ValidationError("参数不能为空")
        token = request.data.get('token')
        accName = rc4_decode_main(secretkey, token)
        if 'etpCode' not in request.data or request.data.get('etpCode') is "":
            raise ValidationError("参数不能为空")
        etpCode = request.data.get('etpCode')
        sid = transaction.savepoint()  # 开启事务
        enterprise = Enterprise.objects.filter(etpCode=etpCode).first()
        if not enterprise:
            raise NotFoundError('该组织机构不存在')
        try:
            updateTime = (request.data.get('updateTime') if ('updateTime' in request.data) else datetime.now())
            enterprise.updateTime = updateTime
            if ('dhcpServerIP' in request.data):
                enterprise.dhcpServerIP = request.data.get('dhcpServerIP')
            if ('etpName' in request.data):
                enterprise.etpName = request.data.get('etpName')
            if ('LDAPCode' in request.data):
                enterprise.LDAPCode = request.data.get('LDAPCode')
            if ('TFTPServerIP' in request.data):
                enterprise.TFTPServerIP = request.data.get('TFTPServerIP')
            if ('FTPServerIP' in request.data):
                enterprise.FTPServerIP = request.data.get('FTPServerIP')
            if ('serverInfolist' in request.data):
                serverInfolist = request.data.get('serverInfolist')
                for server in serverInfolist:
                    serverType = (server.get('serverType') if ('serverType' in server) else 0)
                    serverInfo = Server.objects.filter(etpCode = etpCode, serverType = serverType).first()
                    if not serverInfo:
                        serverIP = (server.get('serverIP') if ('serverIP' in server) else "")
                        serverUsername = (server.get('serverUsername') if ('serverUsername' in server) else "")
                        serverPasswd = (server.get('serverPasswd') if ('serverPasswd' in server) else "")
                        newServer = Server()
                        newServer.etpCode = etpCode
                        newServer.serverType = serverType
                        newServer.serverIP = serverIP
                        newServer.serverUsername = serverUsername
                        newServer.serverPasswd = serverPasswd
                        newServer.save()
                    else:
                        if ('serverIP' in server):
                            serverInfo.serverIP = server.get('serverIP')
                        if ('serverUsername' in server):
                            serverInfo.serverUsername = server.get('serverUsername')
                        if ('serverPasswd' in server):
                            serverInfo.serverPasswd = server.get('serverPasswd')
                        serverInfo.save()
            enterprise.save()
            try:
                transaction.savepoint_commit(sid) # 提交
            except Exception as ie:
                Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (accName, ie))
                transaction.savepoint_rollback(sid) # 回滚
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[修改企业异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response), 500


#删除指定企业
class delEnterprise(APIView):
    authentication_classes = [TokenAuth2]
    @transaction.atomic
    def get(self, request):
        IsAuthenticate2.has_permission(self, request, "modules:enterprise:delete")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        token = request.GET.get("token")
        accName = rc4_decode_main(secretkey, token)
        if 'etpCode' not in request.GET or request.GET.get("etpCode") is "":
            raise ValidationError("etpCode参数不能为空")
        etpCode = request.GET.get("etpCode")
        sid = transaction.savepoint()  # 开启事务
        enterprise = Enterprise.objects.filter(etpCode=etpCode).first()
        if not enterprise:
            raise NotFoundError('删除失败，企业不存在')
        try:
            enterprise.delete()
            server = Server.objects.filter(etpCode = etpCode)
            if server:
                server.delete()
            try:
                transaction.savepoint_commit(sid) # 提交
            except Exception as ie:
                Logger('error.log', level='error').logger.error("[事务提交失败]accName:【%s】%s" % (accName, ie))
                transaction.savepoint_rollback(sid) # 回滚
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[删除企业异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response), 500


#获取指定企业信息
class getEnterprise(APIView):
    authentication_classes = [TokenAuth2]
    def get(self, request):
        IsAuthenticate2.has_permission(self, request, "modules:enterprise:info")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        token = request.GET.get("token")
        accName = rc4_decode_main(secretkey, token)
        if 'etpCode' not in request.GET or request.GET.get("etpCode") is "":
            raise ValidationError("etpCode参数不能为空")
        etpCode = request.GET.get("etpCode")
        enterprise = Enterprise.objects.filter(etpCode=etpCode).first()
        if not enterprise:
            raise NotFoundError('该组织机构不存在')
        try:
            serverinfoList = []
            serverList = Server.objects.filter(etpCode = etpCode)
            if serverList:
                for server in serverList:
                    serverinfoList.append(dict(etpCode=etpCode, serverType=server.serverType, serverIP=server.serverIP,
                                               serverUsername=server.serverUsername, serverPasswd=server.serverPasswd))
            data = dict(etpCode=enterprise.etpCode, etpName=enterprise.etpName, LDAPCode=enterprise.LDAPCode,
                        dhcpServerIP=enterprise.dhcpServerIP, TFTPServerIP=enterprise.TFTPServerIP,
                        FTPServerIP=enterprise.FTPServerIP,createAdmin=enterprise.createAdmin,
                        createTime=enterprise.createTime,updateTime=enterprise.updateTime, serverInfolist=serverinfoList)
            api_response['result'] = data
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[获取指定企业信息异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response), 500


# 获取用户列表
class Enterprises(APIView):
    authentication_classes = [TokenAuth2]
    def get(self,request):
        IsAuthenticate2.has_permission(self,request,"modules:usermanage:list")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        token = request.GET.get("token")
        page = (request.GET.get('page') if ('page' in request.GET) else 1)
        limit = (request.GET.get('limit') if ('limit' in request.GET) else 10)
        try:
            enterpriselist = []
            accName = rc4_decode_main(secretkey, token)
            userList = []
            enterpriseList=Enterprise.objects.all()
            sumList = Enterprise.objects.filter().all()[page*limit:(page+1)*limit-1]
            for enterprise in enterpriseList:
                enterpriselist.append(
                    dict(etpCode=enterprise.etpCode, etpName=enterprise.etpName, LDAPCode=enterprise.LDAPCode,
                         dhcpServerIP=enterprise.dhcpServerIP, TFTPServerIP=enterprise.TFTPServerIP,
                         FTPServerIP=enterprise.FTPServerIP,
                         createAdmin=enterprise.createAdmin, createTime=enterprise.createTime,
                         updateTime=enterprise.updateTime))
            result = dict(sumcount=len(sumList), detailcount=len(enterpriseList), list=enterpriselist)
            api_response['result'] = result
            return Response(api_response)
        except Exception as e:
            Logger('error.log', level='error').logger.error("[获取企业列表异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 500
            api_response["msg"] = "服务器未知错误"
            return Response(api_response), 500


#下载文件
class downLoad(APIView):
    authentication_classes = [TokenAuth2]
    def get(self,request,file_name):
        IsAuthenticate2.has_permission(self, request, "sys:download")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        token = request.GET.get("token")
        accName = rc4_decode_main(secretkey, token)
        try:
            def file_iterator(file_name, chunk_size=512):
                with open(file_name, 'rb') as f:
                    if f:
                        yield f.read(chunk_size)
                    else:
                        print('未完成下载')
            the_file_name = 'C:/Users/pcitc/PycharmProjects/django_web/web/files/' + file_name
            response = StreamingHttpResponse(file_iterator(the_file_name))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachement;filename="{0}"'.format(file_name)
            return response
        except Exception as e:
            Logger('error.log', level='error').logger.error("[下载文件异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 400
            api_response["msg"] = "系统异常"
            return Response(api_response)


# 上传文件
class upLoad(APIView):
    authentication_classes = [TokenAuth2]
    def post(self,request):
        IsAuthenticate2.has_permission(self, request, "sys:upload")
        api_response = {
            "code": 0,
            "msg": "success"
        }
        token = request.data.get('token')
        accName = rc4_decode_main(secretkey,token)
        try:
            myFile = request.FILES.get("file", None)
            if not myFile:
                return HttpResponse('no files for upload!')
            destination = open(os.path.join("C:/Users/pcitc/PycharmProjects/django_web/web/files", myFile.name), 'wb+')
            for chunk in myFile.chunks():
                destination.write(chunk)
            destination.close()
        except Exception as e:
            Logger('error.log', level='error').logger.error("[上传文件异常]accName:【%s】%s" % (accName, e))
            api_response["code"] = 400
            api_response["msg"] = "系统异常"
            return Response(api_response)
        api_response["result"] = myFile.name
        return Response(api_response)


#通过SSH连接服务器执行命令脚本
def getNetByIPAndMask(ip,mask):
    # 创建SSH对象
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接服务器
    ssh.connect(hostname='192.168.141.130', port=22, username='root', password='root')
    # 执行命令
    stdin, stdout, stderr = ssh.exec_command('cd /home/smcc/smcc-crst/SMCC_NEW/bin;./ipResponse ' + ip + ' ' + mask,get_pty=True)
    # 获取命令结果
    result = stdout.read()
    # 关闭连接
    ssh.close()
    return result