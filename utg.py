import os
import json
def draw_utg(json_file_path):
    """
    Output current UTG to a js file
    """
    # 输出为html的table
    def list_to_html_table(ClassObj):
        
        table = "<table class=\"table\">\n"
        for key, value in ClassObj.items():
            table += "<tr><th>%s</th><td>%s</td></tr>\n" % (key, value)
        table += "</table>"
        return table
    # 后期封装输出文件的路径

    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    stateList = data["List"]
    statePath = data["Path"]
    base_info = data["base_info"]
    utg_file_path = os.path.join("./output_dir", "utg.js")
    utg_file = open(utg_file_path, "w")
    utg_nodes = []
    utg_edges = []
    for state in stateList:
        utg_node = {
            "id": state["page_path"]+"_"+state["section"],
            "shape": "image",
            # 需要给我img的路径和名称，建议到时维护在state数据结构中
            "image": '.'+state["screenshot"],
            "label": state["page_path"],
            
            "title": list_to_html_table(state),
        }
        
        # 原代码中还标注了第一个和最后一个，这段先不急
        # --------------------------------------
        # if state.state_str == self.first_state_str:
        #     utg_node["label"] += "\n<FIRST>"
        #     utg_node["font"] = "14px Arial red"
        # if state.state_str == self.last_state_str:
        #     utg_node["label"] += "\n<LAST>"
        #     utg_node["font"] = "14px Arial red"
        # --------------------------------------

        utg_nodes.append(utg_node)

    for idx in range(len(statePath)):
        path = statePath[idx]
        from_state = path["start_State"]
        to_state = path["end_State"]

        utg_edge = {
            "from": from_state,
            "to": to_state,
            "id": from_state + "-->" + to_state,
            "title": list_to_html_table(path),
            "label": idx,
            "path": {
                # 不知道这字段干嘛的
                # "path_str": event_str,
                "path_id": idx,
                "path_trigger": path["trigger"],
                # 给我img的路径
                "view_images": '.'+path["pic_name"],
                "bound":path["bound"]
            }
        }

        # # Highlight last transition
        # if state_transition == self.last_transition:
        #     utg_edge["color"] = "red"

        utg_edges.append(utg_edge)

    utg = {
        "nodes": utg_nodes,
        "edges": utg_edges,

        "appid":base_info["appid"],
        "crash_flag":base_info["crash_flag"],
        "crash_info":base_info["crash_info"],
        "dif_page_path_num": base_info["dif_page_path_num"],
        "first_run_page_path_num": base_info["first_run_page_path_num"],
        "whole_page_path_num": base_info["whole_page_path_num"],
        "map_density_first": base_info["map_density_first"],
        "map_density_all": base_info["map_density_all"]

        # 下面的内容全是关于小程序的基本信息
        # 对应修改 网页droidbotUI.js文件中第83行开始


        # "num_nodes": len(utg_nodes),
        # "num_edges": len(utg_edges),
        # "num_effective_events": len(self.effective_event_strs),
        # "num_reached_activities": len(self.reached_activities),
        # "test_date": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        # "time_spent": (datetime.datetime.now() - self.start_time).total_seconds(),
        # "num_transitions": self.num_transitions,

        # "device_serial": self.device.serial,
        # "device_model_number": self.device.get_model_number(),
        # "device_sdk_version": self.device.get_sdk_version(),

        # "app_sha256": self.app.hashes[2],
        # "app_package": self.app.package_name,
        # "app_main_activity": self.app.main_activity,
        # "app_num_total_activities": len(self.app.activities),
    }

    utg_json = json.dumps(utg, indent=2)
    utg_file.write("var utg = \n")
    utg_file.write(utg_json)
    utg_file.close()
    return 

if __name__ == "__main__":
    draw_utg("./formatted_data.json")
    #draw_utg("./wx8e1527ae16f0e930/utg.json")
    