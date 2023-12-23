
import xml.dom.minidom
import simhash
from PIL import *


def get_sim_hash(root):
    return simhash.Simhash("".join([node.getAttribute("text") for node in root.getElementsByTagName("node")]))

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

def find_leaf_nodes(node):
    leaf_nodes=[]
    if node.nodeType == xml.dom.minidom.Node.ELEMENT_NODE and len(node.childNodes) == 0:
        leaf_nodes.append(node)
    for child in node.childNodes:
        leaf_nodes.extend(find_leaf_nodes(child))
    return leaf_nodes


# 求一个node的hash，此处用bounds作为标记
def node_hash(node):
    return node.getAttribute("bounds")


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

def get_box(s):
    p1,p2=s[1:-1].split("][")
    x1,y1=[int(i) for i in p1.split(",")]
    x2,y2=[int(i) for i in p2.split(",")]
    return (x1,y1,x2,y2)

if __name__ == "__main__":
    pass