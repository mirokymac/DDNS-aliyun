# DDNS-aliyun<br>
  Just a project for practice~
  A script that uses only native python to make your Aliyun-DNS updated.
  For those who don't like ali-sdk (or a lazy man like me).
 
# 动态更新 阿里云DNS 解释条目
## 功能介绍
  自动获取本地的ip地址，并更新到阿里云DNS对应的域名解释条目中。
  如果你的设备拥有**动态公网IP**，同时想通过**自己的一级域名**进行接入的话，可以使用这个脚本。

## 使用方法  
  1，安装python2.7<br>
  2，在阿里云平台申请**“AccessKey”**，在*控制台-你的账号名-AcessKey*下。<br>
  3，将申请到的*Acesskey*分别填入*ID*和*Secret*。<br>
  4，在脚本中，将**DomanName**更改为要更换的域名。若有**RequestID**，可以填入；否则程序会自动获取RequesID（**暂时只支持顶级域名和一级域名**）。<br>
  5，使用脚本。<br>
  ```
  python ddns-aliyun.py
  ```  
  
## 参考内容  
  X-Mars： https://github.com/X-Mars/UpgradeDNS<br>
  小马： https://www.xiaomastack.com/2015/10/21/alipushcdn/<br>
  阿里云官方API<br>
