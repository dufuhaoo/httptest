
from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi

class GetContactManager(SheetLoginBaseApi):
    """测试查询用户常用联系人"""
    url = '/netCarAdminAuth/page/contact/getCustomerContactInfo'
    def build_custom_param(self, data):
        return {'mobile': data['mobile']}

class ForbiddenContactManager(SheetLoginBaseApi):
    """测试禁用用户常用联系人"""

    url = '/netCarAdminAuth/page/contact/prohibitContact'

    def build_custom_param(self, data):
        return {'id': data['id'],'state':data['state']}