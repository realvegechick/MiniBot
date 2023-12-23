import uiautomator2 as u2
import os,time,json
import xml.dom.minidom
device=u2.connect()
package={"wechat":"com.tencent.mm","alipay":"com.eg.android.AlipayGphone"}
def locate_window(superapp,node):
    open("./dump1.xml",'wb').write(node.toprettyxml().encode("utf-8"))
    if(superapp=="alipay"):
        while node.getAttribute("resource-id") != "com.alipay.mobile.nebula:id/h5_web_content":
            node=node.childNodes[0]
        return node
    if(superapp=="wechat"):#stupid fix for stupid developers
        while node.getAttribute("resource-id") != "com.tencent.mm:id/biv":
            node=node.childNodes[0]
        return node
        raise Exception("What a coincidence!")

def clear_text_node(root):
    for child in root.childNodes[:]:
        if child.nodeType == xml.dom.Node.TEXT_NODE:
            root.removeChild(child)
        elif child.nodeType == xml.dom.Node.ELEMENT_NODE:
            clear_text_node(child)
    return root

def get_miniapp_hierarchy(superapp,restart=False):
        if(restart):
            #os.system('adb shell /data/local/tmp/atx-agent server --stop')
            #os.system('adb shell /data/local/tmp/atx-agent server -d')
            device._force_reset_uiautomator_v2()
            time.sleep(1)
        #os.system('adb shell "curl http://127.0.0.1:7912/dump/hierarchy > /sdcard/hierachy.json"')
        # 为啥会卡住？？？TODO
        #os.system("adb pull /sdcard/hierachy.json ./")
        
        ui=device.dump_hierarchy()#json.loads(open("./hierachy.json",encoding='utf-8').read())["result"]
        dom=xml.dom.minidom.parseString(ui)
        root=clear_text_node(dom.documentElement)
        open("./dump0.xml",'wb').write(root.toprettyxml().encode("utf-8"))
        x=str(device.info['displayWidth'])
        y=str(device.info['displayHeight'])
        for node in root.childNodes:
            if(node.getAttribute("package")==package[superapp]):
                new_root=locate_window(superapp,node)
                open("./dump.xml",'wb').write(new_root.toprettyxml().encode("utf-8"))
                return new_root
        #os.system('adb shell /data/local/tmp/atx-agent server --stop')
        #os.system('adb shell /data/local/tmp/atx-agent server -d')
        device._force_reset_uiautomator_v2()
        time.sleep(1)
        return get_miniapp_hierarchy(superapp)

get_miniapp_hierarchy("wechat")
print("Done.")