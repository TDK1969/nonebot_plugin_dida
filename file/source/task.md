# 任务字典字段
| 字段名 |类型 | 说明 |
|:----|:----|:----|
|id | str | 任务的ID|
|projectId |str | 任务所属清单的ID|
| title| str | 任务名| 
|content |str |任务的内容 | 
| startDate| str |任务开始时间（UTC时间）| 
|dueDate | str| 任务结束时间（UTC时间）|
| timeZone| str| 时区 | 
|priority |int | 优先级(0-无优先级，1-低优先级，3-中优先级，5-高优先级) | 
| createdTime|str |任务创建时间（UTC时间） | 
|modifiedTime | str | 任务修改时间（UTC时间） | 
| creator| int| 任务创建者的ID |
|tags |List[str] |任务的标签 |
| attachments| List[Dict]| 任务的附件|
| isAllDay|bool | 是否是全天任务（无安排时间则为True）|
| items| List| 检查事项列表|
| kind| str|表示任务内容是纯文字还是检查事项（"TEXT" - 纯文字；"CHECKLIST" - 检查事项） |
|childIds | List[str]| 子任务ID列表|
| etag| str| 另一种唯一标识|

注：
- 未出现的字段暂时作用未知