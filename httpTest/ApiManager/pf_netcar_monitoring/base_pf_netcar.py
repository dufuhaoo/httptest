# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.trade.distance_price_api import DistancePriceApi,TransferDistancePriceApi
from ApiManager.pf_netcar_api.trade.create_order_api import CreateOrderApi,CreateTransferOrderApi
from ApiManager.pf_netcar_api.trade.flight_info_api import FlightInfoApi
from ApiManager.utils.base_logger import BaseLogger
import time

logger = BaseLogger(__name__).get_logger()


city_code = '010'
city_name = '北京市'
# 公益西桥坐标点
start_point = '公益西桥'
from_lat = '39.831240'
from_lng = '116.369840'
# 天通苑坐标点
end_point = '天通苑'
to_lat = '40.063590'
to_lng = '116.419670'

location_code = 'PEK'
# 北京首都国际机场T1航站楼
airport_point_T1 = '北京首都国际机场T1航站楼'
airport_lat_T1 = '40.082803'
airport_lng_T1 = '116.593689'
# 北京首都国际机场T2航站楼
airport_point_T2 = '北京首都国际机场T1航站楼'
airport_lat_T2 = '40.044632'
airport_lng_T2 = '116.597686'


def request_distance_price_api():
    """
    请求实时单询价接口
    :return:
    """
    distance_price_api = DistancePriceApi()
    distance_price_api.get({'cityCode': city_code, 'cityName': city_name, 'fromLat': from_lat, 'fromLng': from_lng,'orderType': 1, 'toLat': to_lat, 'toLng': to_lng,'startAddr':start_point,'endAddr':end_point})
    assert distance_price_api.get_status_code() == 200
    assert distance_price_api.get_resp_code() == 0
    data = distance_price_api.get_resp_data()
    assert data['cityName'] == city_name
    vehicle_info_list = data['vehicleInfoList']
    assert len(vehicle_info_list) != 0
    return vehicle_info_list

def request_transfer_distance_price_api(booking_date=None,order_type=None,flignt_no='MU5121',wait_time=20):
    """
    请求接送机询价接口
    :return:
    """
    data = None
    if order_type == 3: # 送机
        data = {'bookingDate': booking_date, # 预定时间
                'cityCode': city_code, # 城市编码
                'cityName': city_name, # 起点城市名称
                'endAddr': airport_point_T1,  # 终点名称
                'flt': None, # 航班号
                'flightDate': None, # 航班时间
                'fromLat': from_lat, # 起点坐标
                'fromLng': from_lng, # 起点坐标
                'locationCode': location_code, # 机场三字码
                'orderType': 3,  # 订单类型
                'startAddr': start_point,  # 起点名称
                'toLat': airport_lat_T1, # 终点坐标
                'toLng': airport_lng_T1}
    elif order_type == 2: # 送机
        flight_info_api = FlightInfoApi()
        flight_info_api.get({'departDate': booking_date, 'arriveAirportCode': None, 'departAirportCode': None,'flightNo': flignt_no})
        assert flight_info_api.get_status_code() == 200
        assert flight_info_api.get_resp_code() == 0
        plan_depart_time = flight_info_api.get_resp_data()['flights'][0]['planArriveTime']
        # 将航班落地时间转换为时间戳
        plan_depart_time_timeArray = time.strptime(plan_depart_time, "%Y-%m-%d %H:%M:%S")
        plan_depart_time_timeArray_format = int(time.mktime(plan_depart_time_timeArray))
        # 航班抵达X分钟后用车转换为秒
        wait_time_format = wait_time * 60
        # 计算计划用车时间
        book_date_timeArray = int(plan_depart_time_timeArray_format + wait_time_format)
        time_local = time.localtime(book_date_timeArray)
        # 计划用车时间格式转换
        book_date = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

        data = {'bookingDate': book_date, # 预定时间
                'cityCode': city_code, # 城市编码
                'cityName': city_name, # 起点城市名称
                'endAddr': end_point,  # 终点名称
                'flt': flignt_no, # 航班号
                'flightDate': plan_depart_time, # 航班时间
                'fromLat': airport_lat_T2, # 起点坐标
                'fromLng': airport_lng_T2, # 起点坐标
                'locationCode': location_code, # 机场三字码
                'orderType': 2,  # 订单类型
                'startAddr': airport_point_T2,  # 起点名称
                'toLat': to_lat, # 终点坐标
                'toLng': to_lng}

    transfer_distance_price_api = TransferDistancePriceApi()
    transfer_distance_price_api.get(data)
    assert transfer_distance_price_api.get_status_code() == 200
    assert transfer_distance_price_api.get_resp_code() == 0
    data = transfer_distance_price_api.get_resp_data()
    assert data['cityName'] == city_name
    vehicle_info_list = data['vehicleInfoList']
    assert len(vehicle_info_list) != 0
    return vehicle_info_list


def get_distance_price_car_detail(channel_name=None,random=False):
    """
    实时单根据渠道获取预估价车型信息
    :param channel_name:
    :return:
    """
    if not random:
        brand_code = None
        if channel_name == 'cc':
            brand_code = 1
        elif channel_name == 'sq':
            brand_code = 2
        elif channel_name == 'sz':
            brand_code = 4
        elif channel_name == 'yg':
            brand_code = 5

        car_group_list = request_distance_price_api()
        for group in car_group_list:
            for car_detail in group['carDetail']:
                if brand_code == int(car_detail['brandCode']):
                    return {'groupDetail':{'carType':group['carType'],'carTypeName':group['carTypeName']},'carDetail':car_detail}
                else:
                    continue
    else:
        car_group_list = request_distance_price_api()
        for group in car_group_list:
            if car_group_list:
                for car_detail in group['carDetail']:
                    return {'groupDetail':{'carType':group['carType'],'carTypeName':group['carTypeName']},'carDetail':car_detail}
            else:
                continue

def request_create_order_api(user_mobile,car_detail,user_type,open_sign_force):
    """
    请求下单接口
    :return:
    """
    call_car_list = []
    brand = car_detail['brandCode']
    type = car_detail['carCode']
    original_price = int(car_detail['originalPrice'])
    price_token = car_detail['priceToken']

    global city_code
    # 膝盖首汽与神州city_code传值
    if int(car_detail['brandCode']) == 2:
        city_code = '44'
    elif int(car_detail['brandCode']) == 4:
        city_code = '1'

    call_car_list.append({"brand": str(brand), "type": int(type), "estimatedAmount": original_price,"priceToken": price_token, "cityCode": city_code})

    create_order_api = CreateOrderApi(mobile=user_mobile,user_type=user_type,open_sign_force=open_sign_force)
    create_order_api.post({"startPoint": start_point,"endPoint": end_point,"fromLng": from_lng,"fromLat": from_lat,
                           "toLng": to_lng,"toLat": to_lat,"cityCode": city_code,
                           "cityName": city_name,"vehicleDTOList": call_car_list})
    assert create_order_api.get_status_code() == 200
    order_id =  None
    if create_order_api.get_resp_code() == 0:
        create_order_resp_data = create_order_api.get_resp_data()
        order_id = create_order_resp_data['orderId']
    create_order_resp_message = create_order_api.get_resp_message()
    return {"order_id":order_id,'user_mobile':create_order_api.mobile,'message':create_order_resp_message,'resp_code':create_order_api.get_resp_code()}

def request_create_transfer_order_api(user_mobile,car_detail,user_type,open_sign_force,booking_date=None,order_type=None,passenger_mobile=None,passenger_name=None,wait_time=20,flight_no=None):
    """
    接送机请求下单接口
    :return:
    """
    call_car_list = []
    brand = car_detail['brandCode']
    type = car_detail['carCode']
    original_price = int(car_detail['originalPrice'])
    price_token = car_detail['priceToken']
    car_name = car_detail['carName']

    global city_code
    # 膝盖首汽与神州city_code传值
    if int(car_detail['brandCode']) == 2:
        city_code = '44'
    elif int(car_detail['brandCode']) == 4:
        city_code = '1'

    call_car_list.append({"brand": str(brand), "type": int(type), "estimatedAmount": original_price,"priceToken": price_token, "cityCode": city_code})
    data = None
    if order_type == 3: # 送机
        data = {
                "arrCode": location_code,
                "brand": brand,
                "cityCode": city_code,
                "cityName": city_name,
                "couponId": None,
                "depCode": '',
                "departureTime": booking_date,
                "endName": airport_point_T2,
                "estimatedAmount": original_price,
                "flightDelayTime": '',
                "flightTime": '',
                "flt":'',
                "fromLat":from_lat,
                "fromLng":from_lng,
                "groupName":car_name,
                "orderType":'3',
                "passenger":{
                    "mobile":passenger_mobile,
                    "name":passenger_name
                },
                "priceToken":price_token,
                "startName":start_point,
                "toLat":airport_lat_T2,
                "toLng":airport_lng_T2,
                "type":type
            }
    elif order_type == 2: # 接机
        data = {
                "arrCode": '',
                "brand": brand,
                "cityCode": city_code,
                "cityName": city_name,
                "couponId": None,
                "depCode": location_code,
                "departureTime": booking_date,
                "endName": end_point,
                "estimatedAmount": original_price,
                "flightDelayTime": wait_time,
                "flightTime": '',
                "flt":flight_no,
                "fromLat":airport_lat_T2,
                "fromLng":airport_lng_T2,
                "groupName":car_name,
                "orderType":'3',
                "passenger":{
                    "mobile":passenger_mobile,
                    "name":passenger_name
                },
                "priceToken":price_token,
                "startName":airport_point_T2,
                "toLat":to_lat,
                "toLng":to_lng,
                "type":type
            }

    create_transfer_order_api = CreateTransferOrderApi(mobile=user_mobile,user_type=user_type,open_sign_force=open_sign_force)
    create_transfer_order_api.post(data)
    assert create_transfer_order_api.get_status_code() == 200
    order_id =  None
    if create_transfer_order_api.get_resp_code() == 0:
        create_order_resp_data = create_transfer_order_api.get_resp_data()
        order_id = create_order_resp_data['orderId']
    create_order_resp_message = create_transfer_order_api.get_resp_message()
    return {"order_id":order_id,'user_mobile':create_transfer_order_api.mobile,'message':create_order_resp_message,'resp_code':create_transfer_order_api.get_resp_code()}


def create_order(user_mobile=None,user_type=40,channel_name=None,open_sign_force=True,random_channel=False):
    """
    创建实时单订单
    :return:
    """
    distance_price_detail = None
    count = 1
    max_count = 3
    while count < max_count:
        distance_price_detail = get_distance_price_car_detail(channel_name,random_channel)
        if distance_price_detail:
            break
        else:
            count += 1
            time.sleep(1)
    assert count < max_count
    car_detail = distance_price_detail['carDetail']
    create_order_detail = request_create_order_api(user_mobile=user_mobile,car_detail=car_detail,user_type=user_type,open_sign_force=open_sign_force)
    return create_order_detail


def create_transfer_pick_up_order(user_mobile=None,user_type=40,channel_name=None,open_sign_force=True,flight_date=None,passenger_mobile=None,passenger_name=None,flignt_no='MU5121',wait_time=20):
    """
    创建接送机接机订单
    :return:
    """
    # 请求航班查询接口
    flight_info_api = FlightInfoApi()
    flight_info_api.get({'departDate': flight_date, 'arriveAirportCode': None, 'departAirportCode': None, 'flightNo': flignt_no})
    assert flight_info_api.get_status_code() == 200
    assert flight_info_api.get_resp_code() == 0
    plan_arrive_time = flight_info_api.get_resp_data()['flights'][0]['planArriveTime']
    plan_depart_time = flight_info_api.get_resp_data()['flights'][0]['planDepartTime']
    arrive_terminal_name = flight_info_api.get_resp_data()['flights'][0]['arriveAirport']['terminalName']
    # 将航班落地时间转换为时间戳
    plan_arrive_time_timeArray = time.strptime(plan_arrive_time, "%Y-%m-%d %H:%M:%S")
    plan_arrive_time_timeArray_format = int(time.mktime(plan_arrive_time_timeArray))
    # 航班抵达X分钟后用车转换为秒
    wait_time_format = wait_time * 60
    # 计算计划用车时间
    book_date_timeArray = int(plan_arrive_time_timeArray_format + wait_time_format)
    time_local = time.localtime(book_date_timeArray)
    # 计划用车时间格式转换
    book_date = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    # 请求查询预估价格接口
    global city_code
    data = {'bookingDate': book_date,  # 预定时间
            'cityCode': city_code,  # 城市编码
            'cityName': city_name,  # 起点城市名称
            'endAddr': end_point,  # 终点名称
            'flt': flignt_no,  # 航班号
            'flightDate': plan_depart_time,  # 航班时间
            'fromLat': airport_lat_T2,  # 起点坐标
            'fromLng': airport_lng_T2,  # 起点坐标
            'locationCode': location_code,  # 机场三字码
            'orderType': 2,  # 订单类型
            'startAddr': arrive_terminal_name,  # 起点名称
            'toLat': to_lat,  # 终点坐标
            'toLng': to_lng,
            'terminalCode':0,
            'flightDelayTime':wait_time}
    transfer_distance_price_api = TransferDistancePriceApi()
    transfer_distance_price_api.get(data)
    assert transfer_distance_price_api.get_status_code() == 200
    assert transfer_distance_price_api.get_resp_code() == 0
    data = transfer_distance_price_api.get_resp_data()
    assert data['cityName'] == city_name
    vehicle_info_list = data['vehicleInfoList']
    assert len(vehicle_info_list) != 0
    brand_code = None
    if channel_name == 'cc':
        brand_code = 1
    elif channel_name == 'sq':
        brand_code = 2
    elif channel_name == 'sz':
        brand_code = 4
    brand = None
    type = None
    original_price = None
    price_token = None
    car_name = None
    for group in vehicle_info_list:
        for car_detail in group['carDetail']:
            if brand_code == int(car_detail['brandCode']):
                brand = car_detail['brandCode']
                type = car_detail['carCode']
                original_price = int(car_detail['originalPrice'])
                price_token = car_detail['priceToken']
                car_name = car_detail['carName']

    if brand and type and original_price and price_token and car_name:
        # 覆盖首汽与神州city_code传值
        if brand == 2:
            city_code = '44'
        elif brand == 4:
            city_code = '1'

        # 请求下单接口
        data = {"arrCode": '',
                    "brand": brand,
                    "cityCode": city_code,
                    "cityName": city_name,
                    "couponId": None,
                    "depCode": location_code,
                    "departureTime": plan_arrive_time,
                    "endName": end_point,
                    "estimatedAmount": original_price,
                    "flightDelayTime": wait_time,
                    "flightTime":plan_depart_time ,
                    "flt":flignt_no,
                    "fromLat":airport_lat_T2,
                    "fromLng":airport_lng_T2,
                    "groupName":car_name,
                    "orderType":'2',
                    "passenger":{
                        "mobile":passenger_mobile,
                        "name":passenger_name},
                    "priceToken":price_token,
                    "startName":airport_point_T2,
                    "toLat":to_lat,
                    "toLng":to_lng,
                    "type":type
                }
        create_transfer_order_api = CreateTransferOrderApi(mobile=user_mobile,user_type=user_type,open_sign_force=open_sign_force)
        create_transfer_order_api.post(data)
        assert create_transfer_order_api.get_status_code() == 200
        order_id =  None
        if create_transfer_order_api.get_resp_code() == 0:
            create_order_resp_data = create_transfer_order_api.get_resp_data()
            order_id = create_order_resp_data['orderId']
        create_order_resp_message = create_transfer_order_api.get_resp_message()
        return {"order_id":order_id,'user_mobile':create_transfer_order_api.mobile,'message':create_order_resp_message,'resp_code':create_transfer_order_api.get_resp_code()}


