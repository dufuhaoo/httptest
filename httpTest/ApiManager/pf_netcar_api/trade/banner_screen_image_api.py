
# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi
from ApiManager.pf_netcar_api.base_api import BaseApi

class BannerImageApi(LoginBaseApi):
    """
    banner图片地址
    """
    url =  '/netCar/page/query/banner'

class ScreenImageApi(BaseApi):
    """
    弹屏图片地址
    """
    url =  '/netCar/page/query/playScreen'

