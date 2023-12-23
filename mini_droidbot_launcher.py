import os
import json
import time
from state import *
from utils.fridaUtils import *
from utils.xmlUtils import *
from utils.logCreator import *
from path import *
import simhash
from PIL import *
import traceback
import sys
from device_manager import *
from strategy_manager import *
from state_manager import *
'''
    conf = {
        fastmode:False,
        wait:2,
        timeout:60*30
    }
'''
class MiniDroidbotLaucher:
    
    def __init__(self,conf, test_app_list):
        self.conf = conf
        self.test_app_list = test_app_list
        
        # 日志
        self.logger=log_creator("Launcher")


    # 这个应该放在外面
    def scanner_run(self):
        # 实例化三个manager
        
        self.device_manager = DeviceManager(self.conf)
        self.state_manager = StateManager(self.conf,self.device_manager)
        self.stratagy_manager = StrategyManager(self.conf,self.state_manager,self.device_manager)
        for appid in self.test_app_list:
            os.system("mkdir .\\"+appid)
            os.system("mkdir .\\"+appid+"\\pic")

            self.state_manager.reset()
            self.stratagy_manager.reset()
                 
            self.state_manager.set_appid(appid)

            self.logger.info("开始测试："+appid)

            self.device_manager.lauchSuperAPP()
            self.device_manager.LaunchMiniProgram(appid)

            self.state_manager.set_activity(self.device_manager.get_activity())
            
            self.logger.info("初始化完成")

            # ---------异常处理-----------
            # TODO 这部分代码还是需要改一改
            try:
                self.search_mini_program()
            except KeyboardInterrupt:
                print("手动停止")
                traceback.print_exc()
                self.crash_flag = True
                self.crash_info = traceback.format_exc()
            except Exception:
                print("发现异常")
                traceback.print_exc()
                self.crash_flag = True
                self.crash_info = traceback.format_exc()
            finally:
                print("某个小程序测完了")
                self.state_manager.record_test_result()       
                
                if (appid == self.test_app_list[-1]):
                    print("测试全部完成")
                else:
                    print("测试还没完成")
                    continue
            
    
    
    # 执行机执行的代码
    def search_mini_program(self):
        while True:
            # 初始化
            self.before_execute()

            # 执行机执行
            while(True):   
                Current_STATE = self.state_manager.get_Current_STATE()
                Action = self.stratagy_manager.get_Action(Current_STATE)
                if Action != None:
                    self.device_manager.execute(Action)
                else:
                    break

            # 寻找其他状态去拉起
            if not self.get_next_start_state():
                break


        self.logger.info(self.state_manager.appid+" 测试结束！")
        # self.logger.info("花费时间："+str(t//60)+":"+str(int(t)%60))
        return 

    # 初始化
    def before_execute(self):
        nowState=self.device_manager.get_current_State()
        # self.stratagy_manager.dfsStack=[State()]
        self.stratagy_manager.dfsStack.append(nowState)
        self.stratagy_manager.dfsStack[-1].hash = get_sim_hash(get_miniapp_hierarchy(self.device_manager,self.stratagy_manager.dfsStack))
        screenshot=self.device_manager.device.screenshot()
        pic_name="./"+self.state_manager.appid+"/pic/node_"+str(time.time())+".jpg"
        screenshot.save(pic_name)
        nowState.screenshot=pic_name
        self.state_manager.statePre.append(None)
        self.state_manager.stateList.append(nowState)
    
    # 寻找其他的状态去拉起
    def get_next_start_state(self):
        with open(self.conf['input_file'], "r") as json_file:
            tmp_json_data = json.load(json_file)
        allStatePagepathList = tmp_json_data[self.state_manager.appid]
        self.state_manager.allStatePagepathList = copy.deepcopy(tmp_json_data[self.state_manager.appid])
        for i in self.state_manager.stateList:
            if i.page_path.replace(".html","") in allStatePagepathList:
                allStatePagepathList.remove(i.page_path.replace(".html",""))
        print(allStatePagepathList)
        while (allStatePagepathList and not self.state_manager.jump_to_State(allStatePagepathList[-1]+".html"*(self.conf["superapp"]=="wechat"))):
            allStatePagepathList.pop()
            time.sleep(1*self.conf["wait"])
        if not allStatePagepathList:
            return False
        return True

if __name__ == "__main__":
    conf = {}
    conf['superapp'] = "alipay"
    conf['wait'] = 1
    conf['timeout'] = 30*60
    conf['fastmode'] = False
    conf['package'] = {"wechat":"com.tencent.mm","alipay":"com.eg.android.AlipayGphone"}
    conf['input_file'] = "zhifubao_pathct1.json"
    
    explorer=MiniDroidbotLaucher(conf,['2021002175660392']) 
    explorer.scanner_run()

