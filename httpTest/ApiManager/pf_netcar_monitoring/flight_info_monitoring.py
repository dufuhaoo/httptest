# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from ApiManager.pf_netcar_api.trade.flight_info_api import FlightInfoApi
from ApiManager.pf_netcar_api.trade.query_port_info_api import QueryAirPortInfoApi
from ApiManager.utils.redis_helper import FLIGHT_INFO_MONITORING
import datetime


class FlightInfoMonitoring(BaseMonitoring):
    """
    航班信息航站楼接口监控
    """
    now_time = datetime.datetime.now()

    def query_flight_info(self):
        """
        查询航班信息
        :return:
        """
        # 按照航班号查询国内航班
        today = (self.now_time + datetime.timedelta(hours=+1)).strftime("%Y-%m-%d") # 当前日期
        tomorrow = (self.now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d") # 明天日期
        day_after_tomorrow = (self.now_time + datetime.timedelta(days=+2)).strftime("%Y-%m-%d") # 后天日期
        next_week_today = (self.now_time + datetime.timedelta(weeks=+1)).strftime("%Y-%m-%d") # 下周日期
        next_month_today = (self.now_time + datetime.timedelta(weeks=+4)).strftime("%Y-%m-%d") # 下个月日期

        for x in [today,tomorrow,day_after_tomorrow,next_week_today,next_month_today]:
            flight_no = 'MF8456'
            flight_info_api = FlightInfoApi()
            flight_info_api.get({'departDate': x, 'arriveAirportCode': None, 'departAirportCode': None, 'flightNo': flight_no})
            assert flight_info_api.get_status_code() == 200
            assert flight_info_api.get_resp_code() == 0
            assert flight_info_api.get_resp_message() == 'OK'
            flight_info_data = flight_info_api.get_resp_data()['flights']
            assert len(flight_info_data) != 0
            # assert flight_info_data[0]['airlineInfo']['name'] == '厦门航空有限公司'
            # assert flight_info_data[0]['departAirport']['cityName'] == '重庆'
            # assert flight_info_data[0]['departAirport']['code'] == 'CKG'
            # assert flight_info_data[0]['departAirport']['terminalName'] == '重庆江北T3'
            # assert flight_info_data[0]['arriveAirport']['cityName'] == '北京'
            # assert flight_info_data[0]['arriveAirport']['code'] == 'PEK'
            # assert flight_info_data[0]['arriveAirport']['terminalName'] == '北京首都T2'
            # assert flight_info_data[0]['flightNo'] == flight_no
            # assert flight_info_data[0]['status'] == 0
            flight_no = 'KN2218'
            flight_info_api = FlightInfoApi()
            flight_info_api.get({'departDate': x, 'arriveAirportCode': None, 'departAirportCode': None, 'flightNo': flight_no})
            assert flight_info_api.get_status_code() == 200
            assert flight_info_api.get_resp_code() == 0
            assert flight_info_api.get_resp_message() == 'OK'
            flight_info_data = flight_info_api.get_resp_data()['flights']
            assert len(flight_info_data) != 0
            # assert flight_info_data[0]['airlineInfo']['name'] == '中国联合航空有限公司'
            # assert flight_info_data[0]['departAirport']['cityName'] == '上海'
            # assert flight_info_data[0]['departAirport']['code'] == 'SHA'
            # assert flight_info_data[0]['departAirport']['terminalName'] == '上海虹桥T2'
            # assert flight_info_data[0]['arriveAirport']['cityName'] == '天津'
            # assert flight_info_data[0]['arriveAirport']['code'] == 'TSN'
            # assert flight_info_data[0]['arriveAirport']['terminalName'] == '天津滨海T2'
            # assert flight_info_data[0]['flightNo'] == flight_no
            # assert flight_info_data[0]['status'] == 0
            # 按照航班号查询国外飞国内航班
            flight_no = 'NH963'
            flight_info_api = FlightInfoApi()
            flight_info_api.get({'departDate': x, 'arriveAirportCode': None, 'departAirportCode': None, 'flightNo': flight_no})
            assert flight_info_api.get_status_code() == 200
            assert flight_info_api.get_resp_code() == 0
            assert flight_info_api.get_resp_message() == 'OK'
            flight_info_data = flight_info_api.get_resp_data()['flights']
            assert len(flight_info_data) != 0
            # if flight_info_data[0]['airlineInfo']['name'] == '全日本航空公司':
            #     assert flight_info_data[0]['departAirport']['cityName'] == '东京'
            #     assert flight_info_data[0]['departAirport']['code'] == 'HND'
            #     assert flight_info_data[0]['departAirport']['terminalName'] == '东京羽田INTL'
            #     assert flight_info_data[0]['arriveAirport']['cityName'] == '北京'
            #     assert flight_info_data[0]['arriveAirport']['code'] == 'PEK'
            #     assert flight_info_data[0]['arriveAirport']['terminalName'] == '北京首都T3'
            #     assert flight_info_data[0]['flightNo'] == flight_no
            #     assert flight_info_data[0]['status'] == 0
            # else:
            #     assert flight_info_data[1]['airlineInfo']['name'] == '全日本航空公司'
            #     assert flight_info_data[1]['departAirport']['cityName'] == '东京'
            #     assert flight_info_data[1]['departAirport']['code'] == 'HND'
            #     assert flight_info_data[1]['departAirport']['terminalName'] == '东京羽田I'
            #     assert flight_info_data[1]['arriveAirport']['cityName'] == '北京'
            #     assert flight_info_data[1]['arriveAirport']['code'] == 'PEK'
            #     assert flight_info_data[1]['arriveAirport']['terminalName'] == '北京首都T3'
            #     assert flight_info_data[1]['flightNo'] == flight_no
            #     assert flight_info_data[1]['status'] == 0
            flight_no = 'MH360'
            flight_info_api = FlightInfoApi()
            flight_info_api.get({'departDate': x, 'arriveAirportCode': None, 'departAirportCode': None, 'flightNo': flight_no})
            assert flight_info_api.get_status_code() == 200
            assert flight_info_api.get_resp_code() == 0
            assert flight_info_api.get_resp_message() == 'OK'
            flight_info_data = flight_info_api.get_resp_data()['flights']
            assert len(flight_info_data) != 0
            # assert flight_info_data[0]['airlineInfo']['name'] == '马来西亚航空公司'
            # assert flight_info_data[0]['departAirport']['cityName'] == '吉隆坡'
            # assert flight_info_data[0]['departAirport']['code'] == 'KUL'
            # assert flight_info_data[0]['departAirport']['terminalName'] == '吉隆坡M'
            # assert flight_info_data[0]['arriveAirport']['cityName'] == '北京'
            # assert flight_info_data[0]['arriveAirport']['code'] == 'PEK'
            # assert flight_info_data[0]['arriveAirport']['terminalName'] == '北京首都T3'
            # assert flight_info_data[0]['flightNo'] == flight_no
            # assert flight_info_data[0]['status'] == 0
            # 按照起降地查询航班
            start_code = 'PEK' # 北京
            end_code = 'PVG' # 上海浦东
            flight_info_api = FlightInfoApi()
            flight_info_api.get(
                {'departDate': x, 'arriveAirportCode': end_code, 'departAirportCode': start_code, 'flightNo': None})
            assert flight_info_api.get_status_code() == 200
            assert flight_info_api.get_resp_code() == 0
            assert flight_info_api.get_resp_message() == 'OK'
            flight_info_data = flight_info_api.get_resp_data()['flights']
            assert len(flight_info_data) != 0
            # for i in flight_info_data:
            #     assert i['airlineInfo']['name'] != None
            #     assert i['departAirport']['cityName'] == '北京'
            #     assert i['departAirport']['code'] == start_code
            #     assert i['departAirport']['terminalName'] != None
            #     assert i['arriveAirport']['cityName'] == '上海'
            #     assert i['arriveAirport']['code'] == end_code
            #     assert i['arriveAirport']['terminalName'] != None
            #     assert i['flightNo'] != flight_no
            #     assert i['status'] == 0
            #     assert x in i['planArriveTime']
            #     assert x in i['planDepartTime']

    def query_air_port_info(self):
        """
        查询航站楼
        :return:
        """
        query_airport_api = QueryAirPortInfoApi()
        query_airport_api.get()
        assert query_airport_api.get_status_code() == 200
        assert query_airport_api.get_resp_code() == 0
        assert query_airport_api.get_resp_message() == 'OK'
        airport_data = query_airport_api.get_resp_data()
        assert len(airport_data) == 224
        for x in airport_data:
            assert x['name'] != None
            assert x['enName'] != None
            if x['terminalDetail']:
                for i in x['terminalDetail']:
                    assert i['locationCode'] != None
                    assert i['locationName'] != None

if __name__ == '__main__':
    api = FlightInfoMonitoring()
    api.run_method(monitoring_name='查询航班航站楼信息监控',monitoring_class=api,redis_key=FLIGHT_INFO_MONITORING)
    # api.query_flight_info()