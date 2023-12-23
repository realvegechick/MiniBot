import subprocess,time,json
process_name={"wechat":"微信","alipay":"支付宝"}
class Frida:
    def __init__(self,superapp):
        self.superapp=superapp
        self.process=None
        self.log=open("frida.log",'a')
        self.connect()
        

    def __del__(self):
        self.process.stdin.write(b"exit\n")
        self.log.write(self.process.stdout.read().decode('gbk'))
        self.process.wait()
    
    def recv(self,str):
        if self.process==None:
            return None
        data=b''
        while str not in data:
            data+=self.process.stdout.read(1)
            if b'Failed' in data or b'terminate' in data:
                raise Exception("frida异常结束",data.decode())
        return data.decode('gbk')

    def connect(self):
        self.process=subprocess.Popen(["frida","-U",process_name[self.superapp],"-l","./"+self.superapp+".js"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,bufsize=0)
        self.log.write(self.recv(b"]->"))

    def getPath(self):
        self.process.stdin.write(b"path()\n")
        res=self.recv(b"]->")
        self.log.write(res)
        res=res.split("\r\n")[1]
        return json.loads(res)


    def jump(self,appid,path=None):
        if(path==None):
            self.process.stdin.write(('jump("'+appid+'")\n').encode())
        else:
            self.process.stdin.write(('jump("'+appid+'","'+path+'")\n').encode())
        res=self.recv(b"]->")
        self.log.write(res)
        time.sleep(3)
        return res
    
if __name__=='__main__':
    pass
    # f=Frida("alipay")
    # input()
    # print(f.getPath())
