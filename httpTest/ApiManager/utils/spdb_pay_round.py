# -*- coding:utf-8 -*-
from HttpRunnerManager import settings
from ApiManager.utils.mysql_helper import mysql_execute
import time,requests
from ApiManager.utils import redis_helper





if __name__ == '__main__':
    max_count = 2000
    count = 1
    redis_helper.redis_execute().set(name=redis_helper.SPDB_PAYCB_ROUNT_MAX_NUMBER_KEY,value=max_count)
    while count < max_count:
        redis_helper.redis_execute().set(name=redis_helper.SPDB_PAYCB_ROUNT_CURRENT_NUMBER_KEY, value=count)
        orders = mysql_execute('select * from tbl_trade_order where order_status in (22,25)',is_fetchone=False,trade=True)
        if orders:
            print('Paying order number: {0}'.format(len(orders)))
            for x in orders:
                order_id = x['id']
                print('Start order id: {0}'.format(order_id))
                order_pay_record_detail = mysql_execute('select id from tbl_trade_order_pay_record where order_id=%s',params=(order_id), trade=True)
                pay_record_id = order_pay_record_detail['id']

                request_data = {"data": {
                    "bigOrderAmt": 5000,
                    "bigOrderDate": "2019-01-11",
                    "bigOrderDealDateTime": "2019-01-11 T 19:20:22",
                    "bigOrderNo": order_id,  # 订单号
                    "bigOrderReqNo": pay_record_id,  # 支付单ID
                    "bigOrderStatus": 'B',
                    "innerTransNo": "sadf3456789",
                    "marketAmt": 2000,
                    "respCode": "0000",
                    "respMsg": "成功"},
                    "interfaceId": "string",
                    "reqDateTime": "string",
                    "serviceCode": "string",
                    "sign": "string",
                    "signType": "string",
                    "version": "string"}
                response = requests.post(url='http://192.168.0.46:7102/paycb/api/pay/callback/notify', json=request_data, headers={'content-type': 'application/json; charset=UTF-8'}, timeout=5)
                print(response.content)
                count += 1
        else:
            print('No orders!')
            time.sleep(3)
            count += 1
