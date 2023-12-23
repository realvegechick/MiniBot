
import xml.dom.minidom
import time
from utils.xmlUtils import *
from utils.logCreator import *
import os
logger=log_creator("CustomUtils")

package={"wechat":"com.tencent.mm","alipay":"com.eg.android.AlipayGphone"}
superapp = "wechat"

def clear_text_node(root):
    for child in root.childNodes[:]:
        if child.nodeType == xml.dom.Node.TEXT_NODE:
            root.removeChild(child)
        elif child.nodeType == xml.dom.Node.ELEMENT_NODE:
            clear_text_node(child)
    return root


def find_checkable_nodes(node):
    checkable_nodes= []
    # 获取节点的属性值
    if node.nodeType == xml.dom.minidom.Node.ELEMENT_NODE and node.getAttribute("text") == "":
        flag_has_protocol=False
        siblings=node.parentNode.childNodes
        for sibling in siblings:
            if sibling.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                # 检查兄弟节点的文本内容是否包含关键字"已阅读"
                if ("已阅读" in sibling.getAttribute("text") or "同意" in sibling.getAttribute("text")) and int(sibling.getAttribute("index")) == int(node.getAttribute("index"))+1:
                    flag_has_protocol=True
                    break
        if flag_has_protocol == True:   
            return [node]
        
    for child in node.childNodes:
        checkable_nodes_tmp = find_checkable_nodes(child)
        for item in checkable_nodes_tmp:
            if item not in checkable_nodes:
                checkable_nodes.append(item)
    return checkable_nodes

def agree_and_check(device_manager,root):
    logger.info("勾选/点击授权弹窗")
    # 点一顿允许 TODO
    agree_nodes=[node for node in root.getElementsByTagName("node") if (node.getAttribute("text") == "同意" or node.getAttribute("text") == "允许" or node.getAttribute("text") == "确定" or node.getAttribute("text") == "我同意" or node.getAttribute("text") == "忽略" or node.getAttribute("text") == "我知道了" or node.getAttribute("text") == "我知道" or node.getAttribute("text") == "知道了")] 
    for node in agree_nodes:
        device_manager.click_node(node)
        # 点一顿勾
    checkable_nodes = find_checkable_nodes(root)
    for node in checkable_nodes:
        device_manager.click_node(node)
    return [node_hash(i) for i in agree_nodes+list(checkable_nodes)]

def get_miniapp_hierarchy(device_manager,dfsStack,restart=False,raw=False,depth=0):
    if(depth>2):
        raise Exception("无法获取页面布局！")
    logger.info("获取页面布局")
    if(restart):
        #os.system('adb shell /data/local/tmp/atx-agent server --stop')
        #os.system('adb shell /data/local/tmp/atx-agent server -d')
        device_manager.force_reset_uiautomator()
        
    #os.system('adb shell "curl http://127.0.0.1:7912/dump/hierarchy > /sdcard/hierachy.json"')
    # 为啥会卡住？？？TODO
    #os.system("adb pull /sdcard/hierachy.json ./")
    ui=device_manager.device.dump_hierarchy()#json.loads(open("./hierachy.json",encoding='utf-8').read())["result"]
    dom=xml.dom.minidom.parseString(ui)
    
    root=clear_text_node(dom.documentElement)
    open("./test0.xml",'wb').write(root.toprettyxml().encode("utf-8"))
    for node in root.childNodes:
        if(node.getAttribute("package")==package[device_manager.superapp]):
            if(raw==False):
                new_root=locate_window(device_manager,node,dfsStack)
                #open("./test.xml",'wb').write(new_root.toprettyxml().encode("utf-8"))
                return new_root
            else:
                open("./raw.xml",'wb').write(root.toprettyxml().encode("utf-8"))
                return root
    logger.warning("No "+package[device_manager.superapp]+" found!!!")
    device_manager.force_reset_uiautomator()
    logger.info("获取页面失败，重试")
    # 下面部分有待封装
    if(superapp=="alipay"):
    #     adb_command='adb shell input keyevent KEYCODE_APP_SWITCH'
    #     os.system(adb_command)
    #     time.sleep(2)
    #     device_manager.device.click(device_manager.device.info['displayWidth']//2,device_manager.device.info['displayHeight']//2)
    #     time.sleep(2)
          agree_and_check(xml.dom.minidom.parseString(device_manager.device.dump_hierarchy()).documentElement)
    return get_miniapp_hierarchy(device_manager,dfsStack,False,raw,depth+1)


def find_clickable_nodes(node,dfsStack):
    if(node==None):
        return []
    clickable_nodes=[]
    xmls=""
    for i in dfsStack[:-1]:
        xmls+=i.xml
    if node.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
        # 获取节点的属性值
        clickable=node.getAttribute("clickable")
        if clickable == "true" and int(node.getAttribute("index"))<=8:
            leaf_node_list = find_leaf_nodes(node)
            for item in leaf_node_list:
                if item not in clickable_nodes and item.toxml() not in xmls:
                    clickable_nodes.append(item)
    for child in node.childNodes:
        clickable_nodes_tmp = find_clickable_nodes(child,dfsStack)
        for item in clickable_nodes_tmp:
            if item not in clickable_nodes and item.toxml() not in xmls and int(item.getAttribute("index"))<=8:
                clickable_nodes.append(item)
    return clickable_nodes

def find_alipay_nodes(node,dfsStack):
    if(node==None):
        return []
    leaf_nodes=[]
    if node.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
        # 获取节点的属性值
        if int(node.getAttribute("index"))<=8:
            leaf_node_list = find_leaf_nodes(node)
            for item in leaf_node_list:
                if item not in leaf_nodes:
                    leaf_nodes.append(item)
    for child in node.childNodes:
        clickable_nodes_tmp = find_alipay_nodes(child,dfsStack)
        for item in clickable_nodes_tmp:
            if item not in leaf_nodes and int(item.getAttribute("index"))<=8:
                leaf_nodes.append(item)
    return leaf_nodes

# 处理页面覆盖 --支付宝基本没有页面覆盖
# 传入xml node
# 传出特定的子node 我当前页面的node
def locate_window(device_manager,node,dfsStack):
    if(device_manager.superapp=="alipay"):
        res=[i for i in node.getElementsByTagName("node") if i.getAttribute("resource-id")=="com.alipay.mobile.nebula:id/h5_web_content"]
        if(len(res)):
            return res[0]
        else:
            return node
    elif(device_manager.superapp=="wechat"):#stupid fix for stupid developers
        open("./test2.xml",'wb').write(node.toprettyxml().encode("utf-8"))
        # 理论上走到这儿的都是正确的xml
        # node.childNodes and 
        # 去掉异常处理观察是否会有错误的xml走到这一步
        while node.childNodes and node.getAttribute("resource-id") != "com.tencent.mm:id/biv":
            node=node.childNodes[0]
        open("./test1.xml",'wb').write(node.toprettyxml().encode("utf-8"))
        windows=[]
        for i in node.childNodes:
            if i.childNodes and len([k for k in i.childNodes[0].getElementsByTagName("node") if k.getAttribute("content-desc")=="更多"]):
                for j in i.childNodes[1:]:
                    if(j.getAttribute("class") =="android.widget.FrameLayout"):
                        open("./testj.xml",'wb').write(j.toprettyxml().encode("utf-8"))
                        windows+=[j]
        print("窗口数：",len(windows))
        for node in windows:
            dis=[]
            sim=get_sim_hash(node)
            print("------------------------------------------")
            print(sim.value)
            m=False
            print("+++++++++++++++++++++++")
            print(dfsStack)
            for page in dfsStack[:-1]:
                if(not page.hash):
                    continue
                d=sim.distance(page.hash)
                dis.append(d)
                print("distance:"+str(d))
                if d<=4:
                    print("SAME!!!!!!!!!!!!!!!!!!!!!!!!")
                    m=True
                    break
            print("+++++++++++++++++++++++")
            if(not m):
                logger.info("汉明距离："+str(dis))
                print("index:",windows.index(node))
                return node
        logger.warning("Same layout! What a coincidence!")
        # 与原有界面相似 不去探索
        return xml.dom.minidom.Element("")
    

def exclude_node(node):
    if node.getAttribute("content-desc")=="更多" or node.getAttribute("content-desc")=="关闭" or node.getAttribute("content-desc")==" ":
        return True
    return False


if __name__ == "__main__":
    pass

