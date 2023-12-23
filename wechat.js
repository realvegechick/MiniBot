function stackTraceHere(){
    var Exception = Java.use('java.lang.Exception');
    var Log = Java.use('android.util.Log');
    console.log(Log.getStackTraceString(Exception.$new()))
}
var data=null
function path(){
    var text = data.replace(/(\w+)='([^']+)'(,|\})/g, '"$1":"$2"$3');
    text = text.replace(/(\w+)=(\d+)(,|\})/g, '"$1":$2$3');
    text = text.replace(/(\w+)=''(,|\})/g, '"$1":""$2');
    text = text.replace(/(\w+)=(\d+)(,|\})/g, '"$1":"$2"$3');
    console.log(text)
}
/*function test(){
    var text="{appId='wxefcbda7b1df5ebd5', sessionId='hash=928864169&ts=1695544908731&host=&version=671097141&device=2', scene=1037, sceneNote='wxb6d22f922f37b35a:hash=928864169&ts=1695544907693&host=&version=671097141&device=2:1007', preScene=0, preSceneNote='', pagePath='pages/upload/upload.html', usedState=0, appState=1, referPagePath='null', isEntrance=0}"
    text = text.replace(/(\w+)='([^']+)'(,|\})/g, '"$1":"$2"$3');
    text = text.replace(/(\w+)=(\d+)(,|\})/g, '"$1":$2$3');
    text = text.replace(/(\w+)=''(,|\})/g, '"$1":""$2');
    console.log(text)
}*/
function jump(appid,path=null) {
    var str
    if(path){
        str='{"appId":"'+appid+'","path":"'+path+'"}'
    }
    else{
        str='{"appId":"'+appid+'"}'
    }
    Java.choose("com.tencent.mm.plugin.appbrand.jsapi.o",{
		onMatch: function(instance) {
            instance.invokeHandler("navigateToMiniProgram", str, 9999)
		},
		onComplete: function() {}
	});
};
Java.perform(function(){
    var String=Java.use("java.lang.String")
    var log=Java.use('com.tencent.mm.sdk.platformtools.Log')
    
    log.i.overload('java.lang.String', 'java.lang.String').implementation=function(arg1,arg2){
        if(String.$new(arg2).contains(String.$new("pagePath"))&&String.$new(arg1).contains(String.$new("Report.kv_"))){
            //stackTraceHere()
            data=arg2.substring(arg2.indexOf(String.$new("{")))
            //console.log(arg2)
        }
        return this.i(arg1,arg2)
    }
})
