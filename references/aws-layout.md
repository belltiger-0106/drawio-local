# AWS構成図の配置と表現

## 境界を先に決める

必要な境界だけを描く。基本の包含関係は「AWSアカウント → リージョン → VPC → AZ → サブネット → 配置されるリソース」。実際の配置が分からないものを、見た目の都合でサブネットに入れない。

- VPCは複数AZをまたげる。1つのサブネットは1つのAZに属する。
- EC2などは対象サブネット内に置く。サブネットのPublic/Privateはルーティングの性質であり、枠名だけで外部接続を保証しない。
- Route 53とCloudFrontは、通常リージョン枠・VPC枠の外側に置く。
- S3、DynamoDBなどのリージョンサービスをサブネット内の常駐ノードとして描かない。VPC endpointがある場合は、その接続経路を別に示す。
- Lambdaは通常VPCの外側に置く。VPC接続がある場合は接続先サブネットとの関係を示し、実行環境がEC2と同様にそのサブネットへ直接配置されると誤読させない。
- ALBは選択した複数サブネットに関連するリソース。単一AZ専用と誤読されないよう、VPC直下の論理ノードにして対象AZ・サブネットを注記するか、関係を明示する。入口用ALBか内部ALBかを区別する。
- RDSは指定された配置方式を使う。Multi-AZ構成とRead Replicaを混同しない。方式不明なら主従・同期線を推測せず「配置方式は未指定」とする。
- NAT Gatewayは配置サブネットを示す。Internet GatewayはVPC境界に関連付ける。主通信に不要なら無理に図へ追加しない。
- IAM、監視、ログ収集は通信データ経路と区別する。CloudWatchを業務リクエストの直列経路へ挿入しない。

ここにない機能や構成は外部へ調べに行かず、提供されたローカル資料を優先する。分からない仕様を断定しない。

## 情報量と配置

主な読み順は左から右、または上から下に統一する。境界を表す枠と実処理を表すサービスを見分けられるようにする。

| 要素 | 推奨する表現 |
|---|---|
| アカウント・リージョン | 細い中立色の枠。識別名は左上 |
| VPC | 緑系の枠。名前と、分かる場合だけCIDR |
| AZ | 同じ大きさの列または行。未指定なら論理名AZ-A、AZ-B |
| Public subnet | 淡い緑系。必ず文字でもPublicと明示 |
| Private subnet | 淡い青系。必ず文字でもPrivateと明示 |
| AWSサービス | 幅・高さ64〜80の組み込みアイコン。下にサービス名と役割を2〜3行 |
| AWSデータストア | RDS、DynamoDB、S3など対応する組み込みアイコン。汎用円柱で代用しない |
| 構成上の仮定 | 図の下部の注記。サービスの仕様と混同しない |

座標は10または20の倍数を基本にする。枠の上部は見出し用に40以上、左右下は24以上の余白を確保する。ノード間は40以上、接続線の通り道には追加の余白を取る。文字が長い場合は縮小よりも改行・幅の調整・ページ分割を優先する。

## 接続の意味

- 主処理は実線の矢印。必要に応じて `HTTPS`、`SQL`、`イベント送信` などの意味を付ける。
- 関連付け・監視・ログなどは破線にし、図中に凡例を置く。
- 往復を表すためだけに反対向きの矢印を重ねない。依頼で必要なら双方向線にする。
- セキュリティグループ、DNS、認証、通信経路を同じ種類の線として混在させない。
- 境界と接続先の正確さに加え、各AWSサービスに対応する組み込みアイコンを使う。サービス名だけの基本図形で完成扱いにしない。

## 組み込みAWSアイコンを使う

AWSサービスには組み込みアイコンを必ず使う。外部からの取得や画像の同梱は不要。導入済みdraw.ioが持つ図形識別子をXMLのstyleから参照する。下の確認済み対応表から選べるサービスについては、ローカル資材を毎回解析する必要はない。

表にないサービスの確認手段はローカルの図形パレット、利用者が保存した既存図、導入先の読み取り可能なリソース。パレット操作のためにMCPを使わない。アーカイブの解析のために新しいパッケージを入れない。識別子やstyleを推測して大量に並べない。

次の識別子は、ローカルのdraw.io Desktop 32.6.10の同梱リソースで確認したもの。アイコンデータや実装コードは同梱していない。描画時に欠落が見つかった場合は導入済み版の識別子をローカルで確認し、指定を修正する。単に描画未確認という理由で基本図形に戻さない。

| サービス | shape | resIcon |
|---|---|---|
| EC2 | mxgraph.aws4.resourceIcon | mxgraph.aws4.ec2 |
| Lambda | mxgraph.aws4.resourceIcon | mxgraph.aws4.lambda |
| RDS | mxgraph.aws4.resourceIcon | mxgraph.aws4.rds |
| DynamoDB | mxgraph.aws4.resourceIcon | mxgraph.aws4.dynamodb |
| S3 | mxgraph.aws4.resourceIcon | mxgraph.aws4.s3 |
| CloudFront | mxgraph.aws4.resourceIcon | mxgraph.aws4.cloudfront |
| Route 53 | mxgraph.aws4.resourceIcon | mxgraph.aws4.route_53 |
| ALB | mxgraph.aws4.application_load_balancer | 指定しない |
| NAT Gateway | mxgraph.aws4.nat_gateway | 指定しない |
| Internet Gateway | mxgraph.aws4.internet_gateway | 指定しない |

### サービスアイコンのstyle

`resourceIcon` は背景とサービス記号を組み合わせる図形なので `resIcon` を省略しない。EC2の例：

```text
shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;fillColor=#ED7100;strokeColor=#FFFFFF;gradientColor=none;html=0;whiteSpace=wrap;aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;align=center;spacingTop=6;fontColor=#232F3E;fontSize=14;
```

サービス固有shapeのALBの例：

```text
shape=mxgraph.aws4.application_load_balancer;fillColor=#8C4FFF;strokeColor=none;html=0;whiteSpace=wrap;aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;align=center;spacingTop=6;fontColor=#232F3E;fontSize=14;
```

矩形のstyleに重ね書きして同じキーを重複させず、アイコン用styleとして組み立てる。アイコンは64〜80程度の正方形にする。EC2/LambdaなどのComputeはオレンジ系、RDS/DynamoDBは青系、S3は緑系、ネットワーク系は紫系を基本にし、白い記号が白背景に消えないようにする。

アイコンの下にラベル領域を確保する。長い名称・役割は別のプレーンテキストの `mxCell` にして幅を取り、矢印はラベルではなくアイコンのセルへ接続する。コンテナの高さは図形とラベルの両方が収まる大きさにする。

同梱サンプルの `alb`、`ec2-a`、`ec2-b` を実例として使う。構造検査では、この3セルを `--require-aws-icons alb ec2-a ec2-b` で指定する。実際の図ではすべてのAWSサービスノードを対象にする。

未掲載アイコンをローカルでも特定できない場合は、該当サービスをまとめて利用者に確認する。明示的な基本図形の指定がある場合だけ代用し、通常の生成では矩形への自動切り替えを行わない。
