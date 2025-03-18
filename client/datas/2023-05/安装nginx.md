# Nginx



## 反向代理、负载均衡

![反向代理](/Users/fei/Documents/安装nginx.assets/反向代理.png)



## Windows下安装Nginx

- 直接下载运行

  ```python
  """
  https://nginx.org/download/nginx-1.24.0.zip
  """
  ```



## MacOS下安装Nginx

- 安装 Homebrew（安装过程需要输密码，按回车确认）

  ```shell
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"	# 官方源
  
  /bin/bash -c "$(curl -fsSL https://gitee.com/ineo6/homebrew-install/raw/master/install.sh)"	# 国内源
  
  # 安装完成之后重启终端
  ```

- 安装 Nginx

  ```shell
  brew install nginx
  ```

  

## Linux下安装Nginx（CentOS为例）

#### 方法一（命令安装，不会编译第三方模块）

```shell
yum install nginx -y
```



#### 方法二（编译安装，可以自定义把第三方模块编译进去）

- 安装依赖

  ```shell
  yum -y install gcc gcc-c++ make libtool zlib zlib-devel openssl openssl-devel pcre pcre-devel
  ```

  

- 安装

  ```shell
  # 下载
  wget https://nginx.org/download/nginx-1.24.0.tar.gz
  
  # 解压
  tar -zxvf nginx-1.24.0.tar.gz
  # -zxvf：z表示解压缩时使用gzip算法，x表示解压缩，v表示显示详细信息，f表示后面紧跟着要解压缩的文件名
  
  # 进入解压文件夹
  cd nginx-1.24.0
  
  # 配置编译项（可以配置编译那些模块进去，暂时用不到，不做介绍）
  ./configure
  
  # 编译并安装
  make && make install
  
  # 查看安装路径
  whereis nginx
  >>>/usr/local/nginx/
  
  # 建立软连接（/usr/local/bin/这个路径下的文件，可以直接执行，因为这个文件夹在环境变量里面，软连接类似windows的快捷方式，把它加入这个目录之后，就可以不用配置环境变量了）
  ln -s /usr/local/nginx/sbin/nginx /usr/local/bin/nginx
  
  # 启动nginx
  nginx
  
  ```

  

## Nginx常用命令

```shell
1. 启动Nginx：  nginx
2. 停止Nginx：  nginx -s stop
3. 重新加载配置文件：  nginx -s reload
4. 测试配置文件是否正确：  nginx -t
5. 查看Nginx进程： ps -ef | grep nginx
6. 查看Nginx版本号： nginx -v
7. 查看Nginx帮助信息： nginx -h
8. 查看Nginx配置文件位置： nginx -V
9. 查看端口号对应的进程：  lsof -i:80 （查看80端口对应的进程）
```



## 基础配置

```python
"""
# tcp反向代理
stream {
		
		# 负载均衡配置
    upstream chat_server{
        server 127.0.0.1:9001 weight=1;
        server 127.0.0.1:9002 weight=1;
        server 127.0.0.1:9003 weight=1;
        server 127.0.0.1:9004 weight=1;
        server 127.0.0.1:9005 weight=1;
        server 127.0.0.1:9006 weight=1;
        server 127.0.0.1:9007 weight=1;
        server 127.0.0.1:9008 weight=1;
        server 127.0.0.1:9009 weight=1;
        server 127.0.0.1:9010 weight=1;
    }
  	
    server {
        listen 9000;
        proxy_pass chat_server;
    }
}
"""


"""	
# 挂载文件夹
server {
    listen 80;
    server_name example.com;

    location /updates/ {
        alias /path/to/updates/;
        autoindex on;
    }
}
"""
```





