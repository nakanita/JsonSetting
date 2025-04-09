# -*- coding: utf-8 -*-
"""JsonSetting

* Jsonファイルに保存した設定を読み書きするためのユーティリティ.
* Json形式の設定を "/path/to/array[3]/key" のようなパス指定でset,getできる.
* (２重以上の配列には対応していない)

"""

import json
import re
import typing
from datetime import datetime


class JsonSetting:
    """JsonSetting class

    Json設定クラス本体

    """

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self):
        self.dic = {}   # 辞書本体
        self.sep = '/'  # パスの区切り文字
        self.idxpat = re.compile(r'(.+)\[\s*([0-9]*)\s*\]$')  # 配列の添え字パターン
        # Note: ２重以上の配列には対応していない

    def parse_path(self, pathkey: str) -> typing.Tuple[list, str]:
        """parse_path

        パスを区切り文字で分割する

        Args:
            pathkey (str): "/path/to/key" のようなパス指定文字列

        Returns:
            (list,str): パス部分のリスト["path","to"] と、最後のキー"key" の組

        Raises:
            ValueError: 引数pathkeyが空の場合に発生

        """
        lst = pathkey.split(self.sep)
        lst = [item for item in lst if item not in ('', None)]
        # 空文字列やNoneを除く。先頭の'/'はあっても無くても同じことになる

        if len(lst) == 0:  # キーが空となった
            raise ValueError(
                "The path key was empty, pathkey=\"{}\"".format(pathkey))

        path_lst = lst[:-1]     # パス部を切り出す
        last_key = lst[-1]      # 最後の１個がキーとなる
        return (path_lst, last_key)

    # 配列パターンに適合するかどうか調べる
    def index_match(self, key: str) -> typing.Any:
        """index_match

        キーとなる文字列が"array[3]" のようなパターンであるかどうか調べて、
        タグ "array" とインデックス [3] に分解する。

        Args:
            key (str): "array[3]" のようなパターンの文字列

        Returns:
            Any: 配列パターンであれば (tag, index) の組を、配列パターンでなければFalseを返す

        Raises:
            ValueError: 添え字が空だった場合に発生

        """
        result = re.match(self.idxpat, key)
        if result:
            (keytag, idx) = result.groups()
            if len(idx) > 0:
                idx = int(idx)  # 添え字は整数を期待している
            else:  # 添え字が空だった場合は例外とする
                raise ValueError("The index was empty, key=\"{}\"".format(key))
            return (keytag, idx)
        else:
            return False

    def dig_subdic_set(self, dic: dict, item: str) -> dict:
        """dig_subdic_set

        パスをたどって掘り下げる。
        setメソッドから呼ばれている。

        Args:
            dic (dict): 現在着目している辞書
            item (str): 現在キーとなっている文字列

        Returns:
            dict: 現在のパスの先にある辞書（無ければ新規に空の辞書が作成される）

        Note:
            もし該当するキーが無ければ、新たに作成する。
            配列の長さが足りなければ、必要な長さを補う。

        """
        # 配列形式にマッチするか？
        keyindex = self.index_match(item)
        if keyindex:  # 配列であった
            (keytag, idx) = keyindex
            # キーが無ければ
            if keytag not in dic:
                # 新たに十分な長さの配列を作成する
                sublist = [None] * (idx + 1)
                sublist[idx] = {}   # 新たな辞書を作る
                dic[keytag] = sublist
            else:  # 既にあったなら
                sublist = dic[keytag]
                # 長さが足りなかったら延長する
                if len(sublist) <= idx:
                    sublist.extend([None] * ((idx+1) - len(sublist)))
                    sublist[idx] = {}   # 延長した先に新たな辞書を作る

            if sublist[idx] is None:    # まだ辞書ができていなかった
                sublist[idx] = {}

            return sublist[idx]   # いま得られた辞書を次の対象とする

        else:  # 配列形式ではなかった
            # キーが無ければ
            if item not in dic:
                # 新たに空の辞書を作成する
                dic[item] = {}

            return dic[item]

    def set_last_value(self, dic: dict, last_key: str, value) -> None:
        """set_last_value

        最後のキーに値を設定する
        setメソッドから呼ばれている

        Args:
            dic (dict): パスの最後にある、値を設定すべき辞書
            item (str): キーとなる文字列
            value (Any): 設定したい値

        Returns:
            None: 無し

        Note:
            もし該当するキーが無ければ、新たに作成する。
            配列の長さが足りなければ、必要な長さを補う。

        """
        # 配列形式にマッチするか？
        keyindex = self.index_match(last_key)
        if keyindex:  # 配列であった
            (keytag, idx) = keyindex
            # キーが無ければ
            if keytag not in dic:
                # 新たに十分な長さの配列を作成する
                sublist = [None] * (idx + 1)
            else:  # 既にあったなら
                sublist = dic[keytag]
                # 長さが足りなかったら延長する
                if len(sublist) <= idx:
                    sublist.extend([None] * ((idx+1) - len(sublist)))
            sublist[idx] = value   # リストに値を設定する
            dic[keytag] = sublist  # 辞書にリストを設定する
        else:
            dic[last_key] = value   # 辞書に値を設定する

    # 値をセットする
    def set(self, pathkey: str, value) -> dict:
        """set

        パス設定で指定された場所に、値をセットする

        Args:
            pathkey (str): パス設定文字列
            value (Any): 設定したい値

        Returns:
            None: 設定後の辞書 = self.dic

        """
        (path_lst, last_key) = self.parse_path(pathkey)

        # パスを再帰的にたどる
        subdic = self.dic
        for item in path_lst:
            subdic = self.dig_subdic_set(subdic, item)

        self.set_last_value(subdic, last_key, value)

        return self.dic  # 返り値は設定した辞書

    # パスをたどって掘り下げる
    # getメソッドから呼ばれている
    def dig_subdic_get(self, dic: dict, item: str) -> typing.Any:
        """dig_subdic_get

        パスをたどって掘り下げる。
        getメソッドから呼ばれている。

        Args:
            dic (dict): 現在着目している辞書
            item (str): 現在キーとなっている文字列

        Returns:
            Any: 取得されたオブジェクト、辞書または配列。無ければNone。

        Raises:
            ValueError: 配列の範囲を超えた場合に発生

        """
        # 配列形式にマッチするか？
        keyindex = self.index_match(item)
        if keyindex:  # 配列であった
            (keytag, idx) = keyindex
            sublist = dic[keytag]
            if len(sublist) <= idx:
                raise ValueError(
                    "The index out of range, key=\"{}\"".format(item))
            retval = sublist[idx]
        # キーが無ければNoneを返す
        elif dic is None:
            return None
        elif item not in dic:
            return None
        else:  # キーがあって配列で無ければ、辞書の値を返す
            retval = dic[item]
        return retval

    def get_last_value(self, dic: dict, last_key: str) -> typing.Any:
        """get_last_value

        最後のキーの値を読み出す
        getメソッドから呼ばれている

        Args:
            dic (dict): パスの最後にある、値を読み出したい辞書
            item (str): キーとなる文字列

        Returns:
            Any: 読み出された値

        Raises:
            ValueError: 配列の範囲を超えた場合に発生

        """
        # 配列形式にマッチするか？
        keyindex = self.index_match(last_key)
        if keyindex:  # 配列であった
            (keytag, idx) = keyindex
            # キーが無ければ
            if keytag not in dic:
                return None
            else:  # 既にあったなら
                sublist = dic[keytag]
                # 長さが足りなかったら例外
                if len(sublist) <= idx:
                    raise ValueError(
                        "The index out of range, key=\"{}\"".format(last_key))
            return sublist[idx]
        else:
            return dic[last_key]

    def get(self, pathkey: str) -> typing.Any:
        """get

        パス設定で指定された場所の値を読み出す

        Args:
            pathkey (str): パス設定文字列

        Returns:
            Any: 読み出された値

        """
        (path_lst, last_key) = self.parse_path(pathkey)

        # パスを再帰的にたどる
        subdic = self.dic
        for item in path_lst:
            subdic = self.dig_subdic_get(subdic, item)

        if subdic is None:
            return None   # 配列の中のNone要素に当たった場合、ここに来る

        return self.get_last_value(subdic, last_key)

    def load(self, fname: str, create_new: bool = False) -> dict:
        """load

        Jsonで書かれた設定ファイルを読み込む

        Args:
            fname (str): Json設定ファイルへのパス名
            create_new (bool): Trueに設定すると、ファイルが無かった場合エラーとならず、空の設定を作る。

        Returns:
            dict: 読み込まれた辞書 = self.dic

        """
        try:
            f = open(fname, 'r')
        except OSError as e:
            if create_new:  # 新規作成フラグがTrueなら
                pass    # 何もしない
            else:
                raise   # そのまま上に投げる
        else:
            self.dic = json.load(f)
            f.close()

        return self.dic

    def loads(self, jstr: str) -> dict:
        """load

        Json形式の文字列を、辞書に設定する。

        Args:
            jstr (str): Json形式の文字列

        Returns:
            dict: 設定された辞書 = self.dic

        """
        self.dic = json.loads(jstr)
        return self.dic

    def save(self, fname: str) -> None:
        """save

        現在の設定をJsonファイルに保存する

        Args:
            fname (str): Json設定ファイルへのパス名

        Returns:
            None: 無し

        """
        f = open(fname, 'w')
        json.dump(self.dic, f, ensure_ascii=False, indent=2)
        f.close()

    def date2str(self, dt_obj: datetime) -> str:
        """date2str

        datetimeオブジェクトを、Jsonで用いる日付文字列に変換する

        Args:
            dt_obj (datetime): 日付時刻

        Returns:
            str: Jsonで用いる日付文字列

        """
        return dt_obj.strftime(self.DATE_FORMAT)

    def str2date(self, dt_str: str) -> datetime:
        """str2date

        Jsonで用いる日付文字列を、datetimeオブジェクトに変換する

        Args:
            dt_str (str): Jsonで用いる日付文字列

        Returns:
            datetime: 日付時刻

        """
        return datetime.strptime(dt_str, self.DATE_FORMAT)
