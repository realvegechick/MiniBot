from enum import Enum
from state import *
# 定义一个枚举类
class TriggerType(Enum):
    Click = "Click"
    Scroll = "Scroll"
    CallSysBack = "Back"

class PathClass:
    # def __init__(self, start_State, end_State, bound, pic_name,trigger = "Click", crash=False, crash_type = ""):
    def __init__(self, start_State, end_State, bound, pic_name,trigger = None, crash=None, crash_type = None):
        if trigger == None:
            trigger = "Click"
        if crash == None:
            crash = False
        if crash_type == None:
            crash_type = ""
        self.start_State = start_State  # 起始节点
        self.end_State = end_State      # 结束节点
        if(start_State==end_State):
            raise Exception("Bad path!")
        self.bound=bound
        self.pic_name = pic_name
        self.crash = crash
        if trigger == "Click":
            self.trigger = TriggerType.Click  
        if trigger == "Scroll":
            self.trigger = TriggerType.Scroll        
        if trigger == "Back":
            self.trigger = TriggerType.CallSysBack        
        if crash == True:
            if crash_type == "OutOfMiniApp":
                self.crash_type = StateType.OutOfMiniApp
            if crash_type == "InOtherHtml":
                self.crash_type = StateType.InOtherHtml
            if crash_type == "InOtherApp":
                self.crash_type = StateType.InOtherApp
        else:
            self.crash_type = StateType.Normal
        

    def __str__(self):
        # 创建一个空字典
        attributes_dict = {}
        # 遍历类的属性
        for attr_name in dir(self):
            # 排除特殊属性和方法
            if not attr_name.startswith("__") and not callable(getattr(self, attr_name)):
                # 将属性名和对应的值存储在字典中
                if(isinstance(getattr(self, attr_name),State)):
                    attributes_dict[attr_name] = str(getattr(self, attr_name).page_path)+"_"+str(getattr(self, attr_name).section)
                elif isinstance(getattr(self, attr_name),TriggerType) or isinstance(getattr(self, attr_name),StateType) :
                    attributes_dict[attr_name] = str(getattr(self, attr_name).name)
                else:
                    attributes_dict[attr_name] = str(getattr(self, attr_name))
        print("---------------!!!!------------------")
        #print(json.dumps(attributes_dict))
        return json.dumps(attributes_dict)
    
if __name__=="__main__":
    print(PathClass(State(),State()))