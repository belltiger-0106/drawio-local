# drawio-local

Claude CodeでAWS構成図を作成するためのローカル処理用スキルです。編集可能なdraw.io XMLを直接生成し、同一内容の `.drawio` と `.xml` を保存します。

## 特徴

- AWSアカウント・リージョン・VPC・AZ・サブネットの境界と通信経路を表現。
- 図の作成時に外部サイト、外部API、MCP、オンライン変換を使用しない。
- 共有URLを生成せず、ローカルファイルとして納品。
- Python標準ライブラリだけでXML構造と2ファイルの一致を検査。
- 基本図形だけで動作。AWSアイコンを使う場合も、導入済みdraw.ioの組み込み識別子を参照。

「ローカル」は図の参照・生成・検証・保存処理の範囲です。Claude Code本体のモデル通信をオフライン化する機能ではありません。draw.io Desktopの通信を強制遮断する機能もありません。

## 配置方法

このリポジトリを取得し、`SKILL.md` と補助フォルダーを、対象プロジェクトの次の場所へ配置してください。リポジトリの取得後、スキル実行時にネットワークから追加資材を取得する必要はありません。

```text
<project>/
└── .claude/
    └── skills/
        └── drawio-local/
            ├── SKILL.md
            ├── references/
            ├── scripts/
            └── examples/
```

図のXML生成に追加パッケージは不要です。同梱検査スクリプトには導入済みのPython 3を使用します。目視確認には導入済みのdraw.io Desktopを任意で使用できます。

## 使用例

Claude Codeで、次のように依頼します。

```text
/drawio-local AWSのWebアプリ構成図を作成してください。
インターネット向けALBを2AZのPublic subnetに関連付け、
各AZのPrivate subnetにEC2を1台配置してください。
ALBから各EC2へHTTPSで接続し、DBは配置しません。
アカウント・リージョン・VPC・AZ・サブネットの境界を示し、
diagrams/aws-web.drawio と diagrams/aws-web.xml に保存してください。
```

保存先の指定がなければ、現在のプロジェクトの `diagrams/` を使用します。未指定のCIDRやリージョンなどを確定情報として補わず、図中に前提を記載します。

## 内容

| ファイル | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | Claude Codeが使用するスキル本体 |
| [AWS配置ガイド](references/aws-layout.md) | サービスの配置・境界・線の意味 |
| [XML形式ガイド](references/xml-format.md) | XML構造・レイアウト・ローカル描画 |
| [検査スクリプト](scripts/validate_drawio.py) | 構造検査とバイト単位の一致確認 |
| [サンプル.drawio](examples/aws-web.drawio) | 基本図形による2AZのAWS構成例 |
| [サンプル.xml](examples/aws-web.xml) | サンプル.drawioと同一内容のXML |

サンプルはdraw.io Desktop 32.6.10で描画・目視確認済みです。アイコン画像や図形ライブラリの実装コードは同梱していません。

## サンプルの検査

リポジトリのルートで実行します。

```text
python -X utf8 scripts/validate_drawio.py examples/aws-web.drawio examples/aws-web.xml --same
```

macOSやLinuxでコマンド名が `python3` の場合は読み替えてください。追加のPythonパッケージは不要です。

検査は本スキルが生成する非圧縮XML形式が対象です。圧縮ページ、HTMLラベル、画像、独自拡張を含む一般のdraw.ioファイルには対応していません。また、文字の重なりやAWS構成の意味的な正しさは、構造検査だけでは判定しません。
