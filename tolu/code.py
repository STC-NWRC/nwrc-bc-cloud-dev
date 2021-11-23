def sum_ap():
    with open(argv[1],"w") as f:
        values=f.read()
    a=values.split(",")[0]
    b=values.split(",")[-1]
    n=(int(b)-int(a))+1
    result=n((2*int(argv[1]))+(n-1)*1)/2
    with open("./result.txt","w") as f: f.write(str(result))

# def createFiles():
#     start=1
#     end=101
#     for i in range(1,11):
#         values=[str(v) for v in range(start,end)]
#         with open("./docs/{}.txt".format(i),'w') as f: f.write(",".join(values))
#         start+=100
#         end+=100

def main():
    # createFiles()
    sum_ap()

if __name__ == '__main__':
    # from sys import argv
    # main()
    print("Code works!")