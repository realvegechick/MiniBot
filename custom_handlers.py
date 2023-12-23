from path import *
import time
from utils.xmlUtils import *
from utils.logCreator import *
from custom_utils import *

logger=log_creator("CustomHandler")
def out_of_miniapp(device_manager,state_manager,dfsStack):
    target_State = dfsStack[-1]
    if state_manager.call_system_back(target_State):
        pass
    else:
        device_manager.lauchSuperAPP()
        if state_manager.jump_to_State(target_State):
            pass
        else:
            # 不行就从头再来 心若在梦就在 天地之间还有真爱 看成败人生豪迈 只不过是从头再来
            last_available_State=state_manager.from_head_switch_to_State(dfsStack[-1])
            while (len(dfsStack)>1 and last_available_State!= dfsStack[-1]):
                dfsStack.pop()
 
def in_other_app(device_manager,state_manager,dfsStack):
    target_State = dfsStack[-1]
    if state_manager.call_system_back(target_State):
        pass
    else:
        if state_manager.jump_to_State(target_State):
            pass
        else:
            # 不行就从头再来 心若在梦就在 天地之间还有真爱 看成败人生豪迈 只不过是从头再来
            last_available_State=state_manager.from_head_switch_to_State(dfsStack[-1])
            while (len(dfsStack)>1 and last_available_State!= dfsStack[-1]):
                dfsStack.pop()
                    
def in_other_html(device_manager,state_manager,dfsStack):
    target_State = dfsStack[-1]
    if state_manager.call_system_back(target_State):
        pass
    else:
        if state_manager.jump_to_State(target_State):
            pass
        else:
            # 不行就从头再来 心若在梦就在 天地之间还有真爱 看成败人生豪迈 只不过是从头再来
            last_available_State=state_manager.from_head_switch_to_State(dfsStack[-1])
            while (len(dfsStack)>1 and last_available_State!= dfsStack[-1]):
                dfsStack.pop()

def pass_func(*args):
    pass

Exception_Handlers = {
    "OutOfMiniApp": out_of_miniapp,
    "InOtherApp":in_other_app,
    "InOtherHtml":in_other_html,
    "Pass":pass_func

}

def same_state_handler(last_Action,last_STATE,Current_STATE,device_manager,state_manager):
    return {}

def new_state_handler(last_Action,last_STATE,Current_STATE,device_manager,state_manager):
    lastState = last_STATE
    currentState = Current_STATE["current_State"]

    return {
        "dfs_append":True,
        "dfs_append_state":currentState,
        "state_manager_update":True,
        "new_state":True,
        "State_append_state":currentState,
        "State_append_path":(lastState,currentState,last_Action)
    }
  

def reenter_state_handler(last_Action,last_STATE,Current_STATE,device_manager,state_manager):
    lastState = last_STATE
    currentState = Current_STATE["current_State"]

    

    flag_path_exist=False
    for path in state_manager.statePath:
        if lastState==path.start_State and currentState==path.end_State:
            flag_path_exist=True
            break

    if not flag_path_exist :
        return {
            "state_manager_update":True,
            "new_path":True,
            "State_append_path":(lastState,currentState,last_Action),
            "Jump":True,
            "target_State":lastState
        }
    else:
        return {
            "Jump":True,
            "target_State":lastState
        }

def scroll_new_state_handler(last_Action,last_STATE,Current_STATE,device_manager,state_manager):
    lastState = last_STATE
    currentState = Current_STATE["current_State"]
    currentState.section = lastState.section + 1
    # 这个dfs入栈应该放在action那里去操作一下
    # 这个函数还是有个返回值比较好
    # path_tmp=PathClass(lastState,currentState,last_Action["node"].getAttribute("bounds"),"","Scroll")

    return {
        "dfs_pop":True,
        "dfs_append":True,
        "dfs_append_state":currentState,
        "state_manager_update":True,
        "new_state":True,
        "State_append_state":currentState,
        "State_append_path":(lastState,currentState,last_Action)
    }


def scroll_same_state_handler(last_Action,last_STATE,Current_STATE,device_manager,state_manager):
    return {
        "Back":True
    }

Normal_Handlers = {
    "Same_State" : same_state_handler,
    "New_State" : new_state_handler,
    "Re-enter_State" : reenter_state_handler,
    "Scroll_New_State": scroll_new_state_handler,
    "Scroll_Same_State": scroll_same_state_handler,
    "Pass":pass_func
}



def Jump(Current_STATE,targetState,device_manager,state_manager,dfsStack):
    currentState = Current_STATE["current_State"]
    if state_manager.switch_to_State(currentState, targetState):
        pass
    elif state_manager.call_system_back(targetState):
        pass
    elif state_manager.jump_to_State(targetState):
        pass
    else:
        # 从头再来
        last_available_State=state_manager.from_head_switch_to_State(targetState)
        print("--------Stack----------")
        for i in dfsStack:
            print(i.page_path)
        print("--------Stack----------")
        while (last_available_State in dfsStack and last_available_State!= dfsStack[-1]):
            dfsStack.pop()
    return


def Back(device_manager,state_manager,dfsStack):
    currentState = dfsStack[-1]
    dfsStack.pop()
    if (len(dfsStack) < 1):
        logger.info("终于尼玛结束了结束了结束了")
        return False
    # 这部分逻辑应该是相同的，点回上一节点
    if state_manager.switch_to_State(currentState, dfsStack[-1]):
        pass
    elif state_manager.call_system_back(dfsStack[-1]):
        pass
    # 不行就jump到那个节点
    elif state_manager.jump_to_State(dfsStack[-1]):
        pass
    else:
        # 不行就从头再来
        last_available_State=state_manager.from_head_switch_to_State(dfsStack[-1])
            
        # 修改dfs调用栈
        while (len(dfsStack)>1 and last_available_State!= dfsStack[-1]):
            dfsStack.pop()
    logger.info("跳转成功")
    return True



def Before_Next_Action(device_manager,state_manager,dfsStack):
    dfsStack[-1].clicked+=agree_and_check(device_manager,device_manager.get_base_xml())
    return 

def DFS(device_manager,state_manager,dfsStack,conf):
    nowState=dfsStack[-1]
    # agree_and_check(device_manager.get_base_xml())
    root=get_miniapp_hierarchy(device_manager,dfsStack)
    # print(root)
    # print(root.toxml())
    # input()
    if(not nowState.hash):
        nowState.hash=get_sim_hash(root)
    if(nowState.xml==""):
        nowState.xml=root.toxml()
        

    # 获取当前ui的xml
    logger.info("----------------"+str(nowState.page_path)+"--------------------")
    logger.info("寻找可点击节点")
    if(conf["fastmode"]):
        target_nodes=[i for i in root.getElementsByTagName("node") if i.getAttribute("clickable")=="true"]
    elif(conf["superapp"]=="alipay"):
        target_nodes=find_alipay_nodes(root,dfsStack)
    else:
        target_nodes=find_clickable_nodes(root,dfsStack)
    current_node=None
    for node in target_nodes:
        # 跳过已访问和系统ui
        if node_hash(node) in nowState.clicked :
            print("重复节点：",node.getAttribute("text")+node.getAttribute("bounds"))
            continue
        elif exclude_node(node):
            continue
        else:
            current_node=node
            break
    logger.info("待点击的节点:"+get_node_attributes(current_node))
    


    
    if current_node==None:
        nowState.finished=True        
        # 翻页看看
        scroll=[i for i in root.getElementsByTagName("node") if i.getAttribute("class")=="android.webkit.WebView"]
        if(scroll and nowState.section<2):
            return {
                "Type":"Scroll",
                "bounds":scroll[0].getAttribute("bounds"),
                # "node":current_node
            }
        else:
            print("滚动条都没有，不翻页")
            # `回退dfs栈`
            if Back(device_manager,state_manager,dfsStack):
                return {

                }
            else:
                return None
            
                    
    else:
    # 点击当前状态
        nowState.clicked.append(node_hash(current_node))
        logger.info("点击位置："+str(current_node.getAttribute("bounds")))
        return {
            "Type":"Click",
            "bounds":current_node.getAttribute("bounds"),
            # "node":current_node
        }

Get_Next_Action = {
    "DFS" : DFS
}