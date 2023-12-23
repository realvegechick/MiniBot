import os
import json
import uiautomator2 as u2
import time
import xml.dom.minidom
from state import *
import re
import logging
import subprocess
from utils.fridaUtils import *
from utils.xmlUtils import *
from utils.logCreator import *
from path import *
import simhash
from PIL import *
import traceback
import sys
from custom_handlers import *
from dispatcher import *

class StrategyManager:
    # conf用于记录传入的参数，包括需要的小程序的基本参数 
    # 需要一个DeviceManager的实例
    # 需要一个StateManager的实例
    def __init__(self,conf,state_manager,device_manager):
        # 配置文件
        self.superapp=conf["superapp"]
        self.wait=conf["wait"]
        self.conf = conf
        # 日志
        self.logger=log_creator("StrategyManager")


        self.state_manager = state_manager
        self.device_manager = device_manager
        self.reset()
        

    def reset(self):
        self.dfsStack = []
        self.last_Action = None
        


    def get_Action(self,Current_STATE):
        if Current_STATE["Crash_Flag"] == True:
            Exception_Type = Exception_dispatcher(self.last_Action,self.dfsStack[-1],Current_STATE) 
            record_info = Exception_Handlers[Exception_Type](self.device_manager,self.state_manager,self.dfsStack)
        else:
            Normal_Type = Normal_dispatcher(self.last_Action,self.dfsStack[-1],Current_STATE,self.device_manager,self.state_manager,self.dfsStack) 
            record_info = Normal_Handlers[Normal_Type](self.last_Action, self.dfsStack[-1], Current_STATE,self.device_manager,self.state_manager)
        if (not record_info == None):
            if ("dfs_pop" in record_info and record_info["dfs_pop"]):
                self.dfsStack.pop()
            if ("dfs_append" in record_info and record_info["dfs_append"]):
                self.dfsStack.append(record_info["dfs_append_state"])
                self.dfsStack[-1].hash = get_sim_hash(get_miniapp_hierarchy(self.device_manager,self.dfsStack))
                
            if ("state_manager_update" in record_info and record_info["state_manager_update"]):
                self.state_manager.update(record_info)
            # 跳转至某一状态
            if ("Jump" in record_info and record_info["Jump"]):
                Jump(Current_STATE,record_info["target_State"],self.device_manager,self.state_manager,self.dfsStack)
            # dfs状态回退
            if ("Back" in record_info and record_info["Back"]):
                flag = Back(self.device_manager,self.state_manager,self.dfsStack)
                if not flag:
                    return None
        Before_Next_Action(self.device_manager,self.state_manager,self.dfsStack)
        self.last_Action = Get_Next_Action["DFS"](self.device_manager,self.state_manager,self.dfsStack,self.conf)
        
        print("---------------------last_Action--------------")
        print(self.last_Action)
        
        return self.last_Action

if __name__ == "__main__":
    pass