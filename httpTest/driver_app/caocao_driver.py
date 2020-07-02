# -*- coding:utf-8 -*-
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from ApiManager.utils.base_logger import BaseLogger
from ApiManager.utils.redis_helper import redis_execute,CAOCAO_DRIVER_COMMAND
import time,re,json


logger = BaseLogger(__name__).get_logger()


class CaoCaoDriver(object):
    """
    曹操司机端操作类
    指令规则：
    1、online 司机端上线，结果：1 成功 0 失败
    2、down 司机端下线，结果：1 成功 0 失败
    3、dispatched 接单，结果：1 成功 0 失败
    4、arrived 已到达，结果：1 成功 0 失败
    5、serviceStarted 行程中，结果：1 成功 0 失败
    6、serviceFinished 结束服务，结果：1 成功 0 失败
    7、canceled 订单取消，结果：1 成功 0 失败
    """

    def __init__(self):
        self.home_page_activity = 'cn.caocaokeji.driver_home.module.home.HomeActivity'
        self.wait_time = 20
        self.poll_frequency = 0.3
        self.desired_caps = {}
        self.desired_caps['platformName'] = 'Android' # 手机平台
        self.desired_caps['platformVersion'] = '9' # 安卓版本
        # self.desired_caps['platformVersion'] = '8.1' # 安卓版本
        self.desired_caps['deviceName'] = 'RFCM90228PE' # 设备名称
        # self.desired_caps['deviceName'] = 'ZTGMS4VGSOBUU4OB' # 设备名称
        self.desired_caps['appPackage'] = 'com.taobao.taobao' # 包名
        self.desired_caps['appActivity'] = 'com.taobao.tao.welcome.Welcome' # 启动launch Activity
        # self.desired_caps['automationName'] = 'Uiautomator2' # 使用Uiautomator2
        self.desired_caps['unicodeKeyboard'] = True # 使用unicode键盘
        self.desired_caps['resetKeyboard'] = True # 重置手机系统键盘设置
        self.desired_caps['noReset'] = True # 不清空数据
        self.desired_caps['newCommandTimeout'] = 86400 # 无指令最长等待时间
        self.driver = self.start_app()

    def find_element_by(self, by , selector):
        """
        定位方法封装，判断元素可见
        :param by:
        :param selector:
        :return:
        """
        return WebDriverWait(self.driver, self.wait_time,self.poll_frequency).until(expected_conditions.presence_of_element_located((by , selector)))

    def start_app(self):
        """
        启动APP返回driver
        :return:
        """
        driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub",self.desired_caps)
        # 等主页面activity出现,20秒内
        driver.wait_activity(self.home_page_activity, 20)
        logger.info('CaoCao Driver APP started successfully!')
        return driver

    def driver_online(self):
        """
        司机端上线
        :return:
        """
        try:
            # 点击上线
            before_online_text = self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.TextView').text
            assert before_online_text == '点击上线'
            self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.ImageView[2]').click()
            logger.info('The driver is online successfully!')
            return True
        except:
            return False

    def driver_down(self):
        """
        司机端下线
        :return:
        """
        try:
            element = self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.ImageView[4]')
            bounds_str = element.get_attribute('bounds')
            result = re.findall("\[.*?\]", bounds_str)
            coordinates = []
            for x in result:
                coordinates.append(eval(x))
            start_coordinate = coordinates[0]
            end_coordinate = coordinates[1]
            x1 = int(start_coordinate[0])
            y1 = int((start_coordinate[1]))
            x2 = int(end_coordinate[0])
            y2 = int(end_coordinate[1])
            self.driver.tap([(x1,y1),(x2,y2)],50)
            return True
        except:
            return False

    def get_start_address(self):
        """
        获取起点地址名称
        :return:
        """
        try:
            text = self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.RelativeLayout[1]/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.TextView').text
            return text
        except:
            return None

    def get_end_address(self):
        """
        获取终点地址名称
        :return:
        """
        try:
            text = self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.RelativeLayout[1]/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.RelativeLayout[3]/android.widget.TextView').text
            return text
        except:
            return None

    def start_service(self):
        """
        点击前往服务
        :return:
        """
        try:
            start_service_bt = self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.LinearLayout/android.widget.RelativeLayout[3]/android.widget.TextView')
            assert start_service_bt.text == '前往服务'
            start_service_bt.click()
            logger.info('Already gone to service!')
            start_address = self.get_start_address()
            end_address = self.get_end_address()
            logger.info('The start address:{0}'.format(start_address))
            logger.info('The end address:{0}'.format(end_address))
            return True
        except:
            logger.info('No orders!')
            return False

    def sliding_element(self,bounds_str):
        """
        元素滑动
        :return:
        """
        try:
            result = re.findall("\[.*?\]", bounds_str)
            coordinates = []
            for x in result:
                coordinates.append(eval(x))
            start_coordinate = coordinates[0]
            end_coordinate  = coordinates[1]
            x1 = int(start_coordinate[0] + 10)
            x2 = int(end_coordinate[0] - 10)
            y1 = int((start_coordinate[1] + end_coordinate[1]) / 2)
            self.driver.swipe(x1,y1,x2,y1)
            return True
        except:
            return False


    def update_order_status(self):
        """
        订单状态变更
        :return:
        """
        element = self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.view.View')
        bounds_str = element.get_attribute('bounds')
        if self.sliding_element(bounds_str):
            return True
        else:
            return False

    def canceled(self):
        """
        订单被取消
        :return:
        """
        try:
            self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.TextView').click()
            return True
        except:
            return False

    def additional_charge(self,high_speed_fee,bridge_fee,park_fee,other_fee):
        """
        添加额外费用
        :return:
        """
        try:
            # 点击添加额外费用按钮
            self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.TextView[3]').click()
            # 添加高速费
            self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.LinearLayout[1]/android.widget.RelativeLayout[2]/android.widget.EditText').send_keys(high_speed_fee)
            # 添加路桥费
            self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.LinearLayout[1]/android.widget.RelativeLayout[3]/android.widget.EditText').send_keys(bridge_fee)
            # 添加停车费
            self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.LinearLayout[1]/android.widget.RelativeLayout[4]/android.widget.EditText').send_keys(park_fee)
            # 添加其他费用
            self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.LinearLayout[1]/android.widget.RelativeLayout[5]/android.widget.EditText').send_keys(other_fee)
            # 点击保存按钮
            self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.LinearLayout[1]/android.widget.RelativeLayout[6]/android.widget.TextView').click()
        except:
            return False


    def end_trip(self,high_speed_fee='',bridge_fee='',park_fee='',other_fee=''):
        """
        订单结束
        :return:
        """
        try:
            #确定订单费用
            self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.TextView[2]').click()
            self.additional_charge(high_speed_fee,bridge_fee,park_fee,other_fee)
            #在线支付
            self.find_element_by(By.XPATH,'/hierarchy / android.widget.FrameLayout / android.widget.LinearLayout / android.widget.FrameLayout / android.widget.LinearLayout / android.widget.FrameLayout / android.widget.RelativeLayout / android.widget.LinearLayout[1] / android.widget.TextView ').click()
            #停止接单
            self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout[2]/android.widget.TextView[2]').click()
            return True
        except:
            return False


if __name__ == '__main__':
    caocao = CaoCaoDriver()
    while True:
        result = None
        command = redis_execute().get(name=CAOCAO_DRIVER_COMMAND)
        if command:
            command_format = json.loads(command)
            event = command_format['event']
            event_status = command_format['status']
            if int(event_status) == 0:
                logger.info('New Command:{0}'.format(command_format))
                if event == 'down':
                    result = caocao.driver_down()
                elif event == 'dispatched':
                    caocao.driver_online()
                    result = caocao.start_service()
                elif event == 'arrived':
                    result = caocao.update_order_status()
                elif event == 'serviceStarted':
                    result = caocao.update_order_status()
                elif event == 'serviceFinished':
                    event_fee_detail = command_format['fee_detail']
                    high_speed_fee = event_fee_detail['high_speed_fee']
                    bridge_fee = event_fee_detail['bridge_fee']
                    park_fee = event_fee_detail['park_fee']
                    other_fee = event_fee_detail['other_fee']
                    caocao.update_order_status()
                    result = caocao.end_trip(high_speed_fee=high_speed_fee,bridge_fee=bridge_fee,park_fee=park_fee,other_fee=other_fee)
                elif event == 'canceled':
                    result = caocao.canceled()
                command_format['status'] = 1
                if result:
                    command_format['result'] = 1
                else:
                    command_format['result'] = 0
                redis_execute().set(name=CAOCAO_DRIVER_COMMAND, value=json.dumps(command_format))
            else:
                logger.info('No new instructions at present!')
                time.sleep(1)
        else:
            logger.info('No instruction!')
            time.sleep(1)

