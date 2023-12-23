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

package={"wechat":"com.tencent.mm","alipay":"com.eg.android.AlipayGphone"}

class ClickException(Exception):
    pass

class DeviceManager:
    # conf用于记录传入的参数，包括需要的小程序的基本参数 
    # statemanager实例需要来一个
    def __init__(self,conf):
        # 配置文件
        self.superapp=conf["superapp"]
        self.wait=conf["wait"]
        self.package = conf["package"]
        # 这两个比较特殊，获取与小程序交互的必要内容
        # self.device=conf["device"]
        # self.frida=conf["frida"]
        
        self.device=None
        self.frida=None


        # 日志
        self.logger=log_creator("DeviceManager")

    # 启动wx/zfb
    def lauchSuperAPP(self,reset=True):
        if(reset==True):
            self.device=u2.connect()
            self.device.app_stop(package[self.superapp])
            time.sleep(1*self.wait)
        flag=1
        while flag:
            flag=0
            self.device.app_start(package[self.superapp])
            try:
                if(self.superapp=="wechat"):
                    self.logger.info("******重启微信******")
                    time.sleep(2*self.wait)
                    self.click("发现")
                    self.click("小程序")
                    time.sleep(1*self.wait)
                else:
                    self.logger.info("******重启支付宝******")
                    time.sleep(3*self.wait)
                    self.click("忽略")
                    time.sleep(1*self.wait)
            except ClickException:
                flag=1
        self.logger.info("******重启Frida******")
        self.frida=Frida(self.superapp)
        time.sleep(1*self.wait)

    
    # 点击text为某一字符的节点 暂时只用于启动微信和支付宝的时候是哟个
    def click(self,str):
        time.sleep(1*self.wait)
        ui=self.device.dump_hierarchy()
        dom=xml.dom.minidom.parseString(ui)
        root=dom.documentElement
        matching_nodes=[node for node in root.getElementsByTagName("node") if node.getAttribute("text") == str]
        #TODO FIX THIS
        try:
            x,y=get_center(matching_nodes[0])
            self.device.click(x,y)
        except:
            print(ui)
            print(str)
            raise Exception("No such node! Check for setup!")
        time.sleep(1*self.wait)

    # 启动微信小程序
    def LaunchMiniProgram(self,appid):
        self.frida.jump(appid)
        self.logger.info(appid+"已启动！")
        time.sleep(2*self.wait)
    
    # 获取当前activity
    def get_activity(self):
        # adb shell "dumpsys window | grep mCurrentFocus" 实现获取当前页面activity操作
        adb_command='adb shell "dumpsys window | grep mCurrentFocus"'
        result=subprocess.run(adb_command, shell=True, check=True,capture_output=True)
        output_bytes=result.stdout
        output_str=output_bytes.decode('utf-8')
        match=re.search(r'{([^}]*)}', output_str)
        if match:
            res=match.group(1)
        return res[res.index("com."):]
    
    def get_base_xml(self,restart=False):
        self.logger.info("获取页面布局")
        if(restart):
            #os.system('adb shell /data/local/tmp/atx-agent server --stop')
            #os.system('adb shell /data/local/tmp/atx-agent server -d')
            self.device._force_reset_uiautomator_v2()
            time.sleep(1*self.wait)
        #os.system('adb shell "curl http://127.0.0.1:7912/dump/hierarchy > /sdcard/hierachy.json"')
        #os.system("adb pull /sdcard/hierachy.json ./")
        ui=self.device.dump_hierarchy()#json.loads(open("./hierachy.json",encoding='utf-8').read())["result"]
        dom=xml.dom.minidom.parseString(ui)
        return dom.documentElement
    
    def get_path(self):
        return self.frida.getPath()

    # 获取当前页面状态，包括app_id,page_path,current_url 
    def get_current_State(self):
        time.sleep(1*self.wait)
        data=self.frida.getPath()
        # 对字符串进行操作
        app_id=data.get('appId', '')
        page_path=data.get('pagePath', '').split("?")[0]
        if("url" in data):
            current_url=data.get('url', '')
        else:
            current_url=data.get('currentUrl', '')
        return State(app_id,page_path,current_url,)
    
    # 这个和get_base_xml重复了
    def get_whole_xml(self,restart=False):
        self.logger.info("获取页面布局")
        if(restart):
            #os.system('adb shell /data/local/tmp/atx-agent server --stop')
            #os.system('adb shell /data/local/tmp/atx-agent server -d')
            self.device._force_reset_uiautomator_v2()
            time.sleep(1*self.wait)
        #os.system('adb shell "curl http://127.0.0.1:7912/dump/hierarchy > /sdcard/hierachy.json"')
        #os.system("adb pull /sdcard/hierachy.json ./")
        ui=self.device.dump_hierarchy()#json.loads(open("./hierachy.json",encoding='utf-8').read())["result"]
        dom=xml.dom.minidom.parseString(ui)
        return dom.documentElement
    
    def force_reset_uiautomator(self):
        self.device._force_reset_uiautomator_v2()
        time.sleep(1*self.wait)

    # 关闭当前小程序
    def exit_miniapp(self):
        self.logger.info("关闭小程序窗口")
        # 点关闭
        
        
        root = self.get_base_xml()
        has_superapp_package = False
        # print(self.base_xml)
        # print(type(self.base_xml))
        for node in root.childNodes:
            # print(node)
            # print(type(node))
            # input()
            if(not isinstance(node,xml.dom.minidom.Text) and node.getAttribute("package")==self.package[self.superapp]):
                has_superapp_package = True
                break
        if has_superapp_package == False:
            root = self.get_base_xml(True)
    
        
        exit_nodes=[node for node in root.getElementsByTagName("node") if(node.getAttribute("content-desc") == "关闭" 
                    and node.getAttribute("clickable") == "true")] 
        if exit_nodes:
            x,y=get_center(exit_nodes[0])
            self.device.click(x,y)
            self.logger.info("点击关闭按钮")
            time.sleep(0.5*self.wait)
            if(self.superapp=="alipay"):
                self.lauchSuperAPP(reset=False)
        else:
            self.logger.info("出状况了，重启一下")
            self.lauchSuperAPP()
        time.sleep(1*self.wait)
        return
    
    def click_node(self,node):
        x,y=get_center(node)
        self.device.click(x,y)
    
    def scroll_node(self,node):
        x1,y1,x2,y2=get_box(node)
        # 增加滑动逻辑
        self.device.drag(x2-50,y2-50,x1,y1,duration=1)

    def execute(self,Action):
        if Action["Type"] == "Pass":
            pass
        elif Action["Type"] == "Click":
            self.click_node(Action["bounds"])
        elif Action["Type"] == "Scroll":
            self.scroll_node(Action["bounds"])
        return
    
if __name__ == "__main__":
    pass