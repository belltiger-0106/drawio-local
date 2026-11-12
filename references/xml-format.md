# XML形式とレイアウト

## 出力する文書

非圧縮の `mxfile` を使う。`.drawio` と `.xml` は拡張子だけが異なる同一内容にする。次は2つのノードと接続線を持つ最小例。文章やコードフェンスはファイルに含めない。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="Electron" compressed="false">
  <diagram id="page-overview" name="構成概要">
    <mxGraphModel grid="1" gridSize="10" page="1" pageScale="1" pageWidth="1200" pageHeight="800" background="#FFFFFF">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="client" value="利用者" style="rounded=1;whiteSpace=wrap;html=0;fillColor=#F1F5F9;strokeColor=#64748B;fontColor=#0F172A;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="60" y="100" width="160" height="80" as="geometry" />
        </mxCell>
        <mxCell id="service" value="サービス" style="rounded=1;whiteSpace=wrap;html=0;fillColor=#FFF4DF;strokeColor=#B7791F;fontColor=#0F172A;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="340" y="100" width="160" height="80" as="geometry" />
        </mxCell>
        <mxCell id="request" value="HTTPS" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;endArrow=block;endFill=1;strokeColor=#334155;fontColor=#0F172A;fontSize=12;labelBackgroundColor=#FFFFFF;" edge="1" parent="1" source="client" target="service">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 構造上の規則

- 各ページは別の `diagram` とし、ページIDを一意にする。各ページの `root` に `id="0"` と `id="1" parent="0"` を置く。
- `root` 直下に全 `mxCell` を並べる。包含はXMLの入れ子でなく `parent` 属性で表現する。`object` ラッパーや独自要素はこのスキルでは使用しない。
- ノードと枠は `vertex="1"`、線は `edge="1"`。1つのセルに両方を付けない。
- ノードに `mxGeometry` を1つ持たせる。`x`、`y` は親からの位置、`width`、`height` は正の有限値。`as="geometry"` を必ず指定する。
- 線に `source` と `target`、`mxGeometry relative="1" as="geometry"` を持たせる。接続先IDを実在するノードに限定する。
- 線の `parent` は両ノードの親系統を比較し、最も近い共通祖先を選ぶ。例：同じサブネット内ならそのサブネット、別AZなら通常VPC、VPC外とVPC内ならその両方を包む枠。既定レイヤーしか共有しなければ `1`。
- 接続線の折れ点は線の親を基準にした座標。ノードのローカル座標をそのまま別の親の線に使わない。
- 根以外の全セルが、存在する親を介して `0` に到達すること。自己参照や循環を作らない。
- コンテナ自体を接続先にせず、その中の実際の接続対象を指定する。所属は枠と包含で表現する。

## 枠・ラベル・線

背景の枠には、例えば次のstyleを使う。ノードより先に定義し、配色は薄くする。

```text
rounded=0;container=1;collapsible=0;recursiveResize=0;whiteSpace=wrap;html=0;verticalAlign=top;align=left;spacingTop=8;spacingLeft=12;fillColor=#F8FAFC;strokeColor=#94A3B8;fontColor=#0F172A;fontSize=15;fontStyle=1;
```

親の見出し領域に子を重ねない。構造検査は見出しとの衝突や実際の文字幅まで判定しないため、座標と画像も確認する。

ラベルは `html=0`。改行にはXML属性中の `&#10;` を使う。`&`、`<`、`>`、引用符はXMLライブラリでエスケープする。HTMLの `<br>` や `&nbsp;` を挿入しない。日本語はUTF-8で保存し、外部Webフォントは使わない。

直交線を基本とする。図形を横切る線には余白、接続面、折れ点を調整する。接続面はstyleの `exitX=1;exitY=0.5;entryX=0;entryY=0.5;` などで指定できる。折れ点が必要な場合は次の形式を使う。

```xml
<mxGeometry relative="1" as="geometry">
  <Array as="points">
    <mxPoint x="240" y="160" />
    <mxPoint x="240" y="300" />
  </Array>
</mxGeometry>
```

## 外部依存を作らない

出力にはリンク属性、画像セル、SVGの埋め込み、Data URI、URL参照、カスタムJavaScript、外部XML実体、DOCTYPE、HTMLラベルを含めない。XML宣言以外の処理命令も含めない。図形は矩形・円柱などの基本図形、またはローカルで確認した組み込みの名前付き図形を使う。

同梱検査スクリプトはこの制限付き形式を検査する。未知の機能を含む既存ファイルのエラーは、draw.io全体で無効だという意味ではない。検査を通すために既存の内容を無言で落とさない。

## ローカル描画

図の生成・構造検査・2ファイルの保存にdraw.ioアプリの起動は不要。目視確認を行う場合だけ、既存アプリのローカルエクスポートを使用する。アプリ自身のバックグラウンド通信までこのスキルで強制遮断することはできない。ネットワーク遮断が必要な環境では、既に通信を制限した実行環境でのみ起動し、設定変更はしない。

Windowsでは `Get-Command draw.io -ErrorAction SilentlyContinue` と次の候補を確認する。

```text
C:\Program Files\draw.io\draw.io.exe
C:\Program Files (x86)\draw.io\draw.io.exe
%LOCALAPPDATA%\Programs\draw.io\draw.io.exe
```

見つからなければ利用者から渡されたパス、またはアンインストール情報の `InstallLocation` を読み取る。全ドライブの無制限な走査、アプリのダウンロード、PATHの書き換えはしない。macOSではアプリ内の実行ファイル、Linuxでは導入済みの `drawio` を使用する。WSLの場合はLinuxとWindowsのパス表記を混ぜず、Windows実行ファイルにはWindows形式の入力・出力パスを渡す。

導入済み版が対応するCLIをローカルのヘルプやリソースで確認してから実行する。基本のエクスポート指定は次のとおり。

```powershell
& $drawioExe --export --format png --output $previewPath $sourcePath
```

作成時にローカル確認したDesktop 32.6.10では、`--disable-update`（自動更新の停止）、`--timeout 30`（30秒）、`--theme light`、`--border 16` も使用できる。`--disable-update` は全通信を遮断する機能ではない。別の版では対応状況を確認する。

ここで各変数は確認済みの絶対パスとする。空白を含むパスを1つの引数として渡す。複数ページでは、導入済み版の `--page-index` が1始まりであることを確認し、各ページを別の一時画像に出力する。未確認の自動レイアウトや更新抑止オプションを推測して指定しない。

処理にタイムアウトを設け、終了コードだけでなく、新しい出力ファイルの存在・サイズ・画像内容を確認する。既存のGUIセッションは終了しない。GPU関連の失敗時は、その版で対応する `--disable-gpu` を追加して1回だけ再試行できる。それでも失敗したら構造検査結果とともに未確認点を報告する。

## 納品前の確認項目

1. 要求されたリソース、境界、接続がそろい、推測が注記されている。
2. XMLが解釈でき、ID・親・接続先・有限な座標・辺の共通祖先が正しい。
3. 外部参照、画像、HTMLラベルを含まない。
4. 各要素が親枠内に収まり、ラベルが読める。線と図形が不用意に重ならない。
5. `.drawio` と `.xml` が存在し、最終修正後のバイト列が一致する。
6. 実施した検査と未実施の目視確認を区別して報告できる。
