function stackTraceHere(){
    var Exception = Java.use('java.lang.Exception');
    var Log = Java.use('android.util.Log');
    console.log(Log.getStackTraceString(Exception.$new()))
}
var data=null

function path() {
    var match = data.match(/https:\/\/(\d+)\.hybrid.alipay-eco\.com\/index\.html#(.+)/)
    // 使用正则表达式匹配键值对
    var regex = /([^&?#]+)=([^&]+)/g;
    var matches = data.match(regex);
    var result = {"appId":match[1],"pagePath":match[2]};
    if (matches) {
    // 构建目标JSON对象
        for (var i = 0; i < matches.length; i++) {
            var keyValue = matches[i].split("=");
            var key = decodeURIComponent(keyValue[0]);
            var value = decodeURIComponent(keyValue[1]);
            result[key] = value;
        }
    // 打印转换后的JSON格式文本
    }
    var jsonText = JSON.stringify(result);
    console.log(jsonText);
};
/*function test(){
    var text = "https://2019112269337790.hybrid.alipay-eco.com/index.html#pages/index/index";
    const match = text.match(/https:\/\/(\d+)\.hybrid.alipay-eco\.com\/index\.html#(.+)/)
    // 使用正则表达式匹配键值对
    var regex = /([^&?#]+)=([^&]+)/g;
    var matches = text.match(regex);
    var result = {"appId":match[1],"pagePath":match[2]};
    if (matches) {
    // 构建目标JSON对象
    for (var i = 0; i < matches.length; i++) {
        var keyValue = matches[i].split("=");
        var key = decodeURIComponent(keyValue[0]);
        var value = decodeURIComponent(keyValue[1]);
        result[key] = value;
    }

    // 打印转换后的JSON格式文本
    var jsonText = JSON.stringify(result);
    console.log(jsonText);
    } 
    var jsonText = JSON.stringify(result);
    console.log(jsonText);
}*/

function jump(appid,path=null) {
    // 导入Frida的Java模块
    var context = Java.use('android.app.ActivityThread').currentApplication().getApplicationContext();
    var str
    if(path){
        str="alipays://platformapi/startApp?appId="+appid+"&page="+path
    }
    else{
        str="alipays://platformapi/startApp?appId="+appid
    }
    var intent = Java.use('android.content.Intent').$new('android.intent.action.VIEW', Java.use('android.net.Uri').parse(str));
    intent.setFlags(Java.use('android.content.Intent').FLAG_ACTIVITY_NEW_TASK.value)
    context.startActivity(intent);
};
Java.perform(function(){
    var String = Java.use("java.lang.String")
    var c=Java.use("com.alibaba.ariver.app.PageNode")
    c.getPageURI.implementation=function(){
        //stackTraceHere()
        var ret=this.getPageURI()
        if(ret==null) return null
        var tmp=String.$new(ret)
        if(!tmp.equals(data) && tmp.contains(String.$new("#"))){
            data=ret
        }
        return ret
    }
})
