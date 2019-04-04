from voc_eval import voc_eval
import os
FindPath = '/home/user/darknet/results/' #valid生成的测试结果文件路径
FileNames = os.listdir(FindPath)
#for file_name in FileNames:
for file in FileNames:
    file_name = file.split('.')[0]
    print(voc_eval('/home/user/darknet/results/{}.txt',  #valid生成的测试结果文件
              '/home/user/darknet/data/xml/{}.xml', #标签路径
              '/home/user/darknet/test.txt', #只需要测试集里面的图片名，不带路径和后缀
               file_name, '.'))

