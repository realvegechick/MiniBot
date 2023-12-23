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
from utils.logCreator import loginit
from path import *
import simhash
from PIL import *
import traceback
from custom_utils import *

package={"wechat":"com.tencent.mm","alipay":"com.eg.android.AlipayGphone"}
logging.disable(logging.DEBUG)

def clear_text_node(root):
    for child in root.childNodes[:]:
        if child.nodeType == xml.dom.Node.TEXT_NODE:
            root.removeChild(child)
        elif child.nodeType == xml.dom.Node.ELEMENT_NODE:
            clear_text_node(child)
    return root

def get_center(node):
    if isinstance(node,xml.dom.minidom.Node):
        x1,y1,x2,y2=[int(i) for i in node.getAttribute("bounds")[1:-1].replace("][",",").split(",")]
    elif isinstance(node,str):
        x1,y1,x2,y2=[int(i) for i in node[1:-1].replace("][",",").split(",")]
    return ((x1+x2)/2,(y1+y2)/2)

def node_hash(node):
    return node.getAttribute("bounds")

def get_activity():
    # adb shell "dumpsys window | grep mCurrentFocus" 实现获取当前页面activity操作
    adb_command='adb shell "dumpsys window | grep mCurrentFocus"'
    result=subprocess.run(adb_command, shell=True, check=True,capture_output=True)
    output_bytes=result.stdout
    output_str=output_bytes.decode('utf-8')
    match=re.search(r'{([^}]*)}', output_str)
    if match:
        res=match.group(1)
    return res[res.index("com."):]

def find_leaf_nodes(node):
    leaf_nodes=[]
    if node.nodeType == xml.dom.minidom.Node.ELEMENT_NODE and len(node.childNodes) == 0:
        leaf_nodes.append(node)
    for child in node.childNodes:
        leaf_nodes.extend(find_leaf_nodes(child))
    return leaf_nodes

def find_clickable_nodes(node):
    clickable_nodes=[]
    
    if node.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
        # 不要点击下面的导航栏 关闭 更多
        #if "systemui" in node.getAttribute("resource-id") or "systemui" in node.getAttribute("package") :
            #return clickable_nodes
        #if (node.getAttribute("content-desc") == "关闭" or node.getAttribute("content-desc") == "更多" or node.getAttribute("content-desc") == "上首页") and node.getAttribute("clickable") == "true":
            #return clickable_nodes
        # 获取节点的属性值
        clickable=node.getAttribute("clickable")
        if clickable == "true":
            leaf_node_list = find_leaf_nodes(node)
            for item in leaf_node_list:
                if item not in clickable_nodes:
                    clickable_nodes.append(item)
            
        
    for child in node.childNodes:
        clickable_nodes_tmp = find_clickable_nodes(child)
        for item in clickable_nodes_tmp:
            if item not in clickable_nodes:
                clickable_nodes.append(item)
    return clickable_nodes

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

def get_node_attributes(node):
    res=''
    if node!=None and node.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
        attributes=node.attributes
        for attr_name in attributes.keys():
            attr_value=attributes.get(attr_name).nodeValue
            res+=attr_name+":"+attr_value+","
    else:
        res="None"
    return res

def get_sim_hash(root):
    return simhash.Simhash("".join([node.getAttribute("text") for node in root.getElementsByTagName("node")]))

def get_box(s):
    p1,p2=s[1:-1].split("][")
    x1,y1=[int(i) for i in p1.split(",")]
    x2,y2=[int(i) for i in p2.split(",")]
    return (x1,y1,x2,y2)


class Explorer:
    def __init__(self,superapp):
        self.superapp=superapp
        self.logger=loginit()
        # 用于记录State的个数，下标访问，简单又粗暴，有更好的数据结构可以替换
        self.stateList=[]
        # 用于记录每个State的前驱路劲，通过记录该路径在statePath中的下标号来记录
        self.statePre=[]
        # 用于记录State间的点击状态，先拿数组写
        # 效率确实差，因为查找起来速度太慢了
        self.statePath=[]

        self.activity=""
        self.appid=""
        self.wait=2
        self.timeout=30*60
        self.fastmode=False

    def lauchSuperAPP(self,reset=True):
        if(reset==True):
            self.device=u2.connect()
            self.device.app_stop_all()
            time.sleep(1*self.wait)
        self.device.app_start(package[self.superapp] , stop=True)
        if(self.superapp=="wechat"):
            self.logger.info("******重启微信******")
            time.sleep(2*self.wait)
            self.click("发现")
            self.click("小程序")
            time.sleep(1*self.wait)
        else:
            self.logger.info("******重启支付宝******")
            time.sleep(1*self.wait)
            self.click("忽略")
            time.sleep(0.5*self.wait)
        self.frida=Frida(self.superapp)
        time.sleep(0.5*self.wait)

    def click(self,str):
        time.sleep(0.5*self.wait)
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
        time.sleep(0.5*self.wait)


        # adb shell "dumpsys window | grep mCurrentFocus" 实现获取当前页面activity操作
        adb_command='adb shell "dumpsys window | grep mCurrentFocus"'
        result=subprocess.run(adb_command, shell=True, check=True,capture_output=True)
        output_bytes=result.stdout
        output_str=output_bytes.decode('utf-8')
        match=re.search(r'{([^}]*)}', output_str)
        if match:
            res=match.group(1)
        return res[res.index("com."):]
    # 获取当前页面状态，包括app_id,page_path,current_url 
    def get_current_State(self):
        data=self.frida.getPath()
        # 对字符串进行操作
        app_id=data.get('appId', '')
        page_path=data.get('pagePath', '').split("?")[0]
        if("url" in data):
            current_url=data.get('url', '')
        else:
            current_url=data.get('currentUrl', '')
        return State(app_id,page_path,current_url,)

    # 关闭当前小程序
    def exit_miniapp(self):
        self.logger.info("关闭小程序窗口")
        # 点关闭
        root=xml.dom.minidom.parseString(self.device.dump_hierarchy()).documentElement
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
            self.logger.info("已离开小程序页面")
        time.sleep(1*self.wait)
        return
    
    # 调用系统返回
    def call_system_back(self,targetState):
        self.logger.info("尝试系统返回至："+str(targetState))
        # adb shell input keyevent 4 实现返回操作
        adb_command='adb shell input keyevent KEYCODE_BACK'
        os.system(adb_command)
        time.sleep(0.5*self.wait)
        currentSate=self.get_current_State()
        self.dfsStack[-1].clicked+=agree_and_check(xml.dom.minidom.parseString(self.device.dump_hierarchy()).documentElement)
        if (currentSate.app_id == targetState.app_id and self.activity == get_activity()):
            self.logger.info("系统返回成功")
            return True
        else: 
            self.logger.info("系统返回失败")
            return False

    # ——————————————————————非递归实现dfs————————————————————————
    def search_mini_program(self):
        device=self.device
        
        self.logger.info("截屏")
        screenshot=device.screenshot()
        pic_name="./"+self.appid+"/pic/node_"+str(time.time())+".jpg"
        screenshot.save(pic_name)

        with open("pathct1.json", "r") as json_file:
            tmp_json_data = json.load(json_file)
        allStatePagepathList = tmp_json_data[self.appid]
        while True:
            nowState=self.get_current_State()
            self.dfsStack=[State()]
            self.dfsStack.append(nowState)

            self.statePre.append(None)
            self.stateList.append(nowState)
            
            #返回值是花费的时间
            # 时间再做吧 懒得写了 为啥这个时间这个事黄博那么上心呢
            t=self.DFS(self.timeout)
            print("到这儿啦到这儿啦！！！！！！！！！！！！！！！！")
            for i in self.stateList:
                if i.page_path in allStatePagepathList:
                    allStatePagepathList.remove(i.page_path)
            print(allStatePagepathList)
            while (allStatePagepathList and not self.jump_to_State(allStatePagepathList[-1]+".html")):
                allStatePagepathList.pop()
                time.sleep(1*self.wait)
            if not allStatePagepathList:
                break

        
        
        self.logger.info(self.appid+" 测试结束！")
        self.logger.info("花费时间："+str(t//60)+":"+str(int(t)%60))
        return 

    # 用于记录小程序最终运行完成以后的信息
    def record_test_result(self):
        self.logger.info("覆盖路径：")
        self.logger.info(str(self.stateList))
        self.logger.info(str(self.statePath))
        List = []
        Path = []
        for i in self.stateList:
            List.append(json.loads(str(i)))
        for i in self.statePath:
            Path.append(json.loads(str(i)))
        
        base_info = {
            "appid":self.appid,
            # "activity":self.activity,
            "crash_flag":self.crash_flag,
            "crash_info":self.crash_info
            # 此处还能用于记录其他信息，比如说覆盖率等
        }
        open("./"+self.appid+"/"+"utg.json",'w',encoding='utf-8').write(json.dumps({"List":List,"Path":Path,"base_info":base_info},ensure_ascii=False))
        open("./formatted_data.json",'w',encoding='utf-8').write(json.dumps({"List":List,"Path":Path,"base_info":base_info},ensure_ascii=False))

        # raw_data = json.dumps({"List":List,"Path":Path,"base_info":base_info},ensure_ascii=False)
        # parsed_data = json.loads(raw_data)
        # # 重新格式化为JSON字符串
        # formatted_json = json.dumps(parsed_data, indent=4, ensure_ascii=False)
        # # 将重新格式化的JSON字符串保存到文件
        # with open("formatted_data.json", "w", encoding="utf-8") as json_file:
        #     json_file.write(formatted_json)

    def init_mini_program(self,appid):
        os.system("mkdir .\\"+appid)
        os.system("mkdir .\\"+appid+"\\pic")
        self.logger.info("开始测试："+appid)
        self.lauchSuperAPP()
        time.sleep(2*self.wait)
        self.frida.jump(appid)
        self.logger.info(appid+"已启动！")
        time.sleep(4*self.wait)
        self.stateList=[]
        self.statePath=[]
        self.statePre=[]
        self.appid=appid
        self.activity=get_activity()
        self.crash_flag = False
        self.crash_info = ""
        self.logger.info("初始化完成")

    def scanner_run(self,mini_program_list,wait=1,timeout=30*60,fastmode=False):
        #快速模式（不遍历叶子节点）
        self.fastmode=fastmode
        #sleep倍率，目前2比较合适
        self.wait=wait
        #搜索时间
        self.timeout=timeout
        # 用于测试遍历的小程序列表
        for appid in mini_program_list:
            self.init_mini_program(appid)
            # ---------异常处理-----------
            try:
                self.search_mini_program()
            except KeyboardInterrupt:
                print("你keykeykey")
                traceback.print_exc()
                self.crash_flag = True
                self.crash_info = traceback.format_exc()
                pass
            except Exception:
                print("你tm你走到这儿了没啊你tm你走到这儿了没啊你tm你走到这儿了没啊你tm你走到这儿了没啊你tm你走到这儿了没啊")
                traceback.print_exc()
                self.crash_flag = True
                self.crash_info = traceback.format_exc()
                pass
            finally:
                self.record_test_result()       
                if (appid == mini_program_list[-1]):
                    print("你jb退不退啊退不退啊退不退啊退不退啊退不退啊退不退啊退不退啊")
                    # 结束不太了 有点小bug
                    # os._exit(0)
                else:
                    print("不退不退不退")
                    continue

            # 计算最终覆盖率
 

# wxfe9e236ea38b053b 吉工家
# 异常状态的记录已经基本完成
# 异常处理还需完善，包括从头开始点的时候怎么办
# crash触发后其他路径是否需要记录 比如说A点crash再back到A 这样的
# 异常处理函数的封装

# TODO agree and check还应该更多地被调用
# bug出现在 最福利 wx9dd74b84028b139b

if __name__ == "__main__":
    #explorer=Explorer("alipay") 
    #explorer.scanner_run(['2019042664330096'])
    explorer=Explorer("wechat")
    # 笔试助手
    # explorer.scanner_run(['wxefcbda7b1df5ebd5'])
    # 国务院
    # explorer.scanner_run(['wxbebb3cdd9b331046'])
    # 还真能跑完 效果不错
    # 华瑞信息通 不太行
    # explorer.scanner_run(['wx1e509a21cb19ed71'])
    # 国人健康馆 卡住了
    # explorer.scanner_run(['wx883df31d58c3b39e'])
    # 更新微信 又寄一个
    # explorer.scanner_run(['wxa4e40ba0bd541792'])
    # 泰州通
    # explorer.scanner_run(['wxcc01b7a3072b7d07'])
    # 大鱼师傅 破APP 调用没有 用黄博的话说 这勾八是啥
    # wx314c40cf542cafb1
    # 智广云服务 貌似没点我是个人啊 
    # 这个寄了不怪他 他这个页面是被强行拉起来的（被强行拉起来可能会损失覆盖率） 不拉又慢 可以区分一下 然后就没法点到后面的东西
    # 弹窗有点克制啊
    # wxc8665b9c61eb6ff1

    #part1
    # 壹佰金
    # explorer.scanner_run(['wxc52e2ae1254c7a0e'])
    # 快片儿 4/7
    # 登录过不去，另外很多功能都是由webview/webview实现的
    #explorer.scanner_run(['wx0284f91cda6ad7ff'],wait=2,timeout=30*60,fastmode=True)
    # 一点一看
    # 这是小游戏吧，排除掉
    # explorer.scanner_run(["wx60122994cf4e3514"])
    # 什么玩意儿，压根用不了
    # explorer.scanner_run(["wx3c53fe04617a616b"])
    # 什么玩意儿，压根用不了
    # explorer.scanner_run(["wxe9e5571aeb18e585"])
    # 暂停服务了已经
    # explorer.scanner_run(["wx8ff07420995dc908"])
    # 最福利 什么jb玩意
    # explorer.scanner_run(["wx9dd74b84028b139b"])
    # 经传多赢 4/7 触发超时了直接 wxfa9615b1b2ac027b
    # ？？？？黄博电脑是蜗牛嘛 我咋跑完了
    # 视频会卡在那 建议直接kill进程

    # import json

    # 读取JSON文件
    with open('pathct1.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 提取前60个wxappid
    top_60_wxappids = list(data.keys())[:60]

    # 打印结果
    print(top_60_wxappids)

    # explorer.scanner_run(["wxfa9615b1b2ac027b","wx9dd74b84028b139b"])
    explorer.scanner_run(top_60_wxappids)
    