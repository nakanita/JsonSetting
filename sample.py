# -*- coding: utf-8 -*-
"""Sample for JsonSetting

* JsonSettingの動作確認サンプル

"""

from JsonSetting import JsonSetting
from datetime import datetime


def test(me: JsonSetting) -> None:

    now = datetime.now()
    dict = me.set("date", me.date2str(now))
    dict = me.set("dat[3]", "Oooo!")
    dict = me.set("dat[5]", "5555go!")
    print(dict)

    pathkey = "/path/to[3]/the/key"
    value = "Hoge"
    dict = me.set(pathkey, value)
    print(dict)

    pathkey = "/path/to[5]/app/data"
    dict = me.set(pathkey, "Next!")
    print(dict)

    pathkey = "/path/to[2]/hooo"
    dict = me.set(pathkey, "Wooo")
    print(dict)

    print(me.get("/dat"))
    print(me.get("/dat[5]"))
    print(me.get("/path/to[5]/app"))
    print(me.get("/path/to[5]"))


if __name__ == '__main__':

    me = JsonSetting()
    me.load("test1.json", create_new=True)
    test(me)
    me.save("test1.json")

    json_str = '''\
    {
        "key1" : ["a1", "a2", [1, 2, 3], "a3"],
        "key2" : {"key2-1" : "val2-2"}
    }
    '''
    me.loads(json_str)
    me.save("test2.json")
