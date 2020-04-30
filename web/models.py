# @Time : 2020/4/28 11:17 
# @Author : lixiang
# @File : models.py 
# @Software: PyCharm
# @Time : 2020/4/28 10:13
# @Author : lixiang
# @File : log.py.py
# @Software: PyCharm
from django.db import models


class Last_Online(models.Model):
    #id = models.AutoField(primary_key=True, serialize=False)
    accName = models.CharField(max_length=50, verbose_name='登录账号', help_text='登录账号')
    userName = models.CharField(max_length=50, verbose_name='姓名', help_text='姓名')
    last_login_time = models.DateField(auto_now = True, verbose_name='最后登录时间', help_text='最后登录时间')
    login_count = models.IntegerField(default=0, verbose_name='登录次数', help_text='登录次数')

    class Meta:
        # 通过db_table属性,指定模型类对应的数据库表名。
        db_table = 'sys_user_last_online'  # 默认表名： 应用名_模型类名小写
        verbose_name = '登录日志'              # 后台admin管理站点中，表名的显示。

    def __str__(self):
        """定义每个数据对象的显示信息"""
        return self.userName


class User(models.Model):
    accName = models.CharField(max_length=50, null=False, verbose_name='登录账号', help_text='登录账号')
    userID = models.CharField(max_length=20, null=True, verbose_name='AD账号', help_text='AD账号')
    userName = models.CharField(max_length=50, null=True, verbose_name='姓名', help_text='姓名')
    userMail = models.CharField(max_length=50, null=True, verbose_name='邮箱', help_text='邮箱')
    userPhone = models.CharField(max_length=20, null=True, verbose_name='手机号', help_text='手机号')
    userTel = models.CharField(max_length=20, null=True, verbose_name='电话', help_text='电话')
    password = models.CharField(max_length=128, null=False, verbose_name='登录密码', help_text='登录密码')
    status = models.IntegerField(default=1, verbose_name='账户状态', help_text='账户状态')
    accAttr = models.CharField(max_length=20, null=True, verbose_name='企业编码', help_text='企业编码')
    etpName = models.CharField(max_length=50, null=True, verbose_name='企业名称', help_text='企业名称')
    userDP = models.CharField(max_length=50, null=True, verbose_name='部门', help_text='部门')
    create_date = models.DateField(null=True, verbose_name='创建日期', help_text='创建日期')
    create_user_id = models.CharField(null=True, max_length=50, verbose_name='创建人', help_text='创建人')
    remarks = models.CharField(null=True, max_length=100, verbose_name='备注', help_text='备注')

    class Meta:
        db_table = 'sys_user'
        verbose_name = '系统用户'

    def __str__(self):
        return self.userName

    def check_password(self, password):
        return password == self.password


class Role(models.Model):
    name = models.CharField(max_length=100, verbose_name='角色名称', help_text='角色名称')
    role = models.CharField(max_length=100, verbose_name='角色编码', help_text='角色编码')
    description = models.CharField(max_length=200, null=True, verbose_name='角色描述', help_text='角色描述')
    is_show = models.BooleanField(default=False, verbose_name='是否弃用', help_text='是否弃用')
    create_date = models.DateField(null=True, verbose_name='创建日期', help_text='创建日期')

    class Meta:
        db_table = 'sys_role'
        verbose_name = '角色'

    def __str__(self):
        """定义每个数据对象的显示信息"""
        return self.name


class userToRole(models.Model):
    user_id = models.IntegerField(verbose_name='用户ID', help_text='用户ID')
    role_id = models.IntegerField(verbose_name='角色ID', help_text='角色ID')

    class Meta:
        db_table = 'userToRole'
        verbose_name = '用户角色映射表'


class Resource(models.Model):
    name = models.CharField(max_length=50, verbose_name='权限名称', help_text='权限名称')
    url = models.CharField(max_length=200, null=True, verbose_name='跳转路径', help_text='跳转路径')
    perms = models.CharField(max_length=100, null=True, verbose_name='权限编码', help_text='权限编码')
    parent_id = models.IntegerField(verbose_name='父级权限ID', help_text='父级权限ID')
    type = models.IntegerField(verbose_name='权限类型', help_text='权限类型')                    #1：菜单权限 2：功能权限
    icon = models.CharField(max_length=50, null=True, verbose_name='图标', help_text='图标')
    weight = models.IntegerField(null=True, verbose_name='权重', help_text='权重')
    is_show = models.BooleanField(default=True, verbose_name='是否启用', help_text='是否启用')

    class Meta:
        db_table = 'sys_resource'
        verbose_name = '权限'

    def __str__(self):
        """定义每个数据对象的显示信息"""
        return self.name

class roleToResource(models.Model):
    role_id = models.IntegerField(verbose_name='角色ID', help_text='角色ID')
    resource_id = models.IntegerField(verbose_name='权限ID', help_text='权限ID')

    class Meta:
        db_table = 'roleToResource'
        verbose_name = '角色权限映射表'


class UserToken(models.Model):
    token = models.CharField(max_length=100, primary_key=True)
    created = models.DateTimeField(auto_now=True)
    accName = models.CharField(max_length=50)

    class Meta:
        db_table = 'web_usertoken'


class Enterprise(models.Model):
    etpCode = models.CharField(max_length=50, primary_key=True, verbose_name='企业编码', help_text='企业编码')
    etpName = models.CharField(max_length=20, null=False, verbose_name='企业名称', help_text='企业名称')
    LDAPCode = models.CharField(max_length=20, null=False, verbose_name='LDAP编码', help_text='LDAP编码')
    dhcpServerIP = models.CharField(max_length=20, null=True, verbose_name='DHCP服务器IP', help_text='DHCP服务器IP')
    TFTPServerIP = models.CharField(max_length=20, null=True, verbose_name='TFTP服务器IP', help_text='TFTP服务器IP')
    FTPServerIP = models.CharField(max_length=20, null=True, verbose_name='FTP服务器IP', help_text='FTP服务器IP')
    isDelete = models.BooleanField(default=False, verbose_name='是否弃用', help_text='是否弃用')
    createAdmin = models.CharField(max_length=50, null=True, verbose_name='创建人', help_text='创建人')
    createTime = models.DateField(verbose_name='创建时间', null=True, help_text='创建时间')
    updateTime = models.DateField(verbose_name='更新时间', null=True, help_text='更新时间')

    class Meta:
        db_table = 'enterprise_list'
        verbose_name = '企业列表'


class Server(models.Model):
    etpCode = models.CharField(max_length=50, verbose_name='企业编码', help_text='企业编码')
    serverType = models.IntegerField(verbose_name='服务器类型', help_text='服务器类型')      # 1:DHCP 服务器 2:TFTP服务器 3:FTP服务器
    serverIP = models.CharField(max_length=20, verbose_name='服务器IP', help_text='服务器IP')
    serverUsername = models.CharField(max_length=50, verbose_name='服务器账号', help_text='服务器账号')
    serverPasswd = models.CharField(max_length=50, verbose_name='服务器密码', help_text='服务器密码')

    class Meta:
        db_table = 'etp_server_list'
        verbose_name = '服务器列表'
        #unique_together = (("etpCode", "serverType"),)               #设置复合主键