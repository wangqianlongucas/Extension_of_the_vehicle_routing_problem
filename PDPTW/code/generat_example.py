# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/08/07
# 本模块为模型数据结构定义

import pandas as pd
import random
import math

class Data_parameter():
    def __init__(self,path_of_file):
        # 需求数量
        self.number_of_orders = 10  # 个
        # 卡车数量
        self.number_of_trucks = 2  # 梁
        # 需求分布半径，直径为2*R
        self.R = 3  # 千米
        # 需求时间窗长度
        self.TWL = 0.5  # 小时
        # 需求时间窗波动长度的一半
        self.TWL_wave = 0.1  # 小时
        # 规划时间窗最大值，最小值为0
        self.Tmax = 4  # 小时
        # 需求重量下界
        self.demand_min = 0.5  # 千克
        # 需求重量上界
        self.demand_max = 0.75  # 千克
        # pickup的时间
        self.time_of_pickup = 2 / 60  # 小时
        # deliver的时间
        self.time_of_delivery = 3 / 60  # 小时
        # 算例生成位置
        self.outpath = path_of_file

# 需求生成
def orders_generate(data_parameter):
    orders_title = ['OID', 'Pickup', 'Delivery']
    orders_data = [[o, o, o + data_parameter.number_of_orders] for o in range(1, (data_parameter.number_of_orders + 1))]
    orders = pd.DataFrame(orders_data, columns=orders_title)
    orders_to_path = data_parameter.outpath + '\\orders-%s.csv' % data_parameter.number_of_orders
    orders.to_csv(orders_to_path, index=False)

#o_Pickup_deliver生成函数
def o_Pickup_Delivery(o,data_parameter):
    # 需求 o 的时间窗
    a = random.uniform(0,data_parameter.Tmax - data_parameter.TWL)
    # 需求时间窗在一定范围内波动
    o_TWL = data_parameter.TWL + random.uniform(-data_parameter.TWL_wave,data_parameter.TWL_wave)
    b = a + o_TWL
    # 需求重量（也在一定范围内波动）
    dm = random.uniform(data_parameter.demand_min, data_parameter.demand_max)
    # pickup的坐标及相关信息
    o_Pickup_r = random.uniform(0,data_parameter.R)
    o_Pickup_sita = random.uniform(0,2 * math.pi)
    o_Pickup = [o,'pickup%s'%o,o_Pickup_r * math.cos(o_Pickup_sita),o_Pickup_r * math.sin(o_Pickup_sita),a,b,dm,data_parameter.time_of_pickup]
    # delivery的坐标及相关信息
    o_Delivery_r = random.uniform(0,data_parameter.R)
    o_Delivery_sita = random.uniform(0,2 * math.pi)
    o_Delivery = [o + data_parameter.number_of_orders,'delivery%s'%o,o_Delivery_r * math.cos(o_Delivery_sita),o_Delivery_r * math.sin(o_Delivery_sita),a,b,-dm,data_parameter.time_of_delivery]
    return o_Pickup,o_Delivery

# Nodes函数Pickup节点（index）1···n和Delivery节点（index）：n+1···2*n
def nodes_generate(data_parameter):
    P = []
    D = []
    trucks = []
    for o in range(1, (data_parameter.number_of_orders + 1)):
        o_Pickup, o_Deliver = o_Pickup_Delivery(o,data_parameter)
        P.append(o_Pickup)
        D.append(o_Deliver)
    # 生成Nodes_trucks：index：2*n+1···2*n+m
    for truck in range(1, (data_parameter.number_of_trucks + 1)):
        Nodes_truck_r = random.uniform(0, data_parameter.R)
        Nodes_truck_sita = random.uniform(0, 2 * math.pi)
        Node_truck = [2 * data_parameter.number_of_orders + truck,'truck%s' % truck, Nodes_truck_r * math.cos(Nodes_truck_sita),
                       Nodes_truck_r * math.sin(Nodes_truck_sita), 0, data_parameter.Tmax, 0, 0]
        trucks.append(Node_truck)
    Nodes_title = ['ID', 'ID_name', 'x', 'y', 'a', 'b', 'dm', 'st']
    Nodes_data = P + D + trucks
    Nodes = pd.DataFrame(Nodes_data, columns=Nodes_title)
    Nodes_to_path = data_parameter.outpath + '\\Nodes-%s-%s.csv' % (data_parameter.number_of_orders, data_parameter.number_of_trucks)
    Nodes.to_csv(Nodes_to_path, index=False)

def log_generate(data_parameter):
    txt_path = data_parameter.outpath + '\\日志-%s-%s-%s.txt' % (data_parameter.number_of_orders, data_parameter.number_of_trucks, data_parameter.R)
    with open(txt_path, 'w') as f:
        text = ['需求数量\t', '卡车数量\t', '节点半径\t', '订单时间窗长度\t', '需求时间窗波动长度\t','总时间长度\t', '需求下限\t', '需求上限\t', 'pickup服务时间\t', 'delivery服务时间\t']
        text_value = [data_parameter.number_of_orders, data_parameter.number_of_trucks, data_parameter.R, data_parameter.TWL, 2 * data_parameter.TWL_wave, data_parameter.Tmax, data_parameter.demand_min, data_parameter.demand_max, data_parameter.time_of_pickup,data_parameter.time_of_delivery]
        for text_index in range(len(text)):
            f.write(text[text_index] + str(text_value[text_index]) + '\n')
# 算例生成
def data_generate(data_parameter):
    orders_generate(data_parameter)
    nodes_generate(data_parameter)
    log_generate(data_parameter)

if __name__ == '__main__' :
    path_of_file = 'F:\\Extension_of_the_vehicle_routing_problem\\PDPTW\\test_data'
    data_parameter = Data_parameter(path_of_file)
    data_generate(data_parameter)