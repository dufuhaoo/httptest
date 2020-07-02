# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from ApiManager.utils.redis_helper import COMMON_ADDRESS_MONITORING_KEY
from ApiManager.pf_netcar_api.trade.common_address_api import AddCommonAdresstApi,GetCommonAdress,DelCommonAdressApi,EditCommonAddressApi
from ApiManager.utils import hooks
import time


class CommonAdressMonitoring(BaseMonitoring):
    """
    常用地址监控
    """

    def setUp(self):
        self.user_mobile = hooks.get_new_mobile()

    def add_common_address_home(self):
        """
        添加家的常用地址
        :return:
        """
        add_com_adress_home = AddCommonAdresstApi()
        add_com_adress_home.post( {'data': {'addName': '甘肃省淑珍县上街呼和浩特路R座 269118', 'addType': 1,'areaName': '测试区','locationInfo': {'lat': '39.9378','lng': '116.3266' },'streetName': '刘街'}})
        assert add_com_adress_home.get_resp_code() == 0
        assert add_com_adress_home.get_resp_message() == 'OK'

        get_add_com_address_home = GetCommonAdress(mobile=add_com_adress_home.mobile)
        get_add_com_address_home.get()
        get_res_data = get_add_com_address_home.get_resp_data()
        assert get_add_com_address_home.get_resp_code() == 0
        assert get_add_com_address_home.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        assert get_res_data[0]['addName'] == '甘肃省淑珍县上街呼和浩特路R座 269118'
        assert get_res_data[0]['addType'] == 1
        assert get_res_data[0]['streetName'] == '刘街'
        assert get_res_data[0]['lng'] == '116.3266'
        assert get_res_data[0]['lat'] == '39.9378'

    def add_common_address_home_region_empty(self):
        """
        测试添加家常用地址区域名称为空
        :return:
        """
        add_com_adress_home_region_empty = AddCommonAdresstApi()
        add_com_adress_home_region_empty.post( {"data": {"addName": "甘肃省淑珍县上街呼和浩特路R座 269118","addType": 1,"areaName": None,"locationInfo": {"lat": "39.9378","lng": "116.3266"},"streetName": "刘街"},"signStr": "string"})
        assert add_com_adress_home_region_empty.get_resp_code() == 0
        assert add_com_adress_home_region_empty.get_resp_message() == 'OK'

        get_add_com_address_home_region_empty = GetCommonAdress(mobile=add_com_adress_home_region_empty.mobile)
        get_add_com_address_home_region_empty.get()
        get_res_data = get_add_com_address_home_region_empty.get_resp_data()
        assert get_add_com_address_home_region_empty.get_resp_code() == 0
        assert get_add_com_address_home_region_empty.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        assert get_res_data[0]['addName'] == '甘肃省淑珍县上街呼和浩特路R座 269118'
        assert get_res_data[0]['addType'] == 1
        assert get_res_data[0]['streetName'] == '刘街'
        assert get_res_data[0]['lng'] == '116.3266'
        assert get_res_data[0]['lat'] == '39.9378'

    def add_common_address_home_street_empty(self):
        """
        测试添加家常用地址街道名称为空
        :return:
        """
        add_com_adress_home_street_empty = AddCommonAdresstApi()
        add_com_adress_home_street_empty.post({"data": {"addName": "甘肃省淑珍县上街呼和浩特路R座 269118", "addType": 1,"areaName": '测试区',"locationInfo": {"lat": "39.9378", "lng": "116.3266"},"streetName": None}, "signStr": "string"})
        assert add_com_adress_home_street_empty.get_resp_code() == 0
        assert add_com_adress_home_street_empty.get_resp_message() == 'OK'

        get_add_com_address_home_street_empty = GetCommonAdress(mobile=add_com_adress_home_street_empty.mobile)
        get_add_com_address_home_street_empty.get()
        get_res_data = get_add_com_address_home_street_empty.get_resp_data()
        assert get_add_com_address_home_street_empty.get_resp_code() == 0
        assert get_add_com_address_home_street_empty.get_resp_message() == 'OK'
        assert len(get_res_data) == 1

        assert get_res_data[0]['addName'] == '甘肃省淑珍县上街呼和浩特路R座 269118'
        assert get_res_data[0]['addType'] == 1
        assert get_res_data[0]['streetName'] == None
        assert get_res_data[0]['lng'] == '116.3266'
        assert get_res_data[0]['lat'] == '39.9378'


    def add_common_address_home_region_street_empty(self):
        """
        测试添加家常用地址街道名称和区域名称为空
        :return:
        """
        add_com_adress_home_region_street_emp = AddCommonAdresstApi()
        add_com_adress_home_region_street_emp.post({"data": {"addName": "甘肃省淑珍县上街呼和浩特路R座 269118", "addType": 1,
                                                        "areaName": None,
                                                        "locationInfo": {"lat": "39.9378", "lng": "116.3266"},
                                                        "streetName": None}, "signStr": "string"})
        assert add_com_adress_home_region_street_emp.get_resp_code() == 0
        assert add_com_adress_home_region_street_emp.get_resp_message() == 'OK'

        get_add_com_address_home_region_street_emp = GetCommonAdress(mobile=add_com_adress_home_region_street_emp.mobile)
        get_add_com_address_home_region_street_emp.get()
        get_res_data = get_add_com_address_home_region_street_emp.get_resp_data()
        assert get_add_com_address_home_region_street_emp.get_resp_code() == 0
        assert get_add_com_address_home_region_street_emp.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        assert get_res_data[0]['addName'] == '甘肃省淑珍县上街呼和浩特路R座 269118'
        assert get_res_data[0]['addType'] == 1
        assert get_res_data[0]['streetName'] == None
        assert get_res_data[0]['lng'] == '116.3266'
        assert get_res_data[0]['lat'] == '39.9378'

    def add_common_address_home_name_empty(self):
        """
        测试添加家常用地址名称为空
        :return:
        """
        add_com_adressname_home_emp = AddCommonAdresstApi()
        add_com_adressname_home_emp.post({"data": {"addName":None, "addType": 1,"areaName": '测试区',"locationInfo": {"lat": "39.9378", "lng": "116.3266"},"streetName": '刘街'}, "signStr": "string"})
        assert add_com_adressname_home_emp.get_resp_code() == 100101
        assert add_com_adressname_home_emp.get_resp_message() == 'parameter_error'

    def add_common_address_home_again(self):
        """
        测试重复添加家地址
        :return:
        """
        add_com_adress_home = AddCommonAdresstApi(mobile=self.user_mobile)
        add_com_adress_home.post( {"data": {"addName": "甘肃省淑珍县上街呼和浩特路R座 269118", "addType": 1,"areaName": '测试区',"locationInfo": {"lat": "39.9378", "lng": "116.3266"},"streetName": '刘街'}, "signStr": "string"})
        assert add_com_adress_home.get_resp_code() == 0
        assert add_com_adress_home.get_resp_message() == 'OK'
        time.sleep(3)
        add_com_adress_home = AddCommonAdresstApi(mobile=self.user_mobile)
        add_com_adress_home.post({"data": {"addName": "甘肃省淑珍县上街呼和浩特路R座 269223", "addType": 1,"areaName": '测试区',"locationInfo": {"lat": "39.9378", "lng": "116.3266"},"streetName": '刘街'}, "signStr": "string"})
        assert add_com_adress_home.get_resp_code() == 100301
        assert add_com_adress_home.get_resp_message() == "THE_ADD_TYPE_ALREADY_HAS"

    def add_common_address_company(self):
        """
        测试添加公司地址
        :return:
        """
        add_common_adress_company = AddCommonAdresstApi()
        add_common_adress_company.post({"data": {"addName": "广西壮族自治区福州市高明空街g座 828487","addType": 2,"areaName": "测试区","locationInfo": {"lat": "39.9378","lng": "116.3266"},"streetName": "跋路"},"signStr": "string"})
        assert add_common_adress_company.get_resp_code() == 0
        assert add_common_adress_company.get_resp_message() == "OK"

        get_com_adress_company = GetCommonAdress(mobile=add_common_adress_company.mobile)
        get_com_adress_company.get()
        get_res_data = get_com_adress_company.get_resp_data()
        assert get_com_adress_company.get_resp_code() == 0
        assert get_com_adress_company.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        assert get_res_data[0]['addName'] == '广西壮族自治区福州市高明空街g座 828487'
        assert get_res_data[0]['addType'] == 2
        assert get_res_data[0]['streetName'] == '跋路'
        assert get_res_data[0]['lng'] == '116.3266'
        assert get_res_data[0]['lat'] == '39.9378'

    def add_common_address_company_region_empty(self):
        """
        测试添加公司地址区域名称为空
        :return:
        """
        add_com_adress_comp_region_empty = AddCommonAdresstApi()
        add_com_adress_comp_region_empty.post({"data": {"addName": "广西壮族自治区福州市高明空街g座 828487","addType": 2,"areaName": None,"locationInfo": {"lat": "39.9378","lng": "116.3266"},"streetName": "跋路"},"signStr": "string"})
        assert add_com_adress_comp_region_empty.get_resp_code() == 0
        assert add_com_adress_comp_region_empty.get_resp_message() == "OK"

        get_add_com_adress_comp_region_empty = GetCommonAdress(mobile=add_com_adress_comp_region_empty.mobile)
        get_add_com_adress_comp_region_empty.get()
        get_res_data = get_add_com_adress_comp_region_empty.get_resp_data()
        assert get_add_com_adress_comp_region_empty.get_resp_code() == 0
        assert get_add_com_adress_comp_region_empty.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        assert get_res_data[0]['addName'] == '广西壮族自治区福州市高明空街g座 828487'
        assert get_res_data[0]['addType'] == 2
        assert get_res_data[0]['streetName'] == '跋路'
        assert get_res_data[0]['lng'] == '116.3266'
        assert get_res_data[0]['lat'] == '39.9378'

    def add_common_address_company_street_empty(self):
        """
        测试添加公司地址街道名称为空
        :return:
        """
        add_com_adress_comp_street_empty = AddCommonAdresstApi()
        add_com_adress_comp_street_empty.post( {"data": {"addName": "广西壮族自治区福州市高明空街g座 828487","addType": 2,"areaName": "测试区","locationInfo": {"lat": "39.9378","lng": "116.3266"},"streetName": None},"signStr": "string"})
        assert add_com_adress_comp_street_empty.get_resp_code() == 0
        assert add_com_adress_comp_street_empty.get_resp_message() == "OK"

        get_add_com_address_comp_street_empty = GetCommonAdress(mobile=add_com_adress_comp_street_empty.mobile)
        get_add_com_address_comp_street_empty.get()
        get_res_data = get_add_com_address_comp_street_empty.get_resp_data()

        assert get_add_com_address_comp_street_empty.get_resp_code() == 0
        assert get_add_com_address_comp_street_empty.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        assert get_res_data[0]['addName'] == '广西壮族自治区福州市高明空街g座 828487'
        assert get_res_data[0]['addType'] == 2
        assert get_res_data[0]['streetName'] == None
        assert get_res_data[0]['lng'] == '116.3266'
        assert get_res_data[0]['lat'] == '39.9378'

    def add_common_address_company_region_street_empty(self):
        """
        测试添加公司地址街道名称和区域名称为空
        :return:
        """
        add_com_adress_comp_region_street_empty = AddCommonAdresstApi()
        add_com_adress_comp_region_street_empty.post( {"data": {"addName": "广西壮族自治区福州市高明空街g座 828487","addType": 2,"areaName": None,"locationInfo": {"lat": "39.9378","lng": "116.3266"},"streetName": None},"signStr": "string"})
        assert add_com_adress_comp_region_street_empty.get_resp_code() == 0
        assert add_com_adress_comp_region_street_empty.get_resp_message() == 'OK'

        get_add_adress_comp_region_street_empty = GetCommonAdress(mobile=add_com_adress_comp_region_street_empty.mobile)
        get_add_adress_comp_region_street_empty.get()
        get_res_data = get_add_adress_comp_region_street_empty.get_resp_data()

        assert get_add_adress_comp_region_street_empty.get_resp_code() == 0
        assert get_add_adress_comp_region_street_empty.get_resp_message() == "OK"
        assert len(get_res_data) == 1
        assert get_res_data[0]['addName'] == '广西壮族自治区福州市高明空街g座 828487'
        assert get_res_data[0]['addType'] == 2
        assert get_res_data[0]['streetName'] == None
        assert get_res_data[0]['lng'] == '116.3266'
        assert get_res_data[0]['lat'] == '39.9378'

    def add_common_address_company_again(self):
        """
        测试重复添加公司地址
        :return:
        """
        adds_com_adress_company = AddCommonAdresstApi(mobile=self.user_mobile)
        adds_com_adress_company.post({"data": {"addName": "广西壮族自治区林县沈北新沈街b座 440383","addType": 2,"areaName": "测试区","locationInfo": {"lat": "39.9378","lng": "116.3266"},"streetName": "蓟街"},"signStr": "string"})
        assert adds_com_adress_company.get_resp_code() == 0
        assert adds_com_adress_company.get_resp_message() == 'OK'

        adds_com_adress_company = AddCommonAdresstApi(mobile=self.user_mobile)
        adds_com_adress_company.post({"data": {"addName": "广西壮族自治区林县沈北新沈街b座 444443", "addType": 2,"areaName": "测试区","locationInfo": {"lat": "39.9378", "lng": "116.3266"},"streetName": "蓟街"}, "signStr": "string"})
        assert adds_com_adress_company.get_resp_code() == 100301
        assert adds_com_adress_company.get_resp_message() == 'THE_ADD_TYPE_ALREADY_HAS'

    def add_common_address_tyoe_error(self):
        """
        测试添加常用地址类型填写错误
        :return:
        """
        add_test_type_nine =AddCommonAdresstApi()
        add_test_type_nine.post({"data": {"addName": "abc bb","addType": 9,"areaName": "测试区","locationInfo": {"lat": "39.9378","lng": "116.3266"},"streetName": "西安街"},"signStr": "string"})
        assert add_test_type_nine.get_resp_code() == 100300
        assert add_test_type_nine.get_resp_message() == 'PLEASE_ADD_CORRECT_TYPE'

    def add_common_address_type_empty(self):
        """
        测试添加家常用地址类型为空
        :return:
        """
        add_com_adressname_home_emp = AddCommonAdresstApi()
        add_com_adressname_home_emp.post({"data": {"addName":'甘肃省淑珍县上街呼和浩特路R座 269118', "addType": None,"areaName": '测试区',"locationInfo": {"lat": "39.9378", "lng": "116.3266"},"streetName": '刘街'}, "signStr": "string"})
        assert add_com_adressname_home_emp.get_resp_code() == 100101
        assert add_com_adressname_home_emp.get_resp_message() == 'parameter_error'

    def del_common_address_home(self):
        """
        测试删除常用地址（家）
        :return:
        """
        add_com_address_home = AddCommonAdresstApi()
        add_com_address_home.post({'data': {'addName': '山东省兴城市吉区钟路l座 621706', 'addType': 1, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '海口街'}, 'signStr': 'string'})
        assert add_com_address_home.get_resp_code() == 0
        assert add_com_address_home.get_resp_message() == 'OK'

        get_add_com_adress_home = GetCommonAdress(mobile=add_com_address_home.mobile)
        get_add_com_adress_home.get()
        get_res_data = get_add_com_adress_home.get_resp_data()
        assert get_add_com_adress_home.get_resp_code() == 0
        assert get_add_com_adress_home.get_resp_message() == 'OK'
        common_adress_id = get_res_data[0]['id']

        del_com_adress_home = DelCommonAdressApi(mobile=add_com_address_home.mobile)
        del_com_adress_home.get({'commonAddressId': common_adress_id})
        assert del_com_adress_home.get_resp_code() == 0
        assert del_com_adress_home.get_resp_message() == 'OK'

        get_add_com_adress_home = GetCommonAdress(mobile=add_com_address_home.mobile)
        get_add_com_adress_home.get()
        get_res_data = get_add_com_adress_home.get_resp_data()
        assert get_add_com_adress_home.get_resp_code() == 0
        assert get_add_com_adress_home.get_resp_message() == 'OK'
        assert len(get_res_data) == 0

    def del_common_address_company(self):
        """
        测试删除常用地址（公司）
        :return:
        """
        add_com_adress_company = AddCommonAdresstApi()
        add_com_adress_company.post({'data': {'addName': '山西省娟市牧野天津路M座 425579', 'addType': 2, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '银川街'}, 'signStr': 'string'})
        assert add_com_adress_company.get_resp_code() == 0
        assert add_com_adress_company.get_resp_message() == 'OK'

        get_com_adress_company = GetCommonAdress(mobile=add_com_adress_company.mobile)
        get_com_adress_company.get()
        assert get_com_adress_company.get_resp_code() == 0
        assert get_com_adress_company.get_resp_message() == 'OK'
        get_res_data = get_com_adress_company.get_resp_data()
        common_adress_id = get_res_data[0]['id']

        del_com_address_company = DelCommonAdressApi(mobile=add_com_adress_company.mobile)
        del_com_address_company.get({'commonAddressId': common_adress_id})
        assert del_com_address_company.get_resp_code() == 0
        assert del_com_address_company.get_resp_message() == 'OK'

        get_com_adress_company = GetCommonAdress(mobile=add_com_adress_company.mobile)
        get_com_adress_company.get()
        assert get_com_adress_company.get_resp_code() == 0
        assert get_com_adress_company.get_resp_message() == 'OK'
        get_res_data = get_com_adress_company.get_resp_data()
        assert len(get_res_data) == 0

    def del_common_address_id_empty(self):
        """
        测试地址ID为空时请求接口
        :return:
        """
        del_com_address_empty = DelCommonAdressApi()
        del_com_address_empty.get({'commonAddressId': None})
        assert del_com_address_empty.get_resp_code() == 100101
        assert del_com_address_empty.get_resp_message() == 'parameter_error'

    def edit_common_address_home(self):
        """
        测试修改家常用地址
        :return:
        """
        #添加用户常用家地址
        add_com_adress_home = AddCommonAdresstApi()
        add_com_adress_home.post({'data': {'addName': '吉林省军县上街刁路p座 191905', 'addType': 1, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '嘉禾路'}, 'signStr': 'string'})
        assert add_com_adress_home.get_resp_code() == 0
        assert add_com_adress_home.get_resp_message() == 'OK'
        # 查看用户常用家地址
        get_com_aderss_home = GetCommonAdress(mobile=add_com_adress_home.mobile)
        get_com_aderss_home.get()
        get_res_data = get_com_aderss_home.get_resp_data()
        assert get_com_aderss_home.get_resp_code() == 0
        assert get_com_aderss_home.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        common_address_id = get_res_data[0]['id']
        # 修改用户常用家地址
        edit_com_adress_home = EditCommonAddressApi(mobile=add_com_adress_home.mobile)
        edit_com_adress_home.post({'data': {'addName': 'oppo', 'areaName': 'oppo区', 'commonAddressId': common_address_id, 'lat': 111.1, 'lng': 120.1, 'streetName': 'oppo街道'}, 'signStr': 'string'})
        assert edit_com_adress_home.get_resp_code() == 0
        assert edit_com_adress_home.get_resp_message() == 'OK'
        #查看修改后常用地址
        get_edit_com_adress_home = GetCommonAdress(mobile=add_com_adress_home.mobile)
        get_edit_com_adress_home.get()
        get_edit_res_data = get_edit_com_adress_home.get_resp_data()
        assert get_edit_com_adress_home.get_resp_code() == 0
        assert get_edit_com_adress_home.get_resp_message() == 'OK'
        assert len(get_edit_res_data) == 1
        assert get_edit_res_data[0]['addName'] == 'oppo'
        assert get_edit_res_data[0]['addType'] == 1
        assert get_edit_res_data[0]['streetName'] == 'oppo街道'
        assert get_edit_res_data[0]['lng'] == '120.1'
        assert get_edit_res_data[0]['lat'] == '111.1'

    def edit_common_address_home_street_empty(self):
        """
        测试修改家常用地址街道名称为空
        :return:
        """
        add_com_adress_street_empty = AddCommonAdresstApi()
        add_com_adress_street_empty.post({'data': {'addName': '山西省武汉县大兴段路D座 451580', 'addType': 1, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '辛集路'}, 'signStr': 'string'})
        assert add_com_adress_street_empty.get_resp_code() == 0
        assert add_com_adress_street_empty.get_resp_message() == 'OK'
        # 查询常用地址
        get_com_adress_street_empty = GetCommonAdress(mobile=add_com_adress_street_empty.mobile)
        get_com_adress_street_empty.get()
        get_res_data = get_com_adress_street_empty.get_resp_data()
        assert get_com_adress_street_empty.get_resp_code() == 0
        assert get_com_adress_street_empty.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        common_address_id = get_res_data[0]['id']

        #修改常用地址
        edit_com_adress_street_empty = EditCommonAddressApi(mobile=add_com_adress_street_empty.mobile)
        edit_com_adress_street_empty.post({'data': {'addName': 'oppo', 'areaName': 'oppo区', 'commonAddressId': common_address_id, 'lat': 111.1, 'lng': 120.1, 'streetName': None}, 'signStr': 'string'})
        assert edit_com_adress_street_empty.get_resp_code() == 0
        assert edit_com_adress_street_empty.get_resp_message() == 'OK'

        #查询修改后的常用地址
        get_edit_com_adress_street_empty = GetCommonAdress(mobile=add_com_adress_street_empty.mobile)
        get_edit_com_adress_street_empty.get()
        get_edit_res_data = get_edit_com_adress_street_empty.get_resp_data()
        assert get_edit_com_adress_street_empty.get_resp_code() == 0
        assert get_edit_com_adress_street_empty.get_resp_message() == 'OK'
        assert len(get_edit_res_data) == 1
        assert get_edit_res_data[0]['addName'] == 'oppo'
        assert get_edit_res_data[0]['addType'] == 1
        assert get_edit_res_data[0]['streetName'] == '辛集路'
        assert get_edit_res_data[0]['lng'] == '120.1'
        assert get_edit_res_data[0]['lat'] == '111.1'

    def edit_common_address_home_region_empty(self):
        """
        测试修改家常用地址区域名称为空
        :return:
        """
        add_com_address_home_reg_emp = AddCommonAdresstApi()
        add_com_address_home_reg_emp.post({'data': {'addName': '安徽省福州市丰都郝路G座 631645', 'addType': 1, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '官路'}, 'signStr': 'string'})
        assert add_com_address_home_reg_emp.get_resp_code() == 0
        assert add_com_address_home_reg_emp.get_resp_message() == 'OK'
        #查询常用地址
        get_com_adress_home_reg_emp = GetCommonAdress(mobile=add_com_address_home_reg_emp.mobile)
        get_com_adress_home_reg_emp.get()
        get_res_data = get_com_adress_home_reg_emp.get_resp_data()
        assert get_com_adress_home_reg_emp.get_resp_code() == 0
        assert get_com_adress_home_reg_emp.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        common_address_id = get_res_data[0]['id']
        # 修改常用地址
        edit_com_adress_home_reg_emp = EditCommonAddressApi(mobile=add_com_address_home_reg_emp.mobile)
        edit_com_adress_home_reg_emp.post({'data': {'addName': 'oppo', 'areaName': '', 'commonAddressId': common_address_id, 'lat': 111.1, 'lng': 120.1, 'streetName': 'oppo街道'}, 'signStr': 'string'})
        assert edit_com_adress_home_reg_emp.get_resp_code() == 0
        assert edit_com_adress_home_reg_emp.get_resp_message() == 'OK'
        # 查询修改后的常用地址
        get_edit_com_address = GetCommonAdress(mobile=add_com_address_home_reg_emp.mobile)
        get_edit_com_address.get()
        get_edit_res_data = get_edit_com_address.get_resp_data()
        assert get_edit_com_address.get_resp_code() == 0
        assert get_edit_com_address.get_resp_message() == 'OK'
        assert len(get_edit_res_data) == 1
        assert get_edit_res_data[0]['addName'] == 'oppo'
        assert get_edit_res_data[0]['addType'] == 1
        assert get_edit_res_data[0]['streetName'] == 'oppo街道'
        assert get_edit_res_data[0]['lng'] == '120.1'
        assert get_edit_res_data[0]['lat'] == '111.1'

    def edit_common_address_home_region_street_empty(self):
        """
        测试修改家常用地址区域名称和街道名称为空
        :return:
        """
        add_com_adress_home_reg_str_emp = AddCommonAdresstApi()
        add_com_adress_home_reg_str_emp.post({'data': {'addName': '陕西省深圳县璧山狐路x座 116077', 'addType': 1, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '子路'}, 'signStr': 'string'})
        assert add_com_adress_home_reg_str_emp.get_resp_code() == 0
        assert add_com_adress_home_reg_str_emp.get_resp_message() == 'OK'
        # 查询常用地址
        get_com_adress_reg_str_emp = GetCommonAdress(mobile=add_com_adress_home_reg_str_emp.mobile)
        get_com_adress_reg_str_emp.get()
        get_res_data = get_com_adress_reg_str_emp.get_resp_data()
        assert get_com_adress_reg_str_emp.get_resp_code() == 0
        assert get_com_adress_reg_str_emp.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        common_address_id = get_res_data[0]['id']
        # 修改常用地址
        edit_com_adress_reg_str_emp = EditCommonAddressApi(mobile=add_com_adress_home_reg_str_emp.mobile)
        edit_com_adress_reg_str_emp.post({'data': {'addName': 'oppo', 'areaName': '', 'commonAddressId': common_address_id, 'lat': 111.1, 'lng': 120.1, 'streetName': ''}, 'signStr': 'string'})
        assert edit_com_adress_reg_str_emp.get_resp_code() == 0
        assert edit_com_adress_reg_str_emp.get_resp_message() == 'OK'
        # 查询出修改后的常用地址
        get_edit_com_adress = GetCommonAdress(mobile=add_com_adress_home_reg_str_emp.mobile)
        get_edit_com_adress.get()
        get_edit_res_data = get_edit_com_adress.get_resp_data()
        assert get_edit_com_adress.get_resp_code() == 0
        assert get_edit_com_adress.get_resp_message() == 'OK'
        assert len(get_edit_res_data) == 1
        assert get_edit_res_data[0]['addName'] == 'oppo'
        assert get_edit_res_data[0]['addType'] == 1
        assert get_edit_res_data[0]['streetName'] == ''
        assert get_edit_res_data[0]['lng'] == '120.1'
        assert get_edit_res_data[0]['lat'] == '111.1'

    def edit_common_address_name_empty(self):
        """
        测试修改家常用地址名称为空
        :return:
        """
        add_com_adress_name_emp = AddCommonAdresstApi()
        add_com_adress_name_emp.post({'data': {'addName': '贵州省波市合川成都路s座 705874', 'addType': 1, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '驷路'}, 'signStr': 'string'})
        assert add_com_adress_name_emp.get_resp_code() == 0
        assert add_com_adress_name_emp.get_resp_message() == 'OK'
        # 查询常用地址
        get_com_address_name = GetCommonAdress(mobile=add_com_adress_name_emp.mobile)
        get_com_address_name.get()
        get_res_data = get_com_address_name.get_resp_data()
        assert get_com_address_name.get_resp_code() == 0
        assert get_com_address_name.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        common_address_id = get_res_data[0]['id']
        # 修改常用地址
        edit_com_adress_name_emp = EditCommonAddressApi(mobile=add_com_adress_name_emp.mobile)
        edit_com_adress_name_emp.post({'data': {'addName': '', 'areaName': '测试区', 'commonAddressId': common_address_id, 'lat': 111.1, 'lng': 120.1, 'streetName': '驷路'}, 'signStr': 'string'})
        assert edit_com_adress_name_emp.get_resp_code() == 100101
        assert edit_com_adress_name_emp.get_resp_message() == 'parameter_error'

    def edit_common_address_company(self):
        """
        测试修改公司常用地址
        :return:
        """
        add_com_adress_company = AddCommonAdresstApi()
        add_com_adress_company.post({'data': {'addName': '新疆维吾尔自治区博市长寿夔街f座 513790', 'addType': 2, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '濮路'}, 'signStr': 'string'})
        assert add_com_adress_company.get_resp_code() == 0
        assert add_com_adress_company.get_resp_message() == 'OK'
        # 查询公司常用地址
        get_com_adress_company = GetCommonAdress(mobile=add_com_adress_company.mobile)
        get_com_adress_company.get()
        get_res_data = get_com_adress_company.get_resp_data()
        assert get_com_adress_company.get_resp_code() == 0
        assert get_com_adress_company.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        common_adress_id = get_res_data[0]['id']
        # 修改公司常用地址
        edit_com_adress_company = EditCommonAddressApi(mobile=add_com_adress_company.mobile)
        edit_com_adress_company.post({'data': {'addName': 'oppo', 'areaName': 'oppo区', 'commonAddressId': common_adress_id, 'lat': 111.1, 'lng': 120.1, 'streetName': 'oppo街道'}, 'signStr': 'string'})
        assert edit_com_adress_company.get_resp_code() == 0
        assert edit_com_adress_company.get_resp_message() == 'OK'
        # 查询修改后公司常用地址
        get_edit_com_adress = GetCommonAdress(mobile=add_com_adress_company.mobile)
        get_edit_com_adress.get()
        get_edit_res_data = get_edit_com_adress.get_resp_data()
        assert get_edit_com_adress.get_resp_code() == 0
        assert get_edit_com_adress.get_resp_message() == 'OK'
        assert len(get_edit_res_data) == 1
        assert get_edit_res_data[0]['addName'] == 'oppo'
        assert get_edit_res_data[0]['addType'] == 2
        assert get_edit_res_data[0]['streetName'] == 'oppo街道'
        assert get_edit_res_data[0]['lng'] == '120.1'
        assert get_edit_res_data[0]['lat'] == '111.1'

    def edit_common_address_company_street_empty(self):
        """
        测试修改公司常用地址街道名称为空
        :return:
        """
        add_com_adress_comp_str_emp = AddCommonAdresstApi()
        add_com_adress_comp_str_emp.post({'data': {'addName': '河南省海门市南湖淮安街b座 138118', 'addType': 2, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': 'abcd'}, 'signStr': 'string'})
        assert add_com_adress_comp_str_emp.get_resp_code() == 0
        assert add_com_adress_comp_str_emp.get_resp_message() == 'OK'
        #查询公司常用地址
        get_com_adress_comp_str_emp = GetCommonAdress(mobile=add_com_adress_comp_str_emp.mobile)
        get_com_adress_comp_str_emp.get()
        get_res_data = get_com_adress_comp_str_emp.get_resp_data()
        assert get_com_adress_comp_str_emp.get_resp_code() == 0
        assert get_com_adress_comp_str_emp.get_resp_message() == 'OK'
        assert len(get_res_data)
        common_address_id = get_res_data[0]['id']
        # 修改公司常用地址街道名称为空
        edit_com_address_comp_str_emp = EditCommonAddressApi(mobile=add_com_adress_comp_str_emp.mobile)
        edit_com_address_comp_str_emp.post({'data': {'addName': 'oppo', 'areaName': 'oppo区', 'commonAddressId': common_address_id, 'lat': 111.1, 'lng': 120.1, 'streetName': ''}, 'signStr': 'string'})
        assert edit_com_address_comp_str_emp.get_resp_code() == 0
        assert edit_com_address_comp_str_emp.get_resp_message() == 'OK'
        # 查询修改后的公司常用地址
        get_edit_com_adress_comp_str_emp = GetCommonAdress(mobile=add_com_adress_comp_str_emp.mobile)
        get_edit_com_adress_comp_str_emp.get()
        get_edit_res_data = get_edit_com_adress_comp_str_emp.get_resp_data()
        assert get_edit_com_adress_comp_str_emp.get_resp_code() == 0
        assert get_edit_com_adress_comp_str_emp.get_resp_message() == 'OK'
        assert len(get_edit_res_data) == 1
        assert get_edit_res_data[0]['addName'] == 'oppo'
        assert get_edit_res_data[0]['addType'] == 2
        assert get_edit_res_data[0]['streetName'] == ''
        assert get_edit_res_data[0]['lng'] == '120.1'
        assert get_edit_res_data[0]['lat'] == '111.1'

    def edit_common_address_company_region_empty(self):
        """
        测试修改家公司用地址区域名称为空
        :return:
        """
        add_com_adress_comp_reg_emp = AddCommonAdresstApi()
        add_com_adress_comp_reg_emp.post({'data': {'addName': '辽宁省郑州市翔安陆路y座 969644', 'addType': 2, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '公路'}, 'signStr': 'string'})
        assert add_com_adress_comp_reg_emp.get_resp_code() == 0
        assert add_com_adress_comp_reg_emp.get_resp_message() == 'OK'
        # 查询公司常用地址
        get_com_adress_comp_reg_emp = GetCommonAdress(mobile=add_com_adress_comp_reg_emp.mobile)
        get_com_adress_comp_reg_emp.get()
        get_res_data = get_com_adress_comp_reg_emp.get_resp_data()
        assert get_com_adress_comp_reg_emp.get_resp_code() == 0
        assert get_com_adress_comp_reg_emp.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        common_address_id = get_res_data[0]['id']
        #修改公司常用地址区域为空
        edit_com_adress_comp_reg_emp = EditCommonAddressApi(mobile=add_com_adress_comp_reg_emp.mobile)
        edit_com_adress_comp_reg_emp.post({'data': {'addName': 'oppo', 'areaName': "", 'commonAddressId': common_address_id, 'lat': 111.1, 'lng': 120.1, 'streetName': 'oppo街道'}, 'signStr': 'string'})
        assert edit_com_adress_comp_reg_emp.get_resp_code() == 0
        assert edit_com_adress_comp_reg_emp.get_resp_message() == 'OK'
        # 查看修改后常用地址
        get_edit_com_adress_comp_reg_emp = GetCommonAdress(mobile=add_com_adress_comp_reg_emp.mobile)
        get_edit_com_adress_comp_reg_emp.get()
        edit_get_res_data = get_edit_com_adress_comp_reg_emp.get_resp_data()
        assert get_edit_com_adress_comp_reg_emp.get_resp_code() == 0
        assert get_edit_com_adress_comp_reg_emp.get_resp_message() == 'OK'
        assert len(edit_get_res_data) == 1

        assert edit_get_res_data[0]['addName'] == 'oppo'
        assert edit_get_res_data[0]['addType'] == 2
        assert edit_get_res_data[0]['streetName'] == 'oppo街道'
        assert edit_get_res_data[0]['lng'] == '120.1'
        assert edit_get_res_data[0]['lat'] == '111.1'

    def edit_common_address_company_region_street_empty(self):
        """
        测试修改公司常用地址区域名称和街道名称为空
        :return:
        """
        add_com_adress_comp_reg_str_emp = AddCommonAdresstApi()
        add_com_adress_comp_reg_str_emp.post({'data': {'addName': '江西省博县海港六盘水路R座 687126', 'addType': 2, 'areaName': '测试区域', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '张家港街'}, 'signStr': 'string'})
        assert add_com_adress_comp_reg_str_emp.get_resp_code() == 0
        assert add_com_adress_comp_reg_str_emp.get_resp_message() == 'OK'
        # 查询公司常用地址
        get_com_adress_comp_reg_str_emp = GetCommonAdress(mobile=add_com_adress_comp_reg_str_emp.mobile)
        get_com_adress_comp_reg_str_emp.get()
        get_res_data = get_com_adress_comp_reg_str_emp.get_resp_data()
        assert get_com_adress_comp_reg_str_emp.get_resp_code() == 0
        assert get_com_adress_comp_reg_str_emp.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        common_address_id = get_res_data[0]['id']
        # 修改公司常用地址区域和街道为空
        edit_com_adress_comp_reg_str_emp = EditCommonAddressApi(mobile=add_com_adress_comp_reg_str_emp.mobile)
        edit_com_adress_comp_reg_str_emp.post({'data': {'addName': 'oppo', 'areaName': "", 'commonAddressId': common_address_id, 'lat': 111.1, 'lng': 120.1, 'streetName': ""}, 'signStr': 'string'})
        assert edit_com_adress_comp_reg_str_emp.get_resp_code() == 0
        assert edit_com_adress_comp_reg_str_emp.get_resp_message() == 'OK'
        # 查询修改后的公司常用地址
        get_edit_address_comp_reg_str_emp = GetCommonAdress(mobile=add_com_adress_comp_reg_str_emp.mobile)
        get_edit_address_comp_reg_str_emp.get()
        get_edit_res_data = get_edit_address_comp_reg_str_emp.get_resp_data()
        assert get_edit_address_comp_reg_str_emp.get_resp_code() == 0
        assert get_edit_address_comp_reg_str_emp.get_resp_message() == 'OK'
        assert len(get_edit_res_data) == 1
        assert get_edit_res_data[0]['addName'] == 'oppo'
        assert get_edit_res_data[0]['addType'] == 2
        assert get_edit_res_data[0]['streetName'] == ''
        assert get_edit_res_data[0]['lng'] == '120.1'
        assert get_edit_res_data[0]['lat'] == '111.1'

    def edit_common_address_name_company_empty(self):
        """
        测试修改公司常用地址名称为空
        :return:
        """
        add_com_adress_name_company_emp = AddCommonAdresstApi()
        add_com_adress_name_company_emp.post({'data': {'addName': '陕西省云县黄浦合肥路w座 202949', 'addType': 2, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '司路'}, 'signStr': 'string'})
        assert add_com_adress_name_company_emp.get_resp_code() == 0
        assert add_com_adress_name_company_emp.get_resp_message() == 'OK'
        # 查询公司常用地址
        get_com_adress_name_emp = GetCommonAdress(mobile=add_com_adress_name_company_emp.mobile)
        get_com_adress_name_emp.get()
        get_res_data = get_com_adress_name_emp.get_resp_data()
        assert get_com_adress_name_emp.get_resp_code() == 0
        assert get_com_adress_name_emp.get_resp_message() == 'OK'
        assert len(get_res_data) == 1
        common_address_id = get_res_data[0]['id']
        # 修改公司常用地址名称为空
        edit_com_adress_name_emp = EditCommonAddressApi(mobile=add_com_adress_name_company_emp.mobile)
        edit_com_adress_name_emp.post({'data': {'addName': "", 'areaName': '测试区', 'commonAddressId': common_address_id, 'lat': 111.1, 'lng': 120.1, 'streetName': '司路'}, 'signStr': 'string'})
        assert edit_com_adress_name_emp.get_resp_code() == 100101
        assert edit_com_adress_name_emp.get_resp_message() == 'parameter_error'

    def edit_common_address_company_id_empty(self):
        """
        修改公司常用地址ID为空
        :return:
        """
        edit_com_adress_comp_id_emp = EditCommonAddressApi()
        edit_com_adress_comp_id_emp.post({'data': {'addName': "测试名称", 'areaName': '测试区', 'commonAddressId': '', 'lat': 111.1, 'lng': 120.1, 'streetName': '司路'}, 'signStr': 'string'})
        assert edit_com_adress_comp_id_emp.get_resp_code() == 100101
        assert edit_com_adress_comp_id_emp.get_resp_message() == 'parameter_error'

    def add_common_address_frequent_operation(self):
        """
        测试添加地址频繁操作
        :return:
        """
        add_com_adress_fre_oper = AddCommonAdresstApi(mobile=self.user_mobile)
        add_com_adress_fre_oper.post({"data": {"addName": "甘肃省淑珍县上街呼和浩特路R座 269118","addType": 1,"areaName": "测试区","locationInfo": {"lat": "39.9378","lng": "116.3266"},"streetName": "刘街"},"signStr": "string"})
        add_com_adress_fre_oper.post({'data': {'addName': '陕西省云县黄浦合肥路w座 202949', 'addType': 1, 'areaName': '测试区', 'locationInfo': {'lat': '39.9378', 'lng': '116.3266'}, 'streetName': '司路'}, 'signStr': 'string'})
        add_com_adress_fre_oper.post({"data": {"addName": "甘肃省淑珍县上街呼和浩特路R座 269118","addType": 1,"areaName": "测试区","locationInfo": {"lat": "39.9378","lng": "116.3266"},"streetName": "刘街"},"signStr": "string"})
        assert add_com_adress_fre_oper.get_resp_code() == 100104
        assert add_com_adress_fre_oper.get_resp_message() == 'do_not_frequent_operation'


if __name__ == '__main__':

    api = CommonAdressMonitoring()
    # api.setUp()
    # api.edit_common_address_home_street_empty()
    api.run_method(monitoring_name='常用地址管理监控', monitoring_class=api, redis_key=COMMON_ADDRESS_MONITORING_KEY)




