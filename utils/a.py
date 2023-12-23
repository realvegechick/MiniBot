n,left,right=[int(i) for i in input().split(" ")]
paints=[]
for i in range(n):
    paints.append([int(i) for i in input().split(" ")])
paints=sorted(paints,key=lambda x:(x[0],x[1]))
maxn=left-1
for p in paints:
    if(maxn>=p[0]-1):
        maxn=max(maxn,p[1])
print(maxn>=right)