# -*- coding: utf-8 -*-
# @author: wangqianlong
# @email: 1763423314@qq.com
# @date: 2021/06/23
# 本模块将负责模型及算法结果输出：输出为文件，可视化等。

import matplotlib.pyplot as plt

# 模型求解结果可视化
def model_output_picture(X,model_inputdata,output_picture_path, number_of_orders, number_of_trucks):
    # 总图
    truck_color = ['g--', 'r--', 'y--']
    plt.figure()
    # 所有Pickup Deliver节点
    for node in range(1, model_inputdata.number_of_orders * 2 + 1):
        plt.scatter(model_inputdata.nodes.loc[node].x, model_inputdata.nodes.loc[node].y, s=5, color='#35b779')
        plt.text(model_inputdata.nodes.loc[node].x, model_inputdata.nodes.loc[node].y, '%s' % node, fontsize=5)
    # 所有的卡车
    for k in model_inputdata.K:
        plt.scatter(model_inputdata.nodes.loc[k.T_k_start].x, model_inputdata.nodes.loc[k.T_k_start].y, s=5, color='r')
        plt.text(model_inputdata.nodes.loc[k.T_k_start].x, model_inputdata.nodes.loc[k.T_k_start].y, 'truck%s'%k.id, fontsize=5)
    for k in model_inputdata.K:
        for i in k.V_k:
            for j in k.V_k:
                if X[i, j, k].x > 0.9:
                    x_plt = [model_inputdata.nodes.loc[i].x, model_inputdata.nodes.loc[j].x]
                    y_plt = [model_inputdata.nodes.loc[i].y, model_inputdata.nodes.loc[j].y]
                    plt.plot(x_plt, y_plt, truck_color[k.id - 1], linewidth=0.5)
    plt.savefig(output_picture_path + '\\%s-%s.png'%(number_of_orders, number_of_trucks), dpi=600)
    plt.show()

def model_output_txt(X, S, L, Z, obj_arph, obj_beita, obj_gama, model_inputdata, output_txt_path):
    output_txt_name = output_txt_path + '\\log-%s-%s.txt' % (model_inputdata.number_of_orders, model_inputdata.number_of_trucks)
    with open(output_txt_name, 'w') as txt:
        txt.write('obj_arph = %s, obj_beita = %s, obj_gama = %s\n' % (obj_arph.getValue(), obj_beita.getValue(), obj_gama.getValue()))
        for i in model_inputdata.V:
            for j in model_inputdata.V:
                for k in model_inputdata.K:
                    if X[i, j, k].x > 0.9:
                        txt_write = 'X[%s,%s,%s] = 1' % (i, j, k.id)
                        txt_write += '  S[%s,%s] = %s' % (i, k.id, S[i, k].x)
                        txt_write += '  L[%s,%s] = %s\n' % (i, k.id, L[i, k].x)
                        txt.write(txt_write)
        for i in model_inputdata.P:
            if Z[i].x >= 0.9:
                txt.write('Z[%s] = 1    ' % i)
