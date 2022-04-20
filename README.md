<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# nonebot-plugin-dida

✅ _NoneBot 滴答清单插件_ ✅
<p>version: 1.0.0</p>
    
</div>

# 简介
基于[Nonebot2](https://github.com/nonebot/nonebot2)的滴答清单插件，可通过本插件创建任务、子任务、查询任务

**已支持v2.0.0-beta.2**
## 依赖
- 适配器: onebot v11
- 插件:
    - [nonebot_plugin_apscheduler](https://pypi.org/project/nonebot-plugin-apscheduler/)

# 近期更新
[完整日志](https://github.com/TDK1969/nonebot_plugin_dida/blob/main/file/source/changelog.md)
- **v 1.0.0**
```
正在准备1.0发布
```

# 配置项
配置方式：在 NoneBot 全局配置文件中添加以下配置项
## dida_phone
- 类型: `str`
- 说明: 滴答清单绑定的手机号(目前仅支持通过手机号登录)

## dida_password
- 类型: `str`
- 说明: 滴答清单账号的密码

## dida_genIDJson
- 类型: `bool`
- 默认值: True
- 说明: 是否生成记录清单/分组/任务的Json文件。将该项置为True，自动每分钟获取清单/分组/任务的详细内容，并保存到机器人工作目录下`/src/plugins/nonebot_plugin_dida`的json文件中，可通过文件获取清单/分组/任务的ID。在不需要的时候可置为False。

    清单 —— `projectID.json`

    分组 —— `columnID.json`

    任务 —— `taskID.json`

    各文件中的字段，详见[project.md](https://github.com/TDK1969/nonebot_plugin_dida/blob/main/file/source/project.md), [column.md](https://github.com/TDK1969/nonebot_plugin_dida/blob/main/file/source/column.md), [task.md](https://github.com/TDK1969/nonebot_plugin_dida/blob/main/file/source/task.md)

# 安装方式
通过nb plugin安装（推荐）

- `nb plugin install nonebot-plugin-dida`

# 使用方式
## 导入dida
在你的插件中使用export导入实例dida，通过dida进行操作

`dida = require("nonebot_plugin_dida").dida`

## 创建任务
`dida.createTask()` - 根据传递的参数创建任务
### 参数
|参数名 |数据类型 | 默认值 | 说明|
|:---   |:------ | :------ | :---|
| title|str |- | 任务名 |
| projectId| str | "" | 任务所属的清单的ID (ID不存在则放到收集箱) |
| parentId| str | "" | 母任务的ID（ID不存在则无作用） |
|columnId | str| "" | 任务所属的分组的ID（ID不存在则放到第一个分组 ；若清单不存在分组则无作用） |
|tags |List[str] |[] |任务的标签（如果标签不存在则自动创建） |
| priority| int|0 | 任务的优先级(0-无优先级，1-低优先级，3-中优先级，5-高优先级)|
|startDate |datetime |None |任务开始日期 |
|dueDate | datetime|None | 设置时间段时的结束日期|
| content| str| ""| 任务的描述（不支持checkbox，支持markdown语法） |

### 返回值
返回一个元组——（isSuccess, msg）
| 字段名 |类型 | 说明 |
|:----|:----|:----|
|isSuccess |bool | 创建任务是否成功|
|msg |str | 成功/失败的描述信息|

## 查询任务
`dida.getFilterTask()` - 将参数作为过滤条件，查询未完成的任务；无参数则返回所有任务
### 参数
|参数名 |数据类型 | 默认值 | 说明|
|:---   |:------ | :------ | :---|
| title| str|None | 任务名|
|projectId |str| None| 任务所属的清单ID|
| parentId| str| None| 任务的母任务ID|
|columnId |str | None| 任务所属的分组ID|
| tags| List[str]| None| 任务的标签|
|priority | int|None |任务的优先级(0-无优先级，1-低优先级，3-中优先级，5-高优先级) |
|startDate | datetime|None |任务的开始日期 |
| dueDate| datetime|None | 任务的结束日期|
注：
- 仅指定startDate时，返回与startDate相同开始日期的任务
- 仅指定dueDate时，返回与dueDate相同结束日期的任务
- 同时指定startDate和dueDate时，返回startDate-dueDate之间的任务

### 返回值
返回一个列表，其中每个元素是一个任务的字典，见[task.md](https://github.com/TDK1969/nonebot_plugin_dida/blob/main/file/source/task.md) 

