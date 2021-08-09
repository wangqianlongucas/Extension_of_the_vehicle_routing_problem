# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/08/08
# 本模块为模型建立及优化部分
# 求解速度和规模待测试

import math as m
import matplotlib.pyplot as plt
from gurobipy import *
from model_data import *
from output import *
import time

# 初始化模型参数函数
def model_initial_parameter(model,model_inputdata):
    model.Params.TimeLimit = 600
    model.Params.MIPGap = 0.2 / model_inputdata.M[1]

# 模型变量添加函数
def add_vars(model,model_inputdata):
    X = model.addVars(model_inputdata.V, model_inputdata.V, model_inputdata.K, vtype=GRB.BINARY, name='X')
    S = model.addVars(model_inputdata.V, model_inputdata.K, vtype=GRB.CONTINUOUS, name='S')
    L = model.addVars(model_inputdata.V, model_inputdata.K, vtype=GRB.CONTINUOUS, name='L')
    Z = model.addVars(model_inputdata.P, vtype=GRB.BINARY, name='Z')
    return X, S, L, Z

# 模型目标设置函数
def set_objective(model, X, S, Z, model_inputdata):
    obj_arph = quicksum(m.sqrt((model_inputdata.nodes.loc[i].x - model_inputdata.nodes.loc[j].x) ** 2 +
                        (model_inputdata.nodes.loc[i].y - model_inputdata.nodes.loc[j].y) ** 2) * X[i, j, k]
                        for k in model_inputdata.K for i in model_inputdata.V for j in model_inputdata.V)
    obj_beita = quicksum(S[k.T_k_end, k] - model_inputdata.nodes.loc[k.T_k_start].a for k in model_inputdata.K)
    obj_gama = quicksum(Z[i] for i in model_inputdata.P)
    # 模型添加目标
    obj = obj_arph * model_inputdata.arph + obj_beita * model_inputdata.beita + obj_gama * model_inputdata.gama
    model.setObjective(obj,GRB.MINIMIZE)
    return obj_arph, obj_beita, obj_gama

# 约束条件
def orders_been_service_or_in_request_bank(model, X, Z, model_inputdata):
    model.addConstrs(quicksum(X[i, j, k] for k in model_inputdata.order_ks[i] for j in k.N_k) + Z[i] == 1 for i in model_inputdata.P)

def pickup_and_delivery_been_same_truck(model, X, model_inputdata):
    model.addConstrs(
        quicksum(X[i, j, k] for j in k.V_k) - quicksum(X[j, i + model_inputdata.number_of_orders, k] for j in k.V_k) == 0 for k in model_inputdata.K for i in k.P_k)

def start_end_flow_balance(model, X, model_inputdata):
    model.addConstrs(quicksum(X[k.T_k_start, j, k] for j in k.P_k + [k.T_k_end]) == 1 for k in model_inputdata.K)
    model.addConstrs(quicksum(X[i, k.T_k_end, k] for i in k.D_k + [k.T_k_start]) == 1 for k in model_inputdata.K)
    model.addConstrs(quicksum(X[i, j, k] for i in k.V_k) - quicksum(X[j, i, k] for i in k.V_k) == 0 for k in model_inputdata.K for j in k.N_k)

def time_limit(model, X, S, model_inputdata):
    model.addConstrs(S[i, k] + model_inputdata.nodes.loc[i].st + m.sqrt(
        (model_inputdata.nodes.loc[i].x - model_inputdata.nodes.loc[j].x) ** 2 +
        (model_inputdata.nodes.loc[i].y - model_inputdata.nodes.loc[j].y) ** 2) / k.speed <= S[j, k]
                     + (1 - X[i, j, k]) * model_inputdata.M[0] for k in model_inputdata.K for i in k.V_k for j in k.V_k)
    model.addConstrs(S[i, k] == [model_inputdata.nodes.loc[i].a, model_inputdata.nodes.loc[i].b] for k in model_inputdata.K for i in k.V_k)
    # 此处不用大于等于0的约束，order.a 大于等于0

def pickup_befor_delivery(model, S, model_inputdata):
    model.addConstrs(S[i, k] <= S[i + model_inputdata.number_of_orders, k] for k in model_inputdata.K for i in k.P_k)

def weight_limit(model, X, L, model_inputdata):
    model.addConstrs(L[i, k] + model_inputdata.nodes.loc[i].dm <= L[j, k] + (1 - X[i, j, k]) * model_inputdata.M[1] for k in model_inputdata.K for i in k.V_k for j in k.V_k)
    model.addConstrs(L[i, k] + model_inputdata.nodes.loc[i].dm >= L[j, k] - (1 - X[i, j, k]) * model_inputdata.M[1] for k in model_inputdata.K for i in k.V_k for j in k.V_k)
    model.addConstrs(L[i, k] == [0, k.C_k] for k in model_inputdata.K for i in k.V_k)
    # 受本函数中的其他约束的限制，下列约束模型会自动优化
    # model.addConstrs(L[k.T_k_start, k] == 0 for k in model_inputdata.K)
    # model.addConstrs(L[k.T_k_end, k] == 0 for k in model_inputdata.K)

def constraints(model, X, S, L, Z, model_inputdata):
    orders_been_service_or_in_request_bank(model, X, Z, model_inputdata)
    pickup_and_delivery_been_same_truck(model, X, model_inputdata)
    start_end_flow_balance(model, X, model_inputdata)
    time_limit(model, X, S, model_inputdata)
    pickup_befor_delivery(model, S, model_inputdata)
    weight_limit(model, X, L, model_inputdata)

if __name__ == '__main__' :
    # 初始化数据
    path_of_file = 'C:\\Users\\Administrator\\Desktop\\公众号\\模型复现\\2006-Stefan\\test_data'
    number_of_orders, number_of_trucks = 10, 2
    model_inputdata = Model_inputdata(path_of_file, number_of_orders, number_of_trucks)
    # 建立模型
    model = Model('model')
    # 模型参数初始化
    model_initial_parameter(model,model_inputdata)
    # 添加模型变量
    X, S, L, Z = add_vars(model,model_inputdata)
    # 设置模型求解目标
    obj_arph, obj_beita, obj_gama = set_objective(model, X, S, Z, model_inputdata)
    # 添加模型约束
    constraints(model, X, S, L, Z, model_inputdata)
    # 求解
    t_s = time.time()
    model.optimize()
    t_e = time.time()
    # 输出
    if model.Status == 3:
        print('约束冲突')
        # 输出约束冲突内容
        model.computeIIS()
        model.write('model.ilp')
    elif model.Status == 2:
        best_value = model.objVal
        # 可视化
        output_picture_path = path_of_file
        model_output_picture(X, model_inputdata, output_picture_path, number_of_orders, number_of_trucks)
        print('(', obj_arph.getValue(), ',', obj_beita.getValue(), ',', obj_gama.getValue(), ')', t_e - t_s)
        # 输出lp文件
        model.write('model.lp')
    else:
        print('未求出可行解')

