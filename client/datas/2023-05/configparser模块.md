# configparser模块

#### 配置文件(test.ini)

```ini
# 这是注释
; 这也是注释

[default]
delay = 10
compression = true
compression_Level = 2
language_code = en-us
time_zone = UTC
salary = 3.5

[db]
db_type : mysql
database_name = catalogue_data
user = root
password = root
host = 127.0.0.1
port = 3306
charset = utf8

```



#### 读取

```python
import configparser

config = configparser.ConfigParser()
config.read('data/test.ini', encoding='utf-8')

#查看所有的标题
sections = config.sections()
print(sections)
>>>['default', 'db']

#查看标题default下所有key=value的key
options = config.options('default')
print(options)
>>>['delay', 'compression', 'compression_level', 'language_code', 'time_zone', 'salary']

#查看标题default下所有key=value的(key,value)格式
li = config.items('default')
print(li)
>>>[('delay', '10'), ('compression', 'true'), ('compression_level', '2'), ('language_code', 'en-us'), ('time_zone', 'UTC'), ('salary', '3.5')]

#查看标题default下delay的值=>字符串格式
val = config.get('default', 'delay')
print(val)
>>>10

#查看标题default下delay的值=>整数格式
int_val = config.getint('default','delay')
print(int_val)
>>>10

#查看标题default下salary的值=>浮点型格式
float_val = config.getfloat('default','salary')
print(float_val)
>>>3.5

#查看标题default下compression的值=>布尔值格式
bool_val = config.getboolean('default','compression')
print(bool_val)
>>>True
```





#### 修改

```python
import configparser

config=configparser.ConfigParser()
config.read('data/test.ini', encoding='utf-8')

#删除整个标题default(包括下面的配置项)
config.remove_section('default')

#删除标题default下的compression和delay
config.remove_option('default', 'compression')
config.remove_option('default', 'delay')

#判断是否存在某个标题
print(config.has_section('default'))

#判断标题default下是否有delay
print(config.has_option('default', 'delay'))

#添加一个section
config.add_section('connect')

#在标题connect下添加thread=10的配置(如果没有此配置，则会创建配置项，如果已有此配置，则修改原配置项)
config.set('connect', 'thread', '10')
config.set('connect', 'thread', 10) # 这样写回报错，必须写字符串格式

#最后将修改的内容写入文件,完成最终的修改
config.write(open('test.ini', 'w'))


```



#### 创建

```python

import configparser
  
config = configparser.ConfigParser()
config["default"] = {'delay': '15',
                      'compression': 'false',
                     'compression_Level': '3'}
  
config['db'] = {}
config['db']['User'] = 'root'
config['db2'] = {}
topsecret = config['db2']
topsecret['port'] = '3306'
topsecret['compression'] = 'true'
config['default']['compression'] = 'true'
with open('data/test.ini', 'w') as f:
   config.write(f)
```



<p align="right"><a href="https://v.ixigua.com/2asfSbf/">@author:小飞有点东西</a></p>
<p align="right"><a href="https://active.clewm.net/FrcyFA">点我获取更多资料</a></p>