# Json設定ユーティリティ・JsonSetting

Json設定ファイルに、パス形式の文字列によって値を読み書きするユーティリティ.

- パス形式の文字列の例:  
    "/path/to/arr[3]/key"  
    このパス形式文字列は  
    　　{ path: {to: {arr: [None, None, {key: value } ] } } }  
    と解釈されます。

## Environment

- Python version: 3.8.18

## Requirement

- json: 2.0.9

## Installation

適当なディレクトリ(utilなど)にコピーし、importして用いてください。

## Usage

```python
me = JsonSetting()

# Jsonファイルの読み込み（無ければ無視して空からスタート)
me.load("setting.json", create_new=True)

# 値の設定
me.set("/path/to[3]/the/key", "MyValue")

# 値の読み出し
result = me.get("/path/to[3]/the/key")

# 設定の保存
me.save("setting.json")
```

## History

- 2024/11/15    とりあえず動く版。

## Note

- 配列は１次元まで。２次元以上の配列には未対応です。

## Author

* 中西@Motion
