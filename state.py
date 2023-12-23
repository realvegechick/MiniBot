from enum import Enum
import json
import copy
import time
# 定义一个枚举类
class StateType(Enum):
    Normal = "Normal"
    OutOfMiniApp = "OutOfMiniApp"
    InOtherHtml = "InOtherHtml"
    InOtherApp = "InOtherApp"

class State:
    # def __init__(self, app_id = "", page_path = "", current_url = "", state_type = "Normal",clicked=[],section=0,h=None):
    def __init__(self, app_id = None, page_path = None, current_url = None, state_type = None,clicked=None,section=None,h=None):
        if app_id == None:
            app_id = ""
        if page_path == None:
            page_path = ""
        if current_url == None:
            current_url = ""
        if state_type == None:
            state_type = "Normal"
        if clicked == None:
            clicked = []
        if section == None:
            section = 0
        self.app_id = app_id
        self.page_path = page_path
        self.current_url = current_url
        self.clicked = clicked
        self.section = section
        self.hash = h
        self.finished = False
        self.screenshot = None
        self.xml= ""
        if state_type == "Normal":
            self.state_type = StateType.Normal
        if state_type == "OutOfMiniApp":
            self.state_type = StateType.OutOfMiniApp
        if state_type == "InOtherHtml":
            self.state_type = StateType.InOtherHtml
        if state_type == "InOtherApp":
            self.state_type = StateType.InOtherApp
        self.time=time.time()
        # if state_type == "Normal"
        # self.state_type = 
    
    def __eq__(self, other):
        if isinstance(other, State):
            return self.page_path == other.page_path and self.section == other.section
        return False

    def __hash__(self):
        return self.page_path+" "+str(self.section)
    
    def __str__(self):
        # 创建一个空字典
        attributes_dict = {}
        # 遍历类的属性
        for attr_name in dir(self):
            # 排除特殊属性和方法
            if not attr_name.startswith("__") and not callable(getattr(self, attr_name)):
                # 将属性名和对应的值存储在字典中
                if isinstance(getattr(self, attr_name),StateType) :
                    attributes_dict[attr_name] = str(getattr(self, attr_name).name)
                else:
                    attributes_dict[attr_name] = str(getattr(self, attr_name))
        print("---------------!!!!------------------")
        print(self.page_path)
        return json.dumps(attributes_dict)
    
    def __deepcopy__(self, memo):
        # 创建一个新的对象
        new_obj = self.__class__.__new__(self.__class__)

        # 使用反射遍历类的属性，并为每个属性执行深拷贝
        for attr_name in self.__dict__:
            setattr(new_obj, attr_name, copy.deepcopy(getattr(self, attr_name), memo))

        return new_obj


if __name__ == "__main__":

    # # 创建一个State对象
    # state = State("Active")

    # # 访问状态的名称字段
    # print(state.page_path)  # 输出: Active
    print(StateType.Normal.name)

