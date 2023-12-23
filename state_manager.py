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
from custom_utils import *


class StateManager:
    # conf用于记录传入的参数，包括需要的小程序的基本参数 
    def __init__(self,conf,device_manager):
        # 配置文件
        self.superapp=conf["superapp"]
        self.wait=conf["wait"]
        self.package = conf["package"]
        # 日志
        self.logger=log_creator("StateManager")
        self.device_manager = device_manager
        #self.reset()
        
    # 初始化
    def reset(self):
        # 初始化
        self.crash_flag = False
        self.crash_info = ""
        self.stateList=[]
        self.statePath=[]
        self.statePre=[]
        self.current_State = None
        self.appid = ""
        self.activity = ""
        self.section = 0
        self.allStatePagepathList = []
        self.first_dif_page_path = []
        self.total_time = 0

    def get_Current_STATE(self):
        self.current_State = self.device_manager.get_current_State()
        self.current_State.section = self.section
        self.current_activity = self.device_manager.get_activity()
        self.Crash_Flag = False
        self.Crash_type = ""
        # 获取正确的xml文件
        self.base_xml = self.device_manager.get_base_xml()
        has_superapp_package = False
        # print(self.base_xml)
        # print(type(self.base_xml))
        for node in self.base_xml.childNodes:
            # print(node)
            # print(type(node))
            # input()
            if(not isinstance(node,xml.dom.minidom.Text) and node.getAttribute("package")==self.package[self.superapp]):
                has_superapp_package = True
                break
        if has_superapp_package == False:
            self.base_xml = self.device_manager.get_base_xml(True)
        
        if self.current_activity != self.activity:
            self.logger.info("进入错误activity："+self.current_activity)
            self.Crash_Flag = True
            self.Crash_type = "OutOfMiniApp"
        if self.current_State.app_id != self.appid:
            self.logger.info("进入其他小程序")
            self.Crash_Flag = True
            self.Crash_type = "InOtherApp"
        if self.current_State.current_url!='':
            self.logger.info("进入html网页")
            self.Crash_Flag = True
            self.Crash_type = "InOtherHtml"


        return {
            "appid" : self.appid,
            "activity" : self.activity,
            "current_activity" : self.current_activity,
            "Crash_Flag" : self.Crash_Flag,
            "Crash_Type" : self.Crash_type,
            "current_State" : self.current_State,
            "base_xml" : self.base_xml
        }
 
    def set_appid(self,appid):
        self.appid = appid
    
    def set_activity(self,activity):
        self.activity = activity
    
    # 跳转至某一特定state
    def jump_to_State(self,target):
        if isinstance(target,State):
            target_State = target
            self.logger.info("直接跳转:"+str(target_State.page_path))
            # 把当前小程序关掉
            if(self.device_manager.get_activity()==self.activity and self.superapp=="wechat"):
                self.device_manager.exit_miniapp()
            time.sleep(1*self.wait)
            self.device_manager.frida.jump(self.appid,target_State.page_path)
            time.sleep(1*self.wait)
            if self.device_manager.get_current_State() == target_State:
                self.logger.info("跳转成功")
                return True
            else:
                self.logger.info("跳转失败")
                return  False
        else:
            target_path = target
            self.logger.info("直接跳转:"+target_path)
            # 把当前小程序关掉
            if(self.device_manager.get_activity()==self.activity and self.superapp=="wechat"):
                self.device_manager.exit_miniapp()
            time.sleep(1*self.wait)
            self.device_manager.frida.jump(self.appid,target_path)
            time.sleep(1*self.wait)
            current_State = self.device_manager.get_current_State()
            if  current_State.page_path == target_path:
                self.logger.info("跳转成功")
                return True
            else:
                self.logger.info("跳转失败")
                return  False
    
    # 从头跳转至某一特定的state
    # def from_root_switch_to_State(self,target_State):
    #     tmp_target_State = copy.deepcopy(target_State)
    #     self.logger.info("开始从头跳转:"+str(target_State))
    #     if(self.device_manager.get_activity()==self.activity):
    #         self.device_manager.exit_miniapp()
    #     # 跳到当前状态
    #     self.device_manager.frida.jump(self.appid)

    #     # 用于记录从头点到这儿的路径
    #     path_list=[]
    #     statePre=self.statePre
    #     stateList=self.stateList
    #     while (statePre[stateList.index(target_State)] != None):
    #         path_tmp =statePre[stateList.index(target_State)]
    #         path_list.append(path_tmp)
    #         target_State=path_tmp.start_State
    #     path_list.reverse()
        
    #     tmp_section = 0
    #     for path in path_list:
    #         if (path.trigger == TriggerType.Click):
    #             x,y=get_center(path.bound)
    #             self.logger.info("点击记录:"+str([x,y]))
    #             self.device.click(x,y)
    #             tmp_section = 0
    #         elif (path.trigger == TriggerType.Scroll):
    #             x1,y1,x2,y2=get_box(path.bound)
    #             self.logger.info("滑动记录:"+str([x,y]))
    #             self.device.drag(x2-50,y2-50,x1,y1,duration=1)
    #             tmp_section = tmp_section + 1
    #         time.sleep(2*self.wait)
    #         if(path.crash_type!=StateType.Normal):
    #             self.call_system_back(path.end_State)
    #         next_State=self.device_manager.get_current_State()
    #         next_State.section = tmp_section
    #         self.logger.info("已跳转至:"+str(next_State))
    #         if (next_State != path.end_State):
    #             self.logger.info("无法继续跳转！修改dfs栈："+str(next_State))
    #             return path.start_State
    #     self.logger.info("从头跳转成功！")
    #     return tmp_target_State
    
    # 该函数用于实现 返回前一状态
    def switch_to_State(self,nowState,targetState):
        self.logger.info("返回上一状态:"+str(targetState.page_path))
        '''
        传入参数:当前状态,目标状态
        返回结果:是否完成
        '''
        # 有路径直接点
        for path in self.statePath:
            if nowState == path.start_State and targetState == path.end_State:
                
                if (path.trigger == TriggerType.Click):
                    x,y=get_center(path.bound)
                    self.logger.info("点击记录:"+str([x,y]))
                    self.device_manager.device.click(x,y)
                elif (path.trigger == TriggerType.Scroll):
                    x1,y1,x2,y2=get_box(path.bound)
                    self.logger.info("滑动记录:"+str([x1,y1])+str([x2,y2]))
                    self.device_manager.device.drag(x2-50,y2-50,x1,y1,duration=1)


                time.sleep(1*self.wait)
                if(path.crash_type!=StateType.Normal):
                    self.call_system_back(targetState)
                if (targetState == self.device_manager.get_current_State()):
                    self.logger.info("返回成功")
                    return True
                else:
                    self.logger.info("返回失败")
                    return False
        self.logger.info("无关联按钮")
        return False
    
    def from_head_switch_to_State(self,target_State):
        tmp_target_State = target_State
        self.logger.info("开始从头跳转:"+str(target_State.page_path))
        self.device_manager.exit_miniapp()
        # 跳到当前状态
        self.device_manager.frida.jump(self.appid)
        # 用于记录从头点到这儿的路径
        path_list=[]
        while (self.statePre[self.stateList.index(tmp_target_State)] != None):
            path_tmp =self.statePre[self.stateList.index(tmp_target_State)]
            path_list.append(path_tmp)
            tmp_target_State=path_tmp.start_State
            # print(path_list)
            # print(str(path_tmp))
            # print("-----------stateList------------")
            # for i in self.stateList:
            #     print(str(i))
            # print("-----------statePre------------")
            # for i in self.statePre:
            #     print(str(i))
        path_list.reverse()
        tmp_section = 0
        for path in path_list:
            print(str(path))
        for path in path_list:
            if (path.trigger == TriggerType.Click):
                x,y=get_center(path.bound)
                # self.logger.info("点击记录:"+str([x,y]))
                self.device_manager.device.click(x,y)
                tmp_section = 0
            elif (path.trigger == TriggerType.Scroll):
                x1,y1,x2,y2=get_box(path.bound)
                # self.logger.info("滑动记录:"+str([x,y]))
                self.device_manager.device.drag(x2-50,y2-50,x1,y1,duration=1)
                tmp_section = tmp_section + 1
            time.sleep(2*self.wait)
            if(path.crash_type!=StateType.Normal):
                self.call_system_back(path.end_State)
            next_State=self.device_manager.get_current_State()
            next_State.section = tmp_section
            self.logger.info("已跳转至:"+str(next_State.page_path))
            if (next_State != path.end_State):
                self.logger.info("无法继续跳转！修改dfs栈："+str(path.start_State))
                return path.start_State
        self.logger.info("从头跳转成功！")
        return target_State

    # 调用系统返回
    def call_system_back(self,targetState):
        self.logger.info("尝试系统返回至："+str(targetState.page_path))
        # adb shell input keyevent 4 实现返回操作
        adb_command='adb shell input keyevent KEYCODE_BACK'
        os.system(adb_command)
        time.sleep(2*self.wait)
        currentSate=self.device_manager.get_current_State()
        if (currentSate.app_id == targetState.app_id and self.activity == self.device_manager.get_activity()):
            agree_and_check(self.device_manager,xml.dom.minidom.parseString(self.device_manager.device.dump_hierarchy()).documentElement)
            self.logger.info("系统返回成功")
            if(self.superapp=="alipay"):
            #     adb_command='adb shell input keyevent KEYCODE_APP_SWITCH'
            #     os.system(adb_command)
            #     time.sleep(1*self.wait)
            #     self.device_manager.device.click(self.device_manager.device.info['displayWidth']//2,self.device_manager.device.info['displayHeight']//2)
            #     time.sleep(1*self.wait)
                agree_and_check(self.device_manager,xml.dom.minidom.parseString(self.device_manager.device.dump_hierarchy()).documentElement)
            return True
        else: 
            self.logger.info("系统返回失败")
            if(self.superapp=="alipay"):
            #     adb_command='adb shell input keyevent KEYCODE_APP_SWITCH'
            #     os.system(adb_command)
            #     time.sleep(1*self.wait)
            #     self.device_manager.device.click(self.device_manager.device.info['displayWidth']//2,self.device_manager.device.info['displayHeight']//2)
            #     time.sleep(1*self.wait)
                agree_and_check(self.device_manager,xml.dom.minidom.parseString(self.device_manager.device.dump_hierarchy()).documentElement)
            return False

    def record_test_result(self):
        self.logger.info("覆盖路径：")
        self.logger.info(str(self.stateList))
        self.logger.info(str(self.statePath))
        List = []
        Path = []
        dif_page_path  = set([item.page_path for item in self.stateList if item.page_path.replace(".html","") in self.allStatePagepathList])
        
        for i in self.stateList:
            List.append(json.loads(str(i)))

        for i in self.statePath:
            Path.append(json.loads(str(i)))
        if self.allStatePagepathList:
            tmp_map_density_first = str(round((len(self.first_dif_page_path) / len(self.allStatePagepathList)) * 100,2))+"%"
            tmp_map_density_all = str(round((len(dif_page_path) / len(self.allStatePagepathList)) * 100,2))+"%"
        else:
            tmp_map_density_first = "None"
            tmp_map_density_all = "None"
        base_info = {
            "appid":self.appid,
            # "activity":self.activity,
            "crash_flag":self.crash_flag,
            "crash_info":self.crash_info,
            "dif_page_path_num":len(dif_page_path),
            "first_run_page_path_num":len(self.first_dif_page_path),
            "whole_page_path_num":len(self.allStatePagepathList),
            "map_density_first":tmp_map_density_first,
            "map_density_all":tmp_map_density_all,
            "total_time":f"{self.total_time//3600:02d}:{(self.total_time % 3600) // 60:02d}:{self.total_time % 60}"
            # 此处还能用于记录其他信息，比如说覆盖率等
        }
        open("./"+self.appid+"/"+"utg.json",'w',encoding='utf-8').write(json.dumps({"List":List,"Path":Path,"base_info":base_info},ensure_ascii=False))
        open("./formatted_data.json",'w',encoding='utf-8').write(json.dumps({"List":List,"Path":Path,"base_info":base_info},ensure_ascii=False))
        # 打开文件，如果文件不存在会自动创建
        with open("result.txt", "a") as file:
            file.write("app_id: " + str(base_info["appid"]) + "\t")
            file.write("map_density_first: " + base_info["map_density_first"] + "\t")
            file.write("map_density_all: " + base_info["map_density_all"] + "\t")
            file.write("crash_flag: " + str(base_info["crash_flag"]) + "\t")
            file.write("dif_page_path_num: " + str(base_info["dif_page_path_num"]) + "\t")
            file.write("first_run_page_path_num: " + str(base_info["first_run_page_path_num"]) + "\t")
            file.write("whole_page_path_num: " + str(base_info["whole_page_path_num"]) + "\t")
            file.write("total_time: " + str(base_info["total_time"]) + "\n")
            
       
        
        # raw_data = json.dumps({"List":List,"Path":Path,"base_info":base_info},ensure_ascii=False)
        # parsed_data = json.loads(raw_data)
        # # 重新格式化为JSON字符串
        # formatted_json = json.dumps(parsed_data, indent=4, ensure_ascii=False)
        # # 将重新格式化的JSON字符串保存到文件
        # with open("formatted_data.json", "w", encoding="utf-8") as json_file:
        #     json_file.write(formatted_json)

    def update(self,record_info):
        if ("new_state" in record_info and record_info["new_state"]):
            lastState,currentState,last_Action = record_info["State_append_path"]
            screenshot=self.device_manager.device.screenshot()

            pic_name="./"+self.appid+"/pic/node_"+str(time.time())+".jpg"
            screenshot.save(pic_name)
            currentState.screenshot=pic_name

            pic_name="./"+self.appid+"/pic/egde_"+str(time.time())+".jpg"
            screenshot=screenshot.crop(get_box(last_Action["bounds"]))
            screenshot.save(pic_name)

            path_tmp=PathClass(lastState,currentState,last_Action["bounds"],pic_name,last_Action["Type"],False,"")
            self.stateList.append(record_info["State_append_state"])
            self.statePath.append(path_tmp)
            self.statePre.append(path_tmp)
        elif ("new_path" in record_info and record_info["new_path"]):
            
            lastState,currentState,last_Action = record_info["State_append_path"]
            flag_path_exist=False
            for path in self.statePath:
                if lastState==path.start_State and currentState==path.end_State:
                    flag_path_exist=True
                    break
            if flag_path_exist == False:
                screenshot=self.device_manager.device.screenshot()
                pic_name="./"+self.appid+"/pic/egde_"+str(time.time())+".jpg"
                screenshot=screenshot.crop(get_box(last_Action["bounds"]))
                screenshot.save(pic_name)

                path_tmp=PathClass(lastState,currentState,last_Action["bounds"],pic_name,last_Action["Type"],False,"")
                
                self.statePath.append(path_tmp)
            

if __name__ == "__main__":
    pass