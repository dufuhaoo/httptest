# -*- coding:utf-8 -*-
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

class YangGuangDriver(object):
    """
    曹操司机端操作类
    """

    def __init__(self):
        self.home_page_activity = 'com.jryg.driver/com.jryg.driver.activity.home.YGAHomePageActivity'
        self.wait_time = 30
        self.poll_frequency = 0.5
        self.desired_caps = {}
        self.desired_caps['platformName'] = 'Android' # 手机平台
        self.desired_caps['platformVersion'] = '8.1' # 安卓版本
        self.desired_caps['deviceName'] = '7ce460e6' # 设备名称
        self.desired_caps['appPackage'] = 'com.jryg.driver' # 包名
        self.desired_caps['appActivity'] = 'com.jryg.driver.activity.loading.YGALoadingActivity' # 启动launch Activity
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
        司机端上线
        :return:
        """
        # 点击上线
        print('点击上线')
        try:
            car_bt= self.driver.find_element_by_xpath("//*[contains(@text,'点击出车')]")
        except NoSuchElementException:
            print('已经出车')
        else:
            car_bt.click()

        # #点击休息
        # ‘/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.TextView[3]’

    def check_cancelBt(self):

        print('check cancelBt')
        try:
            cancelBt = self.find_element_by(By.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.ImageView')
        except NoSuchElementException:
            print('no cancelBt')
        else:
            cancelBt.click()


    def start_itinerary(self):

        # x1 = 56  y1 = 1443 x2 = 681
        slide_bt = self.find_element_by(By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.ImageView')
        size = self.driver.get_window_size()
        width = size['width']
        print(width)
        height = size['height']
        print(height)
        x1 = width*0.08
        x2 = width*0.95
        y1 = height*0.95
        print('滑动前')
        for i in range(5):
            print('第{}次滑动'.format(i))
            if slide_bt:
                self.driver.swipe(x1,y1,x2,y1,1000)
                time.sleep(4)


if __name__ == '__main__':
    yanguang = YangGuangDriver()
    yanguang.check_cancelBt()
    yanguang.driver_online()
    yanguang.start_itinerary()
































