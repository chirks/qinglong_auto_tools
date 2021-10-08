#作者仓库:https://github.com/spiritLHL/qinglong_auto_tools
#觉得不错麻烦点个star谢谢

#根据主青龙的启用任务和对应脚本同步到副青龙中去，不存在于副青龙中的任务和对应脚本会自动新增，如果启用的任务对应的脚本内容有更新，也会同步更新

#只同步更新主青龙中已经启用的任务和对应脚本

'''
cron: 1
new Env('二叉树同步脚本文件');
'''

#在脚本管理里修改这个文件的配置，然后保存，然后禁用 二叉树同步脚本文件 这个任务，有需要再点运行


# 主青龙，需要修改任务的容器，事先需要在容器里创建应用，给所有权限，然后重启容器，应用设置才会生效，
cilent_id1=""
cilent_secret1=""
url1 = ""

# 副青龙，被同步的任务容器，事先需要在容器里创建应用，给所有权限，然后重启容器，应用设置才会生效，
#按照格式有几个写几个，没有的空的删除
cilent_ids=['','','','']
cilent_secrets=['','','','']
urllist = ["http://xxxx:xxxx/","","",'']



import requests
import time
import json



requests.packages.urllib3.disable_warnings()


def gettimestamp():
    return str(int(time.time() * 1500))

def gettoken(self,url_token):
    r = requests.get(url_token).text
    res = json.loads(r)["data"]["token"]
    self.headers.update({"Authorization": "Bearer "+res})

def login(self, baseurl, cilent_id_temp, cilent_secret_temp):
    url_token = baseurl+'open/auth/token?client_id='+cilent_id_temp+'&client_secret='+cilent_secret_temp
    gettoken(self, url_token)

def getitem(self, baseurl, typ):
    url = baseurl + typ + "/scripts/files?t=%s" % gettimestamp()
    r = self.get(url)
    item = json.loads(r.text)["data"]
    return item

def getscript(self, baseurl, typ, filename):
    url = baseurl + typ + "/scripts/"+filename+"?t=%s" % gettimestamp()
    r = self.get(url)
    script = json.loads(r.text)["data"]
    return script

def pushscript(self, baseurl, typ, data):
    url = baseurl + typ + "/scripts?t=%s" % gettimestamp()
    self.headers.update({"Content-Type": "application/json;charset=UTF-8", 'Connection': 'close'})
    r = self.put(url, data=json.dumps(data))
    #response = json.loads(r.text)["data"]
    return r

def getcrons(self, baseurl, typ):
    url = baseurl + typ + "/crons?t=%s" % gettimestamp()
    r = self.get(url)
    item = json.loads(r.text)["data"]
    return item

def addcron(self, baseurl, typ, data):
    url = baseurl + typ + "/crons?t=%s" % gettimestamp()
    self.headers.update({"Content-Type": "application/json;charset=UTF-8", 'Connection': 'close'})
    r = self.post(url, data=json.dumps(data))
    if json.loads(r.text)["code"] == 200:
        return True
    else:
        return r.text


if __name__ == '__main__':
    #主容器
    s = requests.session()
    login(s, url1, cilent_id1, cilent_secret1)

    #获取主青龙任务
    print("=========== 主青龙 信息获取中 =============")
    print()
    ztasks = getcrons(s , url1, "open")
    zenable_list = []
    zdisable_list = []
    for i in ztasks:
        if i['isDisabled'] == 0:
            zenable_list.append(i)
        else:
            continue
    # enable_tlid = []
    zenable_tname = []
    zenable_tcommand = []
    zenable_tschedule = []
    for j in zenable_list:
        # enable_tlid.append(j['_id'])
        zenable_tname.append(j['name'])
        zenable_tcommand.append(j['command'])
        zenable_tschedule.append(j['schedule'])
    print("主青龙任务数量：{}，启用任务{}".format(len(ztasks), len(zenable_tname)))
    print()

    #获取主青龙的脚本名
    zscripts = getitem(s, url1, "open")
    zscripts_list = []
    for i in zscripts:
        zscripts_list.append(i["key"])
    print("主青龙脚本文件数量：{}".format(len(zscripts_list)))
    print()
    print()

    t = 0
    for k in urllist:
        # 分容器
        print("=========== 副青龙{} 信息获取中 =============".format(t+1))
        print()
        a = requests.session()
        login(a, urllist[t], cilent_ids[0], cilent_secrets[0])
        tasks = getcrons(a, urllist[t], "open")

        # 增加新任务
        enable_list = []
        disable_list = []
        for i in tasks:
            if i['isDisabled'] == 0:
                enable_list.append(i)
            else:
                continue
        # enable_tlid = []
        enable_tname = []
        enable_tcommand = []
        enable_tschedule = []
        for j in enable_list:
            # enable_tlid.append(j['_id'])
            enable_tname.append(j['name'])
            enable_tcommand.append(j['command'])
            enable_tschedule.append(j['schedule'])
        print("副青龙任务数量：{}".format(len(tasks)))
        print()

        print("同步任务中")
        print()

        count = 0
        ct = 0

        for i in zenable_tname:
            if zenable_tname[count] not in enable_tname and zenable_tcommand[count] not in enable_tcommand and \
                    zenable_tschedule[
                        count] not in enable_tschedule:
                data_cron = {
                    "command": zenable_tcommand[count],
                    "schedule": zenable_tschedule[count],
                    "name": zenable_tname[count]
                }
                addcron(a, urllist[t], "open", data_cron)
            else:
                ct += 1
            count += 1
        xc = count - ct
        print("新增启用任务数量：{}".format(xc))
        print()

        # 获取副青龙的脚本名
        scripts = getitem(a, urllist[t], "open")
        scripts_list = []
        for i in scripts:
            scripts_list.append(i["key"])

        # 主青龙启用的任务对应的脚本
        zscripts_enable = []
        for i in zenable_tcommand:
            if i[-2:] == "js" or i[-2:] == "py":
                zscripts_enable.append(i.replace("task ", ""))

        # 筛选需要添加或更改的脚本名
        add_list = []
        change_list = []
        for j in zscripts_enable:
            if j not in scripts_list:
                add_list.append(j)
            else:
                change_list.append(j)
        print("同步脚本文件中")
        print()

        # 查询新增脚本内容
        data_script_list = []
        for i in add_list:
            content = getscript(s, url1, "open", i)
            data_script = {
                "filename": i,
                "content": content,
            }
            data_script_list.append(data_script)

        # 写入新增内容
        for i in data_script_list:
            pushscript(a, urllist[t], "open", i)
        print("新增启用任务对应脚本文件数量：{}".format(xc))
        print()

        print("同步脚本文件中")
        print()

        # 查询需要更改的脚本内容
        change_script_list = []
        for i in change_list:
            content = getscript(s, url1, "open", i)
            data_script = {
                "filename": i,
                "content": content,
            }
            change_script_list.append(data_script)

        origin_script_list = []
        for i in change_list:
            content = getscript(a, urllist[t], "open", i)
            data_script = {
                "filename": i,
                "content": content,
            }
            origin_script_list.append(data_script)

        count = 0
        ct = 0
        while True:
            if count <= (len(change_script_list) - 1):
                if change_script_list[count] != origin_script_list[count]:
                    pushscript(a, urllist[t], "open", change_script_list[count])
                    print("更新脚本文件  {}".format(change_script_list[count]["filename"]))
                else:
                    ct += 1
                count += 1
            else:
                break
        print()

        print("同步脚本文件完毕")

    print('========= 副青龙{} 同步信息完毕 ============='.format(t+1))
    print()

    t +=1









