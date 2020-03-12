#coding=utf-8
import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class Yolov3LogVisualization:

    def __init__(self,log_path,result_dir):

        self.log_path = log_path
        self.result_dir = result_dir

    #解析log文件，去掉冗余日志
    def extract_log(self, save_log_path, key_word):
        with open(self.log_path, 'r') as f:
            with open(save_log_path, 'w') as train_log:
                next_skip = False
                for line in f:
                    if next_skip:
                        next_skip = False
                        continue
                    # 去除多gpu的同步log
                    if 'Syncing' in line:
                        continue
                    # 去除零错误的log
                    if 'nan' in line:
                        continue
                    #去掉保存权重的log
                    if 'Saving weights to' in line:
                        next_skip = True
                        continue
                    if key_word in line:
                        train_log.write(line)
        f.close()
        train_log.close()

    #抽取loss日志
    def parse_loss_log(self,log_path, line_num=2000):

        #去掉前一千个loss较大的数据，后面每十个取一个
        result = pd.read_csv(log_path, skiprows=[x for x in range(line_num) if ((x % 10 != 9) | (x < 1000))],error_bad_lines=False, names=['loss', 'avg', 'rate', 'seconds', 'images'])
        result['loss'] = result['loss'].str.split(' ').str.get(1)
        result['avg'] = result['avg'].str.split(' ').str.get(1)
        result['rate'] = result['rate'].str.split(' ').str.get(1)
        result['seconds'] = result['seconds'].str.split(' ').str.get(1)
        result['images'] = result['images'].str.split(' ').str.get(1)

        result['loss'] = pd.to_numeric(result['loss'])
        result['avg'] = pd.to_numeric(result['avg'])
        result['rate'] = pd.to_numeric(result['rate'])
        result['seconds'] = pd.to_numeric(result['seconds'])
        result['images'] = pd.to_numeric(result['images'])
        return result

    #生成loss图函数
    def gene_loss_pic(self, pd_loss):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(pd_loss['avg'].values, label='avg_loss')
        ax.legend(loc='best')
        ax.set_title('The loss curves')
        ax.set_xlabel('batches')
        fig.savefig(self.result_dir + '/avg_loss')
        logger.info('save iou loss done')

    #保存loss日志和loss图
    def Loss_log_pic(self):
        train_log_loss_path = os.path.join(self.result_dir, 'train_log_loss.txt')
        self.extract_log(train_log_loss_path, 'images')
        pd_loss = self.parse_loss_log(train_log_loss_path)
        self.gene_loss_pic(pd_loss) 

    #对loss日志
    def parse_iou_log(self,log_path, line_num=2000):
        result = pd.read_csv(log_path, skiprows=[x for x in range(line_num) if (x % 10 == 0 or x % 10 == 9)],error_bad_lines=False,names=['Region Avg IOU', 'Class', 'Obj', 'No Obj', 'Avg Recall', 'count'])
        result['Region Avg IOU'] = result['Region Avg IOU'].str.split(': ').str.get(1)
        result['Class'] = result['Class'].str.split(': ').str.get(1)
        result['Obj'] = result['Obj'].str.split(': ').str.get(1)
        result['No Obj'] = result['No Obj'].str.split(': ').str.get(1)
        result['Avg Recall'] = result['Avg Recall'].str.split(': ').str.get(1)
        result['count'] = result['count'].str.split(': ').str.get(1)

        result['Region Avg IOU'] = pd.to_numeric(result['Region Avg IOU'])
        result['Class'] = pd.to_numeric(result['Class'])
        result['Obj'] = pd.to_numeric(result['Obj'])
        result['No Obj'] = pd.to_numeric(result['No Obj'])
        result['Avg Recall'] = pd.to_numeric(result['Avg Recall'])
        result['count'] = pd.to_numeric(result['count'])
        return result

    def gene_iou_pic(self, pd_loss):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(pd_loss['Region Avg IOU'].values, label='Region Avg IOU')
        # ax.plot(result['Class'].values,label='Class')
        # ax.plot(result['Obj'].values,label='Obj')
        # ax.plot(result['No Obj'].values,label='No Obj')
        # ax.plot(result['Avg Recall'].values,label='Avg Recall')
        # ax.plot(result['count'].values,label='count')
        ax.legend(loc='best')
        ax.set_title('The Region Avg IOU curves')
        ax.set_xlabel('batches')
        fig.savefig(self.result_dir + '/region_avg_iou')
        logger.info('save iou pic done')

    #保存 IOU日志和IOU图
    def Iou_log_pic(self):
        train_log_loss_path = os.path.join(self.result_dir, 'train_log_iou.txt')
        self.extract_log(train_log_loss_path, 'IOU')
        pd_loss = self.parse_iou_log(train_log_loss_path)
        self.gene_iou_pic(pd_loss)


if __name__ == '__main__':

    log_path = 'train.log'  #自己的训练日志
    result_dir = 'results'  #生成的loss，iou图和日志保存的路径
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    LogVisual = Yolov3LogVisualization(log_path,result_dir)
    LogVisual.Loss_log_pic()
    LogVisual.Iou_log_pic()
