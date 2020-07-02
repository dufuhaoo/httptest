# -*- coding:utf-8 -*-
from faker import Faker
from ApiManager.utils.mysql_helper import mysql_execute


class BaseFaker(object):
    """
    数据生成
    """

    def __init__(self):
        self.fak = Faker(locale='zh_CN')


    def create_name(self):
        """
        生成姓名
        :return:
        """
        return self.fak.name()

    def create_last_name(self):
        """
        生成姓氏
        :return:
        """
        return self.fak.last_name_female()

    def create_address(self):
        """
        生成地址
        :return:
        """
        return self.fak.address()

    def create_coordinate(self):
        """
        生成地理坐标
        :return:
        """
        return self.fak.geo_coordinate()

    def create_lng(self):
        """
        生成地理坐标（经度）
        :return:
        """
        return self.fak.longitude()

    def create_lat(self):
        """
        生成地理坐标（纬度）
        :return:
        """
        return self.fak.latitude()

    def create_company(self):
        """
        生成公司名称
        :return:
        """
        return self.fak.company()

    def create_phone_number(self):
        """
        生成手机号码
        :return:
        """
        return self.fak.phone_number()

    def create_ssn(self):
        """
        生成身份证号
        :return:
        """
        return self.fak.ssn()

    def create_street_name(self):
        """
        生成街道地址
        :return:
        """
        return self.fak.street_name()

    def create_user_name(self):
        """
        生成用户名
        :return:
        """
        return self.fak.user_name()

    def create_credit_card_security_code(self):
        """
        生成信用卡安全码
        :return:
        """
        return self.fak.credit_card_security_code()

    def create_sentence(self):
        """
        随机生成一句话
        :return:
        """
        return self.fak.sentence()

    def create_numerify(self):
        """
        随机生成三位随机数字
        :return:
        """
        return self.fak.numerify()


if __name__ == '__main__':
    print(BaseFaker().create_name())