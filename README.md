<div align="center">
<h1 align="center">
Isearch_AutoLottery
</h1>

[![GitHub stars](https://img.shields.io/github/stars/sunsikai/Isearch_AutoLottery?style=flat-square)](https://github.com/JunzhouLiu/BILIBILI-HELPER/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/sunsikai/Isearch_AutoLottery?style=flat-square)](https://github.com/JunzhouLiu/BILIBILI-HELPER/network)
[![GitHub issues](https://img.shields.io/github/issues/sunsikai/Isearch_AutoLottery?style=flat-square)](https://github.com/JunzhouLiu/BILIBILI-HELPER/issues)
[![GitHub license](https://img.shields.io/github/license/sunsikai/Isearch_AutoLottery?style=flat-square)](https://github.com/JunzhouLiu/BILIBILI-HELPER/blob/main/LICENSE) 


</div>

## 工具简介

这是一个利用 GitHub Action 等方式实现艺赛旗设计器，每日自动进行签到抽奖\~\~\~\~

**如果觉得好用，顺手点个 Star 吧 ❤**

**仓库地址：[sunsikai/Isearch_AutoLottery][1]**

**请不要滥用相关API，让我们一起爱护艺赛旗RPA ❤**

## 功能列表
### 已实现
* [x] 每天上午 8 点 10 分自动开始任务。*【运行时间可自定义】*
* [x] 登录设计器，进行签到。*【如果签到，则跳过】*
* [x] 获取可抽奖次数，自动进行抽奖。
* [x] 每日进行自动发帖、删帖，延长设计器使用。
* [x] 通过server酱推送执行结果到微信。
	  

## 使用说明

### 一、Actions 方式

1. **Fork 本项目**
2. **点击项目 Settings -\> Secrets -\> New Secrets 添加以下 3 个 Secrets，其中server酱微信推送的sckey可参阅后面设置**

| Name          | Value               |
| ------------- | ------------------- |
| USERNAME      | 用户名              |
| PASSWORD      | 密码                |
| SERVERPUSHKEY | server酱推送的sckey（用于微信通知，没配置则不微信通知）|


![图示][image-1]




3. **修改每日任务执行的时间**

修改 `.github/workflows/auto_lottery_Isearch.yml`，在第 8 行左右位置找到下如下配置。

```yml
  schedule:
    - cron: '0 20 * * *'
    # cron表达式，Actions时区是UTC时间，这里是UTC时区每天20点0分运行，即UTF时区每天4点0分运行（实测会快8个多小时，无法精确到分）
    # 不懂cron表达式的，可以进网站[https://crontab.guru/](https://crontab.guru/)看下
```
**这里强烈建议大家自己实际情况修改下，不然大家的程序每天都同个时间点去签到，那也太。。。。**



4. **手动触发 workflow 运行(测试是否可正常运行)**

**Github Actions 默认处于关闭状态，还大家请手动开启 Actions ，执行一次工作流，验证是否可以正常工作。**
![图示][image-2]


5. **流程运行情况查看**
![图示][image-3]
![图示][image-4]

本工具的 Actions 自动构建配置了缓存，平均运行时间在 25s 左右。


**请各位使用 Actions 时务必遵守Github条款。不要滥用Actions服务。同时，请遵循艺赛旗社区约定，更不要通过本流程 api对社区进行大量发帖以获取Y币，小心账号被封的。（这些后台可以看到数据的，人家能容忍用户水帖来延迟设计器使用已经是很大气的表现了，请大家不要去无底线挑战人家底线。如因大量水贴导致账户被封，完全是自己作死）**

**Please be sure to abide by the Github terms when using Actions. Do not abuse the Actions service.**

## 订阅执行结果
### Server酱Turbo版

目前Turbo版本的消息通道支持以下渠道

- 自定义微信测试号
- 方糖服务号

1. 前往 [sct.ftqq.com](https://sct.ftqq.com/sendkey)点击登入，创建账号。
2. 点击点[SendKey](https://sct.ftqq.com/sendkey) ，生成一个 Key。将其增加到 Github Secrets 中，变量名为 `SERVERPUSHKEY`
3. [配置消息通道](https://sct.ftqq.com/forward) ，选择方糖服务号，保存即可。
4. 推送效果展示
   ![图示][image-5]

**旧版推送渠道[sc.ftqq.com](http://sc.ftqq.com/9.version)即将与4月底下线，请前往[sct.ftqq.com](https://sct.ftqq.com/sendkey)生成`Turbo`版本的`Key`，注意，申请Turbo版Key后请配置消息通道，如果想沿用以前的推送方式，选择方糖服务号即可**

## 免责声明

1. 本工具不会记录你的任何敏感信息，也不会上传到任何服务器上。（例如用户的用户名密码数据均存在Actions Secrets中或者用户自己的设备上）
2. 本工具不会记录任何执行过程中来自艺赛旗的数据信息，也不会上传到任何服务器上。。
3. 本工具执行过程中产生的日志，仅会在使用者自行配置推送渠道后进行推送。日志中不包含任何用户敏感信息。
4. 如果有人修改了本项目（或者直接使用本项目）盈利恰饭，那和我肯定没关系，我开源的目的单纯是技术分享。
5. 如果你使用了第三方修改的，打包的本工具代码，那你可得注意了，指不定人就把你的数据上传到他自己的服务器了，这可和我没关系。（**网络安全教育普及任重而道远**）
6. 本工具源码仅在sunsikai/Isearch_AutoLottery开源，其余的地方的代码均不是我提交的，可能是抄我的，借鉴我的，但绝对不是我发布的，出问题和我也没关系。 
7. 我开源本工具的代码仅仅是技术分享，没有任何丝毫的盈利赚钱目的，如果你非要给我打赏/充电，那我就是网络乞丐，咱们不构成任何雇佣，购买关系的交易。
8. 本项目不会增加类似于死循环发帖来获取Y币，开发这个应用的目的是单纯的技术分享。下游分支开发者/使用者也请不要滥用相关功能。
9. 本项目欢迎其他开发者参与贡献，基于本工具的二次开发，使用其他语言重写都没有什么问题，能在技术上给你带来帮助和收获就很好.
10. 本项目遵守MIT License ，请各位知悉。。。



[1]:	https://github.com/sunsikai/Isearch_AutoLottery

[image-1]:	docs/IMG/配置用户名密码.png
[image-2]:	docs/IMG/手动触发流程.png
[image-3]:	docs/IMG/查看执行情况1.png
[image-4]:	docs/IMG/查看执行情况2.png
[image-5]:	docs/IMG/server酱推送效果.png
