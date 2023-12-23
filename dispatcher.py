from path import *
from utils.xmlUtils import *
from utils.logCreator import *
from custom_utils import *

logger=log_creator("Dispatcher")

def Exception_dispatcher(last_Action,last_State,Current_STATE):
    return Current_STATE['Crash_Type']

def Normal_dispatcher(last_Action,last_STATE,Current_STATE,device_manager,state_manager,dfsStack):
    if last_Action != None:
        lastState = last_STATE
        currentState = Current_STATE["current_State"]
        print(Current_STATE)
    
        if last_Action!=None and last_Action['Type'] == "Scroll":
            currentState.section=lastState.section+1
            currentState.hash=get_sim_hash(get_miniapp_hierarchy(device_manager,dfsStack))
            # print("-------------hash报错看这里--------------")
            # print(currentState)
            # print(lastState)
            # print(currentState.hash)
            # print(lastState.hash)
            
            # print("-------------hash报错看这里--------------")
            
            if(currentState.hash.distance(lastState.hash)>4):
                logger.info("翻页后有新状态"+str(currentState.page_path))
                # Current_STATE["State_type"] = "Scroll_New_State"
                return "Scroll_New_State"
                # self.dfsStack.append(nextState)
                # self.state_manager.stateList.append(nextState)
                # path_tmp=PathClass(nowState,nextState,self.last_Action["bounds"],"","Scroll")
                # self.state_manager.statePre.append(path_tmp)
                # self.state_manager.statePath.append(path_tmp)
            # 那应该跳回去
            else:
                logger.info("没有区别，不翻页")
                # Current_STATE["State_type"] = "Scroll_Same_State"
                return "Scroll_Same_State"
            

        # 下面这段代码不太好放到state_manager里面
        elif  lastState == currentState:
            logger.info("与原有状态相同")
            # Current_STATE["State_type"] = "Same_State"
            return "Same_State"
        elif not currentState in state_manager.stateList:
            logger.info("触发新的状态："+str(currentState.page_path))
            # Current_STATE["State_type"] = "New_State"
            return "New_State"
        else:
            logger.info("重复进入已访问状态:"+str(currentState.page_path))
            # Current_STATE["State_type"] = "Re-enter_State"
            return "Re-enter_State"
    else:
        return "Pass" 