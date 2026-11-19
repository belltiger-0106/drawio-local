# AWSの境界・グループ

AWSアカウント、リージョン、VPC、AZ、サブネットの囲みには、`shape=mxgraph.aws4.group` を使う。サービスのアイコンを囲みの代わりに拡大したり、基本矩形・swimlaneで代用したりしない。タイトル、凡例、注記、AWS外の利用者はこの対象に含めない。

ここに記載する識別子・色・線種は、ローカルのdraw.io Desktop 32.6.10に同梱されたAWS Groupsパレットで確認したもの。図形実装・ステンシル・画像は同梱しない。スタイルは端末にインストール済みの図形を参照するだけであり、外部から取得しない。

## 確認済みの対応表

全行の `shape` は `mxgraph.aws4.group`。`grIcon` はサービス用の `resIcon` と別のキーなので混同しない。

| 境界 | grIcon | 枠・アイコンの色 | 塗り | 線・枠の設定 |
|---|---|---|---|---|
| AWSアカウント | `mxgraph.aws4.group_account` | `#CD2264` | `none` | `dashed=0;grStroke=1;` |
| リージョン | `mxgraph.aws4.group_region` | `#00A4A6` | `none` | `dashed=1;grStroke=1;` |
| VPC | `mxgraph.aws4.group_vpc2` | `#8C4FFF` | `none` | `dashed=0;grStroke=1;` |
| Availability Zone | 指定しない | `#147EBA` | `none` | `dashed=1;grStroke=1;` |
| Public subnet | `mxgraph.aws4.group_security_group` | `#7AA116` | `#F2F6E8` | `dashed=0;grStroke=0;` |
| Private subnet | `mxgraph.aws4.group_security_group` | `#00A4A6` | `#E6F6F7` | `dashed=0;grStroke=0;` |

Public/Private subnetは同じ `group_security_group` の識別子を使う。識別子の名前からSecurity Groupリソースに読み替えず、ラベルと色でサブネットを表す。`grStroke=0` はAWSパレットに合わせた塗りの境界で、外周の線を描かない。`strokeColor` はこの場合も左上のアイコンに使われる。

**AZの扱い:** 確認したAWS GroupsパレットのAvailability Zoneは、専用 `shape` と `grIcon` を指定しない通常の矩形だった。このスキルでは、その青色・破線を保ち、今回の要件に合わせて組み込みAWSの `group` に統一する。これは専用の「AWS AZアイコン」ではない。存在しない `group_availability_zone` などを作らない。`mxgraph.aws4.group` は `grIcon` がないときも枠を描けるため、アイコンを省略すればよい。

## スタイル例

次の共通部分と、各タイプの部分を連結して `mxCell` の `style` に設定する。共通部分は図としての見やすさと本スキルのプレーンテキスト出力方針に合わせた値であり、パレットのコードの転載ではない。

```text
shape=mxgraph.aws4.group;outlineConnect=0;gradientColor=none;html=0;whiteSpace=wrap;fontSize=16;fontStyle=1;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;verticalAlign=top;align=left;spacingTop=10;
```

AWSアカウント:

```text
grIcon=mxgraph.aws4.group_account;grIconSize=25;grStroke=1;strokeColor=#CD2264;fillColor=none;fontColor=#CD2264;dashed=0;spacingLeft=36;
```

リージョン:

```text
grIcon=mxgraph.aws4.group_region;grIconSize=25;grStroke=1;strokeColor=#00A4A6;fillColor=none;fontColor=#147EBA;dashed=1;spacingLeft=36;
```

VPC:

```text
grIcon=mxgraph.aws4.group_vpc2;grIconSize=25;grStroke=1;strokeColor=#8C4FFF;fillColor=none;fontColor=#6D38B8;dashed=0;spacingLeft=36;
```

VPCの文字色は、白背景で読める濃い紫に調整している。元パレットの文字色 `#AAB7B8` をそのまま使う必要はない。枠の色と図形識別子は対応表に合わせる。

AZ（`grIcon` を追加しない）:

```text
grStroke=1;strokeColor=#147EBA;fillColor=none;fontColor=#147EBA;dashed=1;spacingLeft=14;
```

Public subnet:

```text
grIcon=mxgraph.aws4.group_security_group;grIconSize=25;grStroke=0;strokeColor=#7AA116;fillColor=#F2F6E8;fontColor=#248814;dashed=0;spacingLeft=36;
```

Private subnet:

```text
grIcon=mxgraph.aws4.group_security_group;grIconSize=25;grStroke=0;strokeColor=#00A4A6;fillColor=#E6F6F7;fontColor=#147EBA;dashed=0;spacingLeft=36;
```

## 親子構造と余白

- 単なる重ね描きではなく、子セルの `parent` に実際のグループのIDを指定する。一般的な包含順は、AWSアカウント → リージョン → VPC → AZ → サブネット → EC2等のリソース。必要な境界だけを作り、既存の構成事実は変えない。
- 子セルの座標は親グループの左上を原点とする。`group` にはswimlaneのヘッダーのような自動的な本文領域の補正がない。ヘッダーの下に50～60程度、左右に30程度の余白を取り、明示的に配置する。
- 左上のグループアイコンは既定25角。`grIconSize=25`、`spacingLeft=36` とすると、アイコンと見出しが重なりにくい。アイコンを大きくする場合は見出しと子セルの余白も増やす。AZはアイコンを持たないため左余白を14程度にできる。
- サービスアイコンの下に別のラベルセルを置く場合、そのラベルまで親の内側に収める。下端でラベルが切れるときはグループを広げる。
- 入れ子の境界と同じ幅の巨大なサービスアイコンを作らない。グループにサービス用 `resIcon` を設定しない。
- 接続線は両端を包含する最も内側の共通親に所属させる。ヘッダー・左上アイコン・サービスラベルを横切らず、AZ間などの空白を経路に使う。
- ALBのように複数サブネットに関連付く単一の論理リソースは、VPCに置き、関連先をラベルや注記で示せる。見た目の都合で同じALBを2個に増やさない。

## ローカル確認と検証

確認元は、インストール先の `resources/app.asar` 内にある `drawio/src/main/webapp/js/app.min.js` の `addAWS4GroupsPalette` と、`drawio/src/main/webapp/js/shapes-14-6-5.min.js` のAWS group登録。将来のバージョンでパスが変わった場合も、ローカルの同梱ファイルだけを調べる。確認できない識別子を推測せず、基本矩形へ黙って置き換えない。

検証では、XMLの構文・ID・親子関係に加え、AWS境界の `shape`、`grIcon`、ヘッダー余白を確認する。ローカルPNGプレビューが使えるときは、左上アイコンとラベル、破線、サブネットの塗り、サービスへの接続が表示されることを目視確認する。

同梱サンプルの境界9セルとサービス3セルを、スキルのルートで検査する例：

```text
python -X utf8 scripts/validate_drawio.py examples/aws-web.drawio examples/aws-web.xml --same --require-aws-icons alb ec2-a ec2-b --require-aws-groups account region vpc az-a az-b public-a private-a public-b private-b
```

実際の図では全サービスと全AWS境界のIDに置き換える。`--require-aws-groups` は汎用矩形への置換、サービス図形の流用、`container=1` の欠落を検出する。境界種別ごとの `grIcon` と色が適切かどうかは、この対応表との照合も行う。複数ページで同じセルIDを使うときは `page-id/cell-id` 形式にする。
