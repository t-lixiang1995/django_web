from django.contrib import admin

from web.models import Last_Online, User, Role, Resource, Enterprise, Server


class Last_Online_Admin(admin.ModelAdmin):
    list_display = ['id','accName','userName','last_login_time','login_count']
class UserAdmin(admin.ModelAdmin):
    list_display = ['id','accName','userID','userName','userMail','userPhone','userTel','password',
                    'status','accAttr','etpName','userDP','create_date','create_user_id','remarks']
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'role', 'description', 'is_show', 'create_date']
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'url', 'perms', 'parent_id', 'type', 'icon', 'weight', 'is_show']
class EnterpriseAdmin(admin.ModelAdmin):
    list_display = ['etpCode', 'etpName', 'LDAPCode', 'dhcpServerIP', 'TFTPServerIP',
                    'FTPServerIP', 'isDelete', 'createAdmin', 'createTime', 'updateTime']
class ServerAdmin(admin.ModelAdmin):
    list_display = ['id', 'etpCode', 'serverType', 'serverIP', 'serverUsername', 'serverPasswd']

admin.site.register(Last_Online,Last_Online_Admin)
admin.site.register(User,UserAdmin)
admin.site.register(Role,RoleAdmin)
admin.site.register(Resource,ResourceAdmin)
admin.site.register(Enterprise,EnterpriseAdmin)
admin.site.register(Server,ServerAdmin)