class Test(object):
    def __init__(self,name1):
        self.name = name1
    
    def nameprint(self):
        print(self.name)

if __name__ == "__main__":
    classlist = dict()
    t = Test("yamamoto")
    classlist["yamamoto"] = t
    t = Test("tanaka")
    classlist["tanaka"] = t
    t = Test("ojijan")
    classlist["ojijan"] = t

    name = "tanaka"
    classlist[name].nameprint()

    print(classlist)
