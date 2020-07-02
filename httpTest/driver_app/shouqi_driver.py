# -*- coding:utf-8 -*-
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

class ShouQiDriver(object):
    """
    曹操司机端操作类
    """

    def __init__(self):
        self.home_page_activity = ' com.ichinait.gbdriver.activity.MainActivity'
        self.wait_time = 30
        self.poll_frequency = 0.5
        self.desired_caps = {}
        self.desired_caps['platformName'] = 'Android' # 手机平台
        self.desired_caps['platformVersion'] = '8.1' # 安卓版本
        self.desired_caps['deviceName'] = 'ZTGMS4VGSOBUU4OB' # 设备名称
        self.desired_caps['appPackage'] = 'com.ichinait.gbdriver' # 包名
        self.desired_caps['appActivity'] = 'com.ichinait.gbdriver.activity.SplashActivity' # 启动launch Activity
        self.desired_caps['automationName'] = 'Uiautomator2' # 使用Uiautomator2
        self.desired_caps['unicodeKeyboard'] = True # 使用unicode键盘
        self.desired_caps['resetKeyboard'] = True # 重置手机系统键盘设置
        self.desired_caps['noReset'] = True # 不清空数据
        self.desired_caps['newCommandTimeout'] = 180 # 无指令最长等待时间180秒
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
        return driver


    def driver_online(self):
        """
        滑动出车
        :return:
        """
        try:
            slide_car_bt= self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.FrameLayout[2]/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.LinearLayout')
        except NoSuchElementException:
            print('听单中')
        else:
            if slide_car_bt:
                self.driver.swipe(212, 1414, 629, 1414, 1000)
                time.sleep(4)


    def start_itinerary(self):

        #点击 我知道了
        confirm_bt = self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.TextView').click()
        # x1 = 56  y1 = 1443 x2 = 681
        slide_bt = self.find_element_by(By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout[2]/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.ImageView')
        end_itinerary_bt = self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.LinearLayout[2]/android.widget.TextView[2]')
        size = self.driver.get_window_size()
        #x 720 y 1520
        width = size['width']
        print(width)
        height = size['height']
        print(height)
        x1 = width * 0.08
        x2 = width * 0.95
        y1 = height * 0.95
        print('滑动前')
        for i in range(5):
            print('第{}次滑动'.format(i))
            if slide_bt:
                if end_itinerary_bt:
                    end_itinerary_bt.click()
                    time.sleep(2)
                    self.driver.swipe(x1, y1, x2, y1, 1000)
                self.driver.swipe(x1, y1, x2, y1, 1000)
                time.sleep(4)
        #滑动继续出车
        self.driver_online()


if __name__ == '__main__':
    shouqi = ShouQiDriver()
    shouqi.driver_online()
    shouqi.start_itinerary()

































