# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from ApiManager.utils import hooks
from ApiManager.pf_netcar_api.trade.contact_api import AddContactApi,AddContactApiNoLogin,GetAddcontactApiNoLogin,GetAddcontactApi,EditAddcontactApi
from ApiManager.pf_netcar_api.sheet.contact_manager import GetContactManager,ForbiddenContactManager
from ApiManager.utils.redis_helper import CONTACT_MONITORING_KEY
import time

class ContactMonitoring(BaseMonitoring):

    user_mobile = hooks.get_new_mobile()

    def add_contact(self):
        """测试添加常用联系人成功"""
        add_contact_api = AddContactApi()
        add_contact_api.post({'mobile':'13388881338','name':'李阳'})
        assert add_contact_api.get_resp_code() == 0
        assert add_contact_api.get_resp_message() == 'OK'

        add_contact_no_login = AddContactApiNoLogin()
        add_contact_no_login.post({'mobile':'13388881338','name':'李阳'})
        assert add_contact_no_login.get_resp_code() == 700
        assert add_contact_no_login.get_resp_message() == 'token_sign_fail'

    def add_contact_mobile_untrue(self):
        """测试添加常用联系人手机号格式不正确"""
        add_contact_mobile_untrue = AddContactApi()
        add_contact_mobile_untrue.post({'mobile': '10000000000', 'name': '李阳'})
        assert add_contact_mobile_untrue.get_resp_code() == 100101
        assert add_contact_mobile_untrue.get_resp_message() == 'parameter_error'

        """测试添加常用联系人手机号为空"""
        add_contact_mobile_none = AddContactApi()
        add_contact_mobile_none.post({'mobile': '', 'name': '李阳'})
        assert add_contact_mobile_none.get_resp_code() == 100101
        assert add_contact_mobile_none.get_resp_message() == 'parameter_error'

        """测试添加常用联系人手机号特殊字符"""
        add_contact_mobile_special = AddContactApi()
        add_contact_mobile_special.post({'mobile': '<tr>!><)<><', 'name': '李阳'})
        assert add_contact_mobile_special.get_resp_code() == 100101
        assert add_contact_mobile_special.get_resp_message() == 'parameter_error'

        """测试添加常用联系人姓名字段50个字符"""
        add_contact_name_fifty = AddContactApi()
        add_contact_name_fifty.post({'mobile': '13388881338', 'name': '一二三四五六七八九十一二三四五六七八九十一二三四五六七八九十一二三四五六七八九十一二三四五六七八九十'})
        assert add_contact_name_fifty.get_resp_code() == 0
        assert add_contact_name_fifty.get_resp_message() == 'OK'

        """测试添加常用联系人姓名字段51个字符"""
        add_contact_name_fifty_one = AddContactApi()
        add_contact_name_fifty_one.post({'mobile': '13388881338', 'name': '吧一二三四五六七八九十一二三四五六七八九十一二三四五六七八九十一二三四五六七八九十一二三四五六七八九十'})
        assert add_contact_name_fifty_one.get_resp_code() == 100101
        assert add_contact_name_fifty_one.get_resp_message() == 'parameter_error'
        """测试添加常用联系人姓名字段1个字符"""
        add_contact_name_one = AddContactApi()
        add_contact_name_one.post({'mobile': '13388881338', 'name': '门'})
        assert add_contact_name_one.get_resp_code() == 100101
        assert add_contact_name_one.get_resp_message() == 'parameter_error'

        """测试添加常用联系人姓名字段2个字符"""
        add_contact_name_two = AddContactApi()
        add_contact_name_two.post({'mobile': '13388881338', 'name': '豆婷'})
        assert add_contact_name_two.get_resp_code() == 0
        assert add_contact_name_two.get_resp_message() == 'OK'

        """测试添加常用联系人姓名字段为一个空格"""
        add_contact_name_blank = AddContactApi()
        add_contact_name_blank.post({'mobile': '13388881338', 'name': ' '})
        assert add_contact_name_blank.get_resp_code() == 100101
        assert add_contact_name_blank.get_resp_message() == 'parameter_error'

        """测试添加常用联系人姓名字段为空"""
        add_contact_name_none = AddContactApi()
        add_contact_name_none.post({'mobile': '13388881338', 'name': ''})
        assert add_contact_name_none.get_resp_code() == 100101
        assert add_contact_name_none.get_resp_message() == 'parameter_error'

        """测试未登录查询常用联系人"""
        get_add_contact_no_login =GetAddcontactApiNoLogin()
        get_add_contact_no_login.get({'pageNum': 1,'pageSize': 50})
        assert get_add_contact_no_login.get_resp_code() == 700
        assert get_add_contact_no_login.get_resp_message() == 'token_sign_fail'

    def add_contact_mobile_equally(self):
        """测试添加相同手机号联系人"""
        add_contact_mobile_equally = AddContactApi(mobile=self.user_mobile)
        add_contact_mobile_equally.post({'mobile': '13388881338', 'name': '刘小雨'})
        assert add_contact_mobile_equally.get_status_code() == 200
        assert add_contact_mobile_equally.get_resp_code() == 0
        assert add_contact_mobile_equally.get_resp_message() == 'OK'
        add_contact_mobile_equally.post({'mobile': '13388881338', 'name': '刘玉梅'})
        assert add_contact_mobile_equally.get_status_code() == 200
        assert add_contact_mobile_equally.get_resp_code() == 100402
        assert add_contact_mobile_equally.get_resp_message() == 'PERSON_INFO_REPEAT'

    def add_contact_name_equally(self):
        """测试添加不同手机号相同联系人"""
        add_contact_name_equally = AddContactApi(mobile=self.user_mobile)
        add_contact_name_equally.post({'mobile': '13300000001', 'name': '王玥'})
        assert add_contact_name_equally.get_status_code() == 200
        assert add_contact_name_equally.get_resp_code() == 0
        assert add_contact_name_equally.get_resp_message() == 'OK'
        add_contact_name_equally.post({'mobile': '13300000002', 'name': '王玥'})
        assert add_contact_name_equally.get_status_code() == 200
        assert add_contact_name_equally.get_resp_code() == 0
        assert add_contact_name_equally.get_resp_message() == 'OK'


    def add_contact_name_mobile_equally(self):
        """测试添加相同姓名相同手机号联系人"""
        add_contact_name_equally = AddContactApi(mobile=self.user_mobile)
        add_contact_name_equally.post({'mobile': '15500000001', 'name': '风灵'})
        add_contact_name_equally.post({'mobile': '15500000001', 'name': '风灵'})
        assert add_contact_name_equally.get_resp_code() == 100402
        assert add_contact_name_equally.get_resp_message() == 'PERSON_INFO_REPEAT'

    # def add_contact_amount(self):
    #     """测试添加联系人5条"""
    #     add_contact_amount = AddContactApi(mobile='17600021044')
    #     add_contact_amount.post({'mobile': '13500000001', 'name': '联系人1'})
    #     add_contact_amount.post({'mobile': '13500000002', 'name': '联系人2'})
    #     add_contact_amount.post({'mobile': '13500000003', 'name': '联系人3'})
    #     add_contact_amount.post({'mobile': '13500000004', 'name': '联系人4'})
    #     add_contact_amount.post({'mobile': '13500000005', 'name': '联系人5'})
    #     add_contact_amount.post({'mobile': '13500000006', 'name': '联系人6'})
    #     assert add_contact_amount.get_resp_code() == 0
    #     assert add_contact_amount.get_resp_message() == 'OK'
    #     hooks.clean_user_contact('17600021044')

    def get_add_contact(self):
        """测试查询常用联系人"""
        get_add_contact = AddContactApi(mobile=self.user_mobile)
        get_add_contact.post({'mobile': '18800000001', 'name': '刘娜娜'})
        assert get_add_contact.get_status_code() == 200
        assert get_add_contact.get_resp_code() == 0
        assert get_add_contact.get_resp_message() == 'OK'
        get_add_contact = GetAddcontactApi(mobile=self.user_mobile)
        get_add_contact.get({'pageNum': 1, 'pageSize': 50})
        get_res_data = get_add_contact.get_resp_data()
        assert get_add_contact.get_resp_code() == 0
        assert get_add_contact.get_resp_message() == 'OK'
        assert get_res_data['list'][0]['mobile']== '18800000001'
        assert  get_res_data['list'][0]['name'] == '刘娜娜'


    def get_add_contact_sort(self):
        """测试常用联系人列表排序"""
        get_add_contact_sort = AddContactApi(mobile=self.user_mobile)
        get_add_contact_sort.post({'mobile': '18800000002', 'name': '刘明月'})
        assert get_add_contact_sort.get_status_code() == 200
        assert get_add_contact_sort.get_resp_code() == 0
        assert get_add_contact_sort.get_resp_message() == 'OK'
        get_add_contact_sort.post({'mobile': '18800000003', 'name': '王明明'})
        assert get_add_contact_sort.get_status_code() == 200
        assert get_add_contact_sort.get_resp_code() == 0
        assert get_add_contact_sort.get_resp_message() == 'OK'
        get_add_contact_sort.post({'mobile': '18800000004', 'name': '徐晶晶'})
        assert get_add_contact_sort.get_status_code() == 200
        assert get_add_contact_sort.get_resp_code() == 0
        assert get_add_contact_sort.get_resp_message() == 'OK'
        get_add_contact_sort = GetAddcontactApi(mobile=self.user_mobile)
        get_add_contact_sort.get({'pageNum': 1, 'pageSize': 50})
        get_res_data = get_add_contact_sort.get_resp_data()
        assert get_add_contact_sort.get_resp_code() == 0
        assert get_add_contact_sort.get_resp_message() == 'OK'
        assert get_res_data['list'][0]['mobile'] == '18800000004'
        assert get_res_data['list'][0]['name'] == '徐晶晶'
        assert get_res_data['list'][1]['mobile'] == '18800000003'
        assert get_res_data['list'][1]['name'] == '王明明'
        assert get_res_data['list'][2]['mobile'] == '18800000002'
        assert get_res_data['list'][2]['name'] == '刘明月'

    def get_add_contact_page(self):
        """测试常用联系人列表分页"""
        get_add_contact_page = AddContactApi(mobile=self.user_mobile)
        get_add_contact_page.post({'mobile': '17600021041', 'name': '赵冉冉'})
        assert get_add_contact_page.get_status_code() == 200
        assert get_add_contact_page.get_resp_code() == 0
        assert get_add_contact_page.get_resp_message() == 'OK'
        get_add_contact_page.post({'mobile': '17600021042', 'name': '叶琳琳'})
        assert get_add_contact_page.get_status_code() == 200
        assert get_add_contact_page.get_resp_code() == 0
        assert get_add_contact_page.get_resp_message() == 'OK'
        get_add_contact_page.post({'mobile': '17600021043', 'name': '张程程'})
        assert get_add_contact_page.get_status_code() == 200
        assert get_add_contact_page.get_resp_code() == 0
        assert get_add_contact_page.get_resp_message() == 'OK'
        get_add_contact_page.post({'mobile': '17600021044', 'name': '王琪琪'})
        assert get_add_contact_page.get_status_code() == 200
        assert get_add_contact_page.get_resp_code() == 0
        assert get_add_contact_page.get_resp_message() == 'OK'
        get_add_contact_page = GetAddcontactApi(mobile=self.user_mobile)
        get_add_contact_page.get({'pageNum': 1,'pageSize': 2})
        get_res_data = get_add_contact_page.get_resp_data()
        assert get_add_contact_page.get_resp_code() == 0
        assert get_add_contact_page.get_resp_message() == 'OK'
        assert get_res_data['list'][0]['mobile'] == '17600021044'
        assert get_res_data['list'][0]['name'] == '王琪琪'
        assert get_res_data['list'][1]['mobile'] == '17600021043'
        assert get_res_data['list'][1]['name'] == '张程程'

    # def edit_add_contact(self):
    #     """测试修改联系人成功"""
        # edit_add_contact = AddContactApi(mobile='17600021048')
        # edit_add_contact.post({'mobile': '18800000010', 'name': '刘明月'})
        # assert edit_add_contact.get_status_code() == 200
        # assert edit_add_contact.get_resp_code() == 0
        # assert edit_add_contact.get_resp_message() == 'OK'
        #
        # edit_add_contact = GetAddcontactApi(mobile='17600021048')
        # edit_add_contact.get({'pageNum': 1, 'pageSize': 50})
        # assert edit_add_contact.get_status_code() == 200
        # assert edit_add_contact.get_resp_code() == 0
        # assert edit_add_contact.get_resp_message() == 'OK'
        # get_res_data = edit_add_contact.get_resp_data()
        # contact_id = get_res_data['list'][0]['id']
        # print(contact_id)

        # edit_add_contact = EditAddcontactApi()
        # edit_add_contact.post({'contactId':'1185070041998032896','mobile':'18800000011','name':'刘铭玥'})
        # assert edit_add_contact.get_status_code() == 200
        # assert edit_add_contact.get_resp_code() == 0
        # assert edit_add_contact.get_resp_message() == 'OK'

        # edit_add_contact = GetAddcontactApi(mobile='17600021048')
        # edit_add_contact.get({'pageNum': 1, 'pageSize': 50})
        # assert edit_add_contact.get_resp_code() == 0
        # assert edit_add_contact.get_resp_message() == 'OK'
        # assert get_res_data['list'][0]['mobile'] == '18800000011'
        # assert get_res_data['list'][0]['name'] == '刘铭玥'
        # hooks.clean_user_contact('17600021048')

    def get_contact_manager(self):
        """sheet测试查询用户常用联系人"""
        get_contact_manager = AddContactApi(mobile=self.user_mobile)
        get_contact_manager.post({'mobile': '13366666666', 'name': '李宁杨'})
        assert get_contact_manager.get_status_code() == 200
        assert get_contact_manager.get_resp_code() == 0
        assert get_contact_manager.get_resp_message() == 'OK'
        get_contact_manager = GetContactManager()
        get_contact_manager.get({'mobile': self.user_mobile})
        get_res_data = get_contact_manager.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['dpMobile'] == self.user_mobile
        assert get_res_data['data']['list'][0]['mobile'] == '13366666666'
        assert get_res_data['data']['total'] == '1'

    def get_contact_manager_none(self):
        """测试查询用户常用联系人手机号为空"""
        get_contact_manager = GetContactManager()
        get_contact_manager.get({'mobile': ''})
        get_res_data = get_contact_manager.get_resp_content()
        assert get_res_data['code'] == 100101
        assert get_res_data['msg'] == '请检查输入项'

    def get_contact_manager_forbidden(self):
        """测试禁用用户常用联系人"""
        get_contact_manager = AddContactApi(mobile=self.user_mobile)
        get_contact_manager.post({'mobile': '13366666655', 'name': '李宁杨'})
        assert get_contact_manager.get_status_code() == 200
        assert get_contact_manager.get_resp_code() == 0
        assert get_contact_manager.get_resp_message() == 'OK'

        get_contact_manager = GetContactManager()
        get_contact_manager.get({'mobile': self.user_mobile})
        get_res_data = get_contact_manager.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['dpMobile'] == self.user_mobile
        assert get_res_data['data']['list'][0]['mobile'] == '13366666655'
        assert get_res_data['data']['total'] == '1'
        id = get_res_data['data']['list'][0]['id']

        get_contact_manager = ForbiddenContactManager()
        get_contact_manager.get({'id':id,'state':0})
        get_res_data = get_contact_manager.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'

        get_contact_manager = GetContactManager()
        get_contact_manager.get({'mobile': self.user_mobile})
        get_res_data = get_contact_manager.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['total'] == '0'

        get_contact_manager = GetAddcontactApi(mobile=self.user_mobile)
        get_contact_manager.get({'pageNum': 1,'pageSize': 50})
        get_res_data = get_contact_manager.get_resp_data()
        assert get_contact_manager.get_resp_code() == 0
        assert get_contact_manager.get_resp_message() == 'OK'
        assert get_res_data['total'] == 0
        assert get_res_data['list'] == []

    def tearDown(self):
        super(ContactMonitoring,self).tearDown()
        hooks.clean_user_contact(self.user_mobile)
        time.sleep(5)


if __name__ == '__main__':
    api = ContactMonitoring()
    api.run_method(monitoring_name='常用联系人监控',monitoring_class=api,redis_key=CONTACT_MONITORING_KEY)