def create_transfer_drop_off_order(user_mobile=None,user_type=40,channel_name=None,open_sign_force=True,booking_date=None,passenger_mobile=None,passenger_name=None):
    """
    创建接送机送机订单
    :return:
    """
    # 请求查询预估价格接口
    global city_code
    data = {'bookingDate': booking_date,  # 预定时间
            'cityCode': city_code,  # 城市编码
            'cityName': city_name,  # 起点城市名称
            'endAddr': airport_point_T2,  # 终点名称
            'flt': None,  # 航班号
            'flightDate': None,  # 航班时间
            'fromLat': from_lat,  # 起点坐标
            'fromLng': from_lng,  # 起点坐标
            'locationCode': location_code,  # 机场三字码
            'orderType': 2,  # 订单类型
            'startAddr': start_point,  # 起点名称
            'toLat': airport_lat_T2,  # 终点坐标
            'toLng': airport_lng_T2}
    transfer_distance_price_api = TransferDistancePriceApi()
    transfer_distance_price_api.get(data)
    assert transfer_distance_price_api.get_status_code() == 200
    assert transfer_distance_price_api.get_resp_code() == 0
    data = transfer_distance_price_api.get_resp_data()
    assert data['cityName'] == city_name
    vehicle_info_list = data['vehicleInfoList']
    assert len(vehicle_info_list) != 0
    brand_code = None
    if channel_name == 'cc':
        brand_code = 1
    elif channel_name == 'sq':
        brand_code = 2
    elif channel_name == 'sz':
        brand_code = 4
    brand = None
    type = None
    original_price = None
    price_token = None
    car_name = None
    for group in vehicle_info_list:
        for car_detail in group['carDetail']:
            if brand_code == int(car_detail['brandCode']):
                brand = car_detail['brandCode']
                type = car_detail['carCode']
                original_price = int(car_detail['originalPrice'])
                price_token = car_detail['priceToken']
                car_name = car_detail['carName']

    if brand and type and original_price and price_token and car_name:
        # 覆盖首汽与神州city_code传值
        if brand == 2:
            city_code = '44'
        elif brand == 4:
            city_code = '1'

        # 请求下单接口
        data = {"arrCode": location_code,
                    "brand": brand,
                    "cityCode": city_code,
                    "cityName": city_name,
                    "couponId": None,
                    "depCode": None,
                    "departureTime": booking_date,
                    "endName": airport_point_T2,
                    "estimatedAmount": original_price,
                    "flightDelayTime": None,
                    "flightTime":None ,
                    "flt":None,
                    "fromLat":from_lat,
                    "fromLng":from_lng,
                    "groupName":car_name,
                    "orderType":'2',
                    "passenger":{
                        "mobile":passenger_mobile,
                        "name":passenger_name},
                    "priceToken":price_token,
                    "startName":start_point,
                    "toLat":airport_lat_T2,
                    "toLng":airport_lng_T2,
                    "type":type
                }
        create_transfer_order_api = CreateTransferOrderApi(mobile=user_mobile,user_type=user_type,open_sign_force=open_sign_force)
        create_transfer_order_api.post(data)
        assert create_transfer_order_api.get_status_code() == 200
        order_id = None
        if create_transfer_order_api.get_resp_code() == 0:
            create_order_resp_data = create_transfer_order_api.get_resp_data()
            order_id = create_order_resp_data['orderId']
        create_order_resp_message = create_transfer_order_api.get_resp_message()
        return {"order_id":order_id,'user_mobile':create_transfer_order_api.mobile,'message':create_order_resp_message,'resp_code':create_transfer_order_api.get_resp_code()}




if __name__ == '__main__':
    transfer_distance_price = create_transfer_pick_up_order(channel_name='cc',flight_date='2019-10-24',passenger_mobile='13501077762',passenger_name='张三')
    print(transfer_distance_price)
