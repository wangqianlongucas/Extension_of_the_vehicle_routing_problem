# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/08/08
# 本模块为模型数据结构定义

import pandas as pd

# 异质化卡车
class Truck():
    # 初始化
    def __init__(self, id, start, end, P, D):
        self.id = id
        self.speed = 35
        self.C_k = 3
        self.T_k_start = start
        self.T_k_end = end
        self.P_k = P
        self.D_k = D
        self.N_k = self.P_k + self.D_k
        self.V_k = self.N_k + [self.T_k_start, self.T_k_end]

class Model_inputdata():
    # 初始化：读取数据和生成参数
    def __init__(self,path_of_file, number_of_orders, number_of_trucks):
        # 读取需求数据和节点数据
        self.orders = pd.read_csv(path_of_file + '\\orders-%s.csv'%number_of_orders, index_col=0)
        # Nodes[0]表示无人机服务站,Nodes[-1]表示配送员出发点
        self.nodes = pd.read_csv(path_of_file + '\\Nodes-%s-%s.csv'%(number_of_orders, number_of_trucks), index_col=0)
        # 需求初始化
        # Pickup节点
        self.P = list(self.orders['Pickup'])
        # Deliver节点
        self.D = list(self.orders['Delivery'])
        # 需求数量
        self.number_of_orders = len(self.P)

        # 卡车数量
        self.number_of_trucks = len(self.nodes) - 2 * self.number_of_orders
        # 卡车初始化{卡车id,卡车对象}，id从1开始
        self.K = [Truck(truck, 2 * len(self.orders) + truck,2 * len(self.orders) + self.number_of_trucks + truck,self.P, self.D) for truck in range(1, self.number_of_trucks + 1)]
        # T_ks_start 为所有的卡车出发点
        self.T_ks_start = [2 * len(self.orders) + truck for truck in range(1, self.number_of_trucks + 1)]
        # T_ks_end 为所有的卡车结束点
        self.T_ks_end = [2 * len(self.orders) + self.number_of_trucks + truck for truck in range(1, self.number_of_trucks + 1)]
        # 卡车的结束节点相关数据生成
        for truck in self.T_ks_start:
            self.nodes.loc[truck + self.number_of_trucks] = self.nodes.loc[truck]

        # 节点处理
        self.N = self.P + self.D
        self.V = self.N + self.T_ks_start + self.T_ks_end
        # 异质性修改 示例：将前两个需求和后两个需求分别从卡车1，2中移除
        PDs = [[self.P[2:], self.D[2:]], [self.P[:-2], self.D[:-2]]]
        for truck in self.K:
            self.heterogeneous_truck(truck, PDs[truck.id - 1][0], PDs[truck.id - 1][1])
        # 设置K_i（order_ks）
        self.order_ks = {order: [] for order in self.P}
        for order in self.P:
            for truck in self.K:
                if order in truck.P_k:
                    self.order_ks[order].append(truck)
        # 目标函数系数
        self.arph, self.beita, self.gama = 1, 1, 8
        # 其他参数
        self.M = [10, 100, 1000, 10000, 100000]

    # 异质性处理函数
    def heterogeneous_truck(self,truck,P_new,D_new):
        truck.P_k, truck.D_k = P_new, D_new
        # N_k,V_k修改
        truck.N_k = P_new + D_new
        truck.V_k = truck.N_k + [truck.T_k_start, truck.T_k_end]


if __name__ == '__main__' :
    path_of_file = 'F:\\Extension_of_the_vehicle_routing_problem\\PDPTW\\test_data'
    number_of_orders, number_of_trucks = 10, 2
    model_inputdata = Model_inputdata(path_of_file, number_of_orders, number_of_trucks)