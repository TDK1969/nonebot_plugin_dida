import json
import requests
from typing import List, Tuple, Dict
from nonebot import get_driver, logger, require
from .config import Config
from datetime import datetime, timedelta
from random import sample
import os
from os.path import abspath, dirname
global_config = get_driver().config
config = Config.parse_obj(global_config)

class DidaAPI():
    def __init__(self) -> None:
        self.getProjects = "https://api.dida365.com/api/v2/projects"
        """
        获取所有的清单
        方法: GET
        """

        self.createTask = "https://api.dida365.com/api/v2/batch/task"
        """
        创建任务
        方法: POST
        """

        self.getHabits = "https://api.dida365.com/api/v2/habits"
        """
        获取所有的习惯
        方法: GET
        """

        self.getUTCTimetable = "https://api.dida365.com/api/v1/course/timetable"
        """
        获取所有的时间表
        方法: GET
        """

        self.getColumns = "https://api.dida365.com/api/v2/column?from=0"
        """
        获取所有的分组
        方法: GET
        """

        self.getCompleteTasks = "https://api.dida365.com/api/v2/project/{}/completed/?from={}&to={}&limit={}"
        """
        获取指定清单下指定时间段内的已完成任务
        参数:
        清单ID(all可返回所有)，开始时间，截止时间，返回最大数量
        方法: GET
        """

        self.createHabit = "https://api.dida365.com/api/v2/habits/batch"
        """
        创建新的打卡
        方法: POST  
        """

        self.createSubTask = "https://api.dida365.com/api/v2/batch/taskParent"
        """
        创建子任务时需要使用
        方法: POST
        """

        self.getColumnsInProject = "https://api.dida365.com/api/v2/column/project/{}"
        """
        获取特定清单中的分组
        方法: GET
        """

        self.getAllInfo = "https://api.dida365.com/api/v2/batch/check/0"
        """
        获取未完成任务
        方法: GET
        
        """

        self.login = "https://api.dida365.com/api/v2/user/signon?wc=true&remember=true"
        """
        登录滴答清单
        方法: POST
        """

class DidaList(object):
    def __init__(self) -> None:
        # 对config进行检测
        if not hasattr(config, "dida_phone"):
            raise AttributeError("nonebot_plugin_dida缺少配置项: dida_phone")
        if not hasattr(config, "dida_password"):
            raise AttributeError("nonebot_plugin_dida缺少配置项: dida_password")
        
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv2.0.1) Gecko/20100101 Firefox/4.0.1',
            "authority": 'api.dida365.com',
            'referer': 'https://dida365.com/webapp/',
            'origin': 'https://dida365.com',
            'x-device': json.dumps({"platform":"web","os":"Windows 10","device":"Chrome 86.0.4240.198","name":"","version":4130,"id":'6732f9fd4557ba2ce15c00eb',"channel":"website","campaign":"","websocket":""})
        }
        self.__API = DidaAPI()
        rootPath = dirname((abspath(__file__)))
        self.__didaCookie = rootPath + "/cookie.json"
        self.__didaTaskTemplatePath = rootPath + "/file/template/task.json"
        self.__didaUdpateTaskTemplatePath = rootPath + "/file/template/updateTask.json"
        
        listPath = "./src/plugins/nonebot_plugin_dida"
        if not os.path.exists(listPath):
            os.makedirs(listPath)
        self.__projectsIDPath = listPath + "/projectsID.json"
        self.__columnIDPath = listPath + "/columnsID.json"
        self.__taskIDPath = listPath + "/taskID.json"
        
        if not os.path.exists(self.__didaCookie):
            self.updateCookie()
        else:
            with open(self.__didaCookie, 'r') as f:
                cookie = json.load(f)
                self.headers["cookie"] = cookie
        
    
    def updateCookie(self):
        '''登录以获取cookie

        Returns:
            无
        '''
        loginPayload = {
            "password": config.dida_password,
            "phone": config.dida_phone
        }

        res = requests.post(
            url=self.__API.login,
            headers=self.headers,
            json=loginPayload
        )

        assert res.status_code == 200, f"滴答清单登录失败: {res.content}"
        logger.debug(f'登陆成功, {res.content}')
        
        cookies = res.cookies
        cookie = ''
        for name, value in cookies.items():
            cookie += f'{name}={value};'
        
        logger.debug(f"cookie更新成功，cookie为{cookie}")
        self.headers["cookie"] = cookie
        with open(self.__didaCookie, "w+") as f:
            json.dump(cookie, f)
        
    
    def __getUTCTime(self, t:datetime=datetime.now()) -> str:
        '''生成滴答清单使用的utc格式化时间字符串

        Args:
            t (datetime, optional): datetime类的时间. Defaults to datetime.now().

        Returns:
            str: 格式化时间字符串
        '''
        
        template="%Y-%m-%dT%H:%M:%S.000+0000"
        utc_time = t - timedelta(hours=8) 
        utc_time = utc_time.strftime(template)
        return utc_time

    def __getTimeFromTimeStamp(self, timestamp: int) -> str:
        '''根据时间戳生成utc时间字符串

        Args:
            timestamp (int): 时间戳

        Returns:
            str: 时间字符串
        '''
        template = "%Y-%m-%dT%H:%M:%S.000+0000"
        targetTime = datetime.fromtimestamp(timestamp)

        utc_time = targetTime - timedelta(hours=8) 
        utc_time = utc_time.strftime(template)
        return utc_time
    
    def __generateID(self, num=24) -> str:
        '''生成一个滴答清单的id

        Args:
            num (int, optional): id位数. Defaults to 24.

        Returns:
            str: 生成的id
        '''
        
        H = 'abcdef0123456789'*3
        id = "".join(sample(H,num))
        return id
    
    def createTask(
        self, 
        title: str,
        projectId: str="",
        parentId: str="",
        columnId: str="",
        tags: List=[],
        priority: int=0,
        startDate: datetime=None,
        dueDate: datetime=None,
        content: str=""
    ) -> Tuple[bool, str]:
        
        '''根据参数创建任务

        Args:
            title (str): 任务名
            projectId (str): 所属的清单ID. Defaults to "".
            parentId (str, optional): 母任务ID. Defaults to "".
            columnId (str, optional): 分组ID. Defaults to "".
            tags (List, optional): 标签. Defaults to [].
            priority (int, optional): 优先级. Defaults to 0.
            startDate (datetime, optional): 开始时间. Defaults to None.
            dueDate (datetime, optional): 结束时间. Defaults to None.
            conetent (str. optional): 描述. Defaults to "".
        Return:
            [isSuccess, msg]
        '''
        task = json.load(open(self.__didaTaskTemplatePath, 'r'))
        payload = json.load(open(self.__didaUdpateTaskTemplatePath, 'r'))
        timeStr = self.__getUTCTime()
        
        task['title'] = title
        task['projectId'] = projectId
        task['parentId'] = parentId
        task['columnId'] = columnId
        task['tags'] = tags
        task['priority'] = priority
        task['startDate'] = None if not startDate else self.__getUTCTime(startDate)
        task['dueDate'] = None if not dueDate else self.__getUTCTime(dueDate)
        task['id'] = self.__generateID()
        task['createdTime'] = timeStr
        task['modifiedTime'] = timeStr
        task['content'] = content

        payload['add'].append(task)

        res: requests.Response = requests.post(
            url=self.__API.createTask,
            headers=self.headers,
            json=payload
        )
        
        if res.status_code == 200:
            if parentId:
                isSuccess, msg = self.__createSubTask(parentId, projectId, task['id'])
                if not isSuccess:
                    return (False, msg)
            return (True, f"create task successfully: {res.content}" )
        else:
            return (False, f"create task failed: {res.content}" )

    def __createSubTask(self, parentId: str, projectId: str, taskId: str) -> Tuple[bool, str]:
        '''当创建子任务时需要执行的函数

        Args:
            parentId (str): 母任务ID
            projectId (str): 所属清单ID
            taskId (str): 子任务ID

        Returns:
            Tuple[bool, str]: 返回一个元组，第一为是否成功，第二个为信息
        '''
        payload = [
            {
            "parentId": parentId,
            "projectId": projectId,
            "taskId": taskId
            }
        ]

        res:requests.Response = requests.post(
            url=self.__API.createSubTask,
            headers=self.headers,
            json=payload
        )

        if res.status_code == 200:
            return (True, "create subtask successfully: {res.content}")
        else:
            return (False, f"create subtask failed: {res.content}")

    def getFilterTask(
        self,
        title: str = None,
        projectId: str = None,
        parentId: str = None,
        columnId: str = None,
        tags: List = None,
        priority: int = None,
        startDate: datetime = None,
        dueDate: datetime = None
    ) -> List:
        '''根据设置的过滤条件，返回符合条件的任务

        Args:
            title (str, optional): 任务名. Defaults to None.
            projectId (str, optional): 清单Id. Defaults to None.
            parentId (str, optional): 母任务Id. Defaults to None.
            columnId (str, optional): 分组Id. Defaults to None.
            tags (List, optional): 标签. Defaults to None.
            priority (int, optional): 优先级. Defaults to None.
            startDate (datetime, optional): 开始日期. Defaults to None.
            dueDate (datetime, optional): 结束日期. Defaults to None.

        Returns:
            List: 符合条件的任务
        '''

        def filterFunc(
            task: Dict,
            title: str = title,
            projectId: str = projectId,
            parentId: str = parentId,
            columnId: str = columnId,
            tags: List = tags,
            priority: int = priority,
            startDate: datetime = startDate,
            dueDate: datetime = dueDate
        ) -> bool:
            '''根据过滤条件判断该任务是否符合条件

            Args:
                task (Dict): 任务
                title (str, optional): 任务名. Defaults to None.
                projectId (str, optional): 清单Id. Defaults to None.
                parentId (str, optional): 母任务Id. Defaults to None.
                columnId (str, optional): 分组Id. Defaults to None.
                tags (List, optional): 标签. Defaults to None.
                priority (int, optional): 优先级. Defaults to None.
                startDate (datetime, optional): 开始日记. Defaults to None.
                dueDate (datetime, optional): 结束日期. Defaults to None.

            Returns:
                bool: 任务是否符合条件
            '''
            
            if title is not None:
                if task["title"] != title:
                    return False
            
            if projectId is not None:
                if task["projectId"] != projectId:
                    return False
            
            if parentId is not None:
                if "parentId" not in task or task["parentId"] != parentId:
                    return False
            
            if columnId is not None:
                if "columnId" not in task or task["columnId"] != columnId:
                    return False
            
            if tags is not None:
                if "tags" not in task or set(task["tags"]) & set(tags) == set(tags):
                    return False

            if priority is not None:
                if task["priority"] != priority:
                    return False
            
            if startDate is not None and dueDate is not None:
                if "startDate" in task and "dueDate" in task:
                    taskStartDate = datetime.strptime(task["startDate"], "%Y-%m-%dT%H:%M:%S.000+0000")
                    taskStartDate += timedelta(hours=8)
                    taskDueDate = datetime.strptime(task["dueDate"], "%Y-%m-%dT%H:%M:%S.000+0000")
                    taskDueDate += timedelta(hours=8)

                    if not startDate <= taskStartDate <= taskDueDate <= dueDate:
                        return False
                else:
                    return False

            elif startDate is not None:
                if "startDate" in task:
                    taskDatetime = datetime.strptime(task["startDate"], "%Y-%m-%dT%H:%M:%S.000+0000")
                    taskDatetime += timedelta(hours=8)
                    if taskDatetime.date() != startDate.date():
                        return False
                else:
                    return False
            
            elif dueDate is not None:
                if "dueDate" in task:
                    taskDatetime = datetime.strptime(task["dueDate"], "%Y-%m-%dT%H:%M:%S.000+0000")
                    taskDatetime += timedelta(hours=8)
                    if taskDatetime.date() != dueDate.date():
                        return False
                else:
                    return False

            return True

        res = requests.get(
            url=self.__API.getAllInfo,
            headers=self.headers
        )

        tasks = res.json()["syncTaskBean"]["update"]
        ans = []
        
        for task in tasks:
            if filterFunc(task):
                ans.append(task)
        
        return ans
    
    def getProjects(self) -> List[Dict]:
        '''获取所有的清单

        Returns:
            List[Dict]: 清单列表
        '''

        res = requests.get(
            url=self.__API.getProjects,
            headers=self.headers
        )

        projects = res.json()

        return projects

    def getColumns(self, projectId:str=None) -> List[Dict]:
        '''获取分组，可指定特定清单下的分组，无指定则获取全部分组

        Args:
            projectId (str, optional): 指定的清单id. Defaults to None.

        Returns:
            List[Dict]: 分组列表
        '''

        res = requests.get(
            url=self.__API.getColumns,
            headers=self.headers
        )

        columns = res.json()["update"]

        if projectId is not None:
            ans = []
            for column in columns:
                if column["projectId"] == projectId:
                    ans.append(column)
            
            return ans
        
        return columns

    def getHabits(self) -> List[Dict]:
        '''获取所有的习惯

        Returns:
            List[Dict]: 习惯列表
        '''

        res = requests.get(
            url=self.__API.getHabits,
            headers=self.headers
        )

        return res.json()
    
    def getCompletedTasks(self, projects: List[str] = None, startTime: datetime = None, endTime: datetime = None, limit: int = 50) -> List[Dict]:
        '''获取已完成的任务

        Args:
            projects (List[str]): 指定清单列表的清单Id，可指定多个
            startTime (str): 开始时间
            endTime (str): 结束时间
            limit (int): 数量限制

        Returns:
            List[Dict]: 任务列表
        '''
        if projects is not None:
            projects = ','.join(projects)
        else:
            projects = "all"
        
        if startTime is not None:
            startTime = startTime.strftime("%Y-%m-%d") + "%20" + startTime.strftime("%H:%M:%S")
        else:
            startTime = ""
        
        if endTime is not None:
            endTime = endTime.strftime("%Y-%m-%d") + "%20" + endTime.strftime("%H:%M:%S")
        else:
            endTime = ""

        res = requests.get(
            url=self.__API.getCompleteTasks.format(projects, startTime, endTime, limit),
            headers=self.headers
        )

        tasks = res.json()

        return tasks
    
    def genProjectIDJson(self):
        '''
        将清单的ID输出到json文件中
        '''
        
        projects = self.getProjects()
        with open(self.__projectsIDPath, "w+") as f:
            json.dump(projects, f, ensure_ascii=False, indent=4)
    
    def genColumnIDJson(self):
        '''
        将分组的ID输出到json文件中
        '''
        
        columns = self.getColumns()
        with open(self.__columnIDPath, "w+") as f:
            json.dump(columns, f, ensure_ascii=False, indent=4)
    
    def genTaskIDJson(self):
        '''
        将未完成任务的ID输出到json文件中
        '''
        
        tasks = self.getFilterTask()
        with open(self.__taskIDPath, "w+") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=4)
        
dida = DidaList()

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

scheduler.add_job(dida.updateCookie, "cron", day_of_week=6, hour=0, minute=0, second=0, misfire_grace_time=75)
if config.dida_genid:
    
    logger.debug(f'[滴答清单]将生成ID文件')
    
    scheduler.add_job(dida.genProjectIDJson, "interval", minutes=1, misfire_grace_time=45)
    scheduler.add_job(dida.genColumnIDJson, "interval", minutes=1, misfire_grace_time=45)
    scheduler.add_job(dida.genTaskIDJson, "interval", minutes=1, misfire_grace_time=45)


