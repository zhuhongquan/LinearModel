# Linear model
## 一、目录文件
    ./data/:
        train.conll: 训练集
        dev.conll: 开发集
    ./big_data/
        train.conll: 训练集
        dev.conll: 开发集
        test.conll: 测试集
    ./src:
        linear_model.py: 初始版本的代码
        linear_model_v2.py: 速度更快的代码
    ./README.md: 使用说明

## 二、运行
### 1.运行环境
    python 3
### 2.运行方法
    各个参数
    'train_data_file': '../data/train.conll', #训练集文件,大数据改为'../big_data/train.conll'
    'dev_data_file': '../data/dev.conll',     #开发集文件,大数据改为'../big_data/dev.conll'
    'test_data_file': '../data/dev.conll',    #测试集文件,大数据改为'../big_data/test.conll'
    'averaged': False,                        #是否使用averaged percetron
    'iterator': 100,                           #最大迭代次数
    'stop_iterator': 10,                      #迭代stop_iterator次性能没有提升则结束
    
### 3.参考结果
#### (1)小数据测试

```
训练集：data/train.conll
开发集：data/dev.conll
```
|     文件名     | averaged percetron | 打乱数据 | 最优迭代轮次 | dev准确率 |  时间  |
| :-----------: | :----------------: | :------: | :---------: | :------: | :----: |
|linear_model.py|         ×          |    √     |    8/14    |   85.30%  | 151s |
|linear_model.py|         √          |    √     |    11/21   |  84.73%   | 289s |


#### (2)大数据测试

```
训练集：big-data/train.conll
开发集：big-data/dev.conll
测试集：big-data/test.conll
```

|     文件名     | averaged percetron | 打乱数据 | 最优迭代轮次 | dev准确率 |  时间  |
| :-----------: | :----------------: | :------: | :---------: | :------: | :----: |
|linear_model.py|         ×          |    √     |        |      |  |
|linear_model.py|         √          |    √     |        |      |  |

