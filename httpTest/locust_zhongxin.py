# -*- coding:utf-8 -*-
from locust import HttpLocust, TaskSet, task
import json,random,time

def on_report_to_master(client_id, data):
    data['mars'] = 'loo'
    print("Slave: Client %s, data " % client_id, data)

def on_slave_report(client_id, data):
    print("Master Recive: Client %s, data " % client_id, data)

class WebTasks(TaskSet):


    @task(5)  # 通过@task()装饰的方法为一个事务，方法的参数用于指定该行为的执行权重，参数越大每次被虚拟用户执行的概率越高，默认为1
    def near_car_api(self):
        """
        查询附近车辆接口请求
        :return:
        """
        request_url = '/netCar/page/query/nearCar'
        request_headers = {'Content-Type': 'application/json'}
        # 创建临时文件，记录网络状态码与接口响应结果
        result_file = open('./locust_near_car_result.txt','a+',encoding='utf-8')
        coordinates = [] # 坐标点列表
        # 北京市西单大悦城
        coordinates.append({'lng':'116.379488','lat':'39.916902'})
        # 南京市夫子庙
        coordinates.append({'lng':'118.795758','lat':'32.027757'})
        # 上海市外滩
        coordinates.append({'lng':'121.511969','lat':'31.25539'})
        # 成都市成都火车站
        coordinates.append({'lng':'104.079853','lat':'30.703259'})
        # 青岛五四广场
        coordinates.append({'lng':'120.386944','lat':'36.069199'})
        # 深圳市远望科技城
        coordinates.append({'lng':'114.116389','lat':'22.563179'})
        # 杭州市杭州东站
        coordinates.append({'lng':'120.219396','lat':'30.297149'})
        # 广州市东山湖公园
        coordinates.append({'lng':'113.298465','lat':'23.122361'})
        # 南宁市广西大学
        coordinates.append({'lng':'108.29703','lat':'22.850984'})
        # 哈尔滨市世纪广场
        coordinates.append({'lng':'126.690798','lat':'45.757155'})
        # 生成随机索引获取地址坐标点
        random_index = random.randint(0,len(coordinates) - 1)
        print(random_index)
        random_coordinate = coordinates[random_index]
        print(random_coordinate)
        # 组装请求参数
        request_data = {}
        request_data.update(random_coordinate)
        request_data.update({'radius':10000})
        print(request_data)
        print('Test Url:{0}'.format(request_url))
        print('Request Data:{0}'.format(request_data))
        print('Request Headers:{0}'.format(request_headers))
        request_time = time.time()
        with self.client.get(request_url,params=request_data,headers=request_headers,timeout=10,catch_response=True) as response:
            print('Resopnse Text:{0}'.format(response.text))
            result_file.write(str({'status_code':response.status_code,'response':response.text,'request_time':request_time}))
            result_file.close()
            if response.status_code == 200:  # 对http响应码是否200进行判断
                response.success()
            else:
                response.failure("Abnormal network status!")

            if json.loads(response.text)['code'] == 0:
                response.success()
            else:
                response.failure("Interface response exception!")


    @task(4)
    def distance_price_api(self):
        """
        实时单查询预估价格接口
        :return:
        """
        request_url = '/netCar/page/query/distancePrice'
        request_headers = {'content-type': 'application/json'}
        # 创建临时文件，记录网络状态码与接口响应结果
        result_file = open('./locust_distance_price_result.txt', 'a+', encoding='utf-8')
        request_data_1 = {'cityCode':'010','cityName':'北京市','fromLat':'39.93855','fromLng':'116.3266','toLat':'39.867676','toLng':'116.378036','orderType':'1','startAddr':'腾达大厦','endAddr':'北京南站(公交站)'}
        request_data_2 = {'cityCode':'010','cityName':'北京市','fromLat':'39.866133','fromLng':'116.377428','toLat':'39.995724','toLng':'116.449884','orderType':'1','startAddr':'北京南站(北出口)','endAddr':'望京西(地铁站)'}
        request_data_3 = {'cityCode':'010','cityName':'北京市','fromLat':'39.936188','fromLng':'116.417023','toLat':'39.852715','toLng':'116.359299','orderType':'1','startAddr':'东四十二条(公交站)','endAddr':'草桥南(公交站)'}
        request_data_list = []
        request_data_list.append(request_data_1)
        request_data_list.append(request_data_2)
        request_data_list.append(request_data_3)
        request_data = request_data_list[random.randint(0,len(request_data_list) - 1)]
        print('Test Url:{0}'.format(request_url))
        print('Request Data:{0}'.format(request_data))
        print('Request Headers:{0}'.format(request_headers))
        request_time = time.time()
        with self.client.get(request_url, params=request_data, headers=request_headers,timeout=20,catch_response=True) as response:
            print('Resopnse Text:{0}'.format(response.text))
            result_file.write(str({'status_code':response.status_code,'response':response.text,'request_time':request_time}))
            result_file.close()
            if response.status_code == 200:  # 对http响应码是否200进行判断
                response.success()
            else:
                response.failure("Abnormal network status!")

            if json.loads(response.text)['code'] == 0 and json.loads(response.text)['data'] is not None:
                response.success()
            else:
                response.failure("Interface response exception!")

    @task(4)
    def sz_callback_for_pipe(self):
        """
        神州订单回调pipe落地
        :param request:
        :return:
        """
        call_back_url = 'http://tcnl.ywsk.cn:37000/pfCallbackGateway/callback/szCallbackOrderStatusNotify'
        headers = {'content-type': 'application/json; charset=UTF-8'}

        file = open('./zhongxin_test_order_detail.txt','a+')
        all_detail = file.readlines()
        for x in all_detail:
            channel_order_id = json.loads(x)['channel_order_id']  # 渠道ID
            partner_order_id = json.loads(x)['pipe_order_id']

            change_status_request_data = {"bankFlag": 1, "content": {"dOrderId": partner_order_id, "eventExplanation": "",
                                                                     "orderId": channel_order_id,"status": 'dispatched'},
                                          "operation": "statusChanged"}

            request_encrypt = self.client.get(url='http://192.168.0.46:7003/szNetCarCallback/callback/getEncrypt', params={'q': str(change_status_request_data)},headers=headers)

            with self.client.get(url=call_back_url, params={'q': request_encrypt.text}, headers=headers) as resp:
                if resp.status_code != 200:
                    resp.failure("Interface response exception!")
                resp_content = json.loads(resp.content)
                if resp_content['status'] == 200:
                    resp.success()
                else:
                    resp.failure("Interface response exception!")
        file.close()


    def query_air_port(self):
        """
        查询机场
        :return:
        """
        url = 'https://citictest.ywsk.cn:7104/netCar/page/query/queryAirPortInfo'
        with self.client.get(url=url) as response:
            if response.status_code == 200:  # 对http响应码是否200进行判断
                response.success()
            else:
                response.failure("Abnormal network status!")

            if json.loads(response.text)['code'] == 0 and json.loads(response.text)['data'] is not None:
                response.success()
            else:
                response.failure("Interface response exception!")



class WebsiteUser(HttpLocust):
    host = "https://citictest.ywsk.cn:7104"  # 被测系统的host，在终端中启动locust时没有指定--host参数时才会用到
    task_set = WebTasks  # TaskSet类，该类定义用户任务信息，必填。这里就是:WebsiteTasks类名,因为该类继承TaskSet；
    min_wait = 500  # 每个用户执行两个任务间隔时间的上下限（毫秒）,具体数值在上下限中随机取值，若不指定默认间隔时间固定为1秒
    max_wait = 1000

