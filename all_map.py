from voc_eval import voc_eval
import os
FindPath = '/home/lzm/data/darknet/results/' #valid生成的测试结果文件路径
FileNames = os.listdir(FindPath)
#for file_name in FileNames:
for file in FileNames:
    file_name = file.split('.')[0]
    print(voc_eval('/home/lzm/data/darknet/results/{}.txt',  #valid生成的测试结果文件
              '/home/lzm/data/darknet/gpu_train/xml/{}.xml', #标签路径
              '/home/lzm/data/darknet/test.txt', #只需要train.txt里面的图片名，不带路径和后缀
               file_name, '.'))

