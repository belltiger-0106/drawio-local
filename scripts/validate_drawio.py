#!/usr/bin/env python3
"""Read-only validation of the small, offline XML profile used by drawio-local.

This is not a general draw.io importer. Compressed pages, object wrappers,
HTML labels, images and custom XML extensions are deliberately unsupported.
Only Python's standard library is required. No network or subprocess is used.
"""

import argparse
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


ATTRIBUTES = {
    "mxfile": {"host", "modified", "agent", "version", "type", "pages", "compressed", "etag"},
    "diagram": {"id", "name"},
    "mxGraphModel": {
        "dx", "dy", "grid", "gridSize", "guides", "tooltips", "connect", "arrows",
        "fold", "page", "pageScale", "pageWidth", "pageHeight", "math", "shadow",
        "background", "adaptiveColors",
    },
    "root": set(),
    "mxCell": {
        "id", "value", "style", "vertex", "edge", "parent", "source", "target",
        "connectable", "visible", "collapsed",
    },
    "mxGeometry": {"x", "y", "width", "height", "relative", "as"},
    "mxPoint": {"x", "y", "as"},
    "Array": {"as"},
}
CHILDREN = {
    "mxfile": {"diagram"}, "diagram": {"mxGraphModel"},
    "mxGraphModel": {"root"}, "root": {"mxCell"},
    "mxCell": {"mxGeometry"}, "mxGeometry": {"mxPoint", "Array"},
    "Array": {"mxPoint"}, "mxPoint": set(),
}
STYLE_KEYS = set("""
shape rounded arcSize absoluteArcSize whiteSpace html fillColor gradientColor
gradientDirection strokeColor strokeWidth dashed dashPattern opacity fillOpacity
strokeOpacity fontColor fontSize fontFamily fontStyle align verticalAlign
labelPosition verticalLabelPosition spacing spacingTop spacingRight spacingBottom
spacingLeft labelBackgroundColor labelBorderColor rotation direction flipH flipV
shadow glass perimeter perimeterSpacing startSize horizontal swimlaneLine
container collapsible childLayout recursiveResize resizeParent resizeLast
connectable movable resizable editable deletable cloneable autosize overflow
pointerEvents boundedLbl aspect fixedAspect resIcon outlineConnect
edgeStyle rounded orthogonalLoop jettySize orthogonal curved endArrow endFill
endSize startArrow startFill startSize entryX entryY entryDx entryDy entryPerimeter
exitX exitY exitDx exitDy exitPerimeter sourcePerimeterSpacing targetPerimeterSpacing
elbow noEdgeStyle routingCenterX routingCenterY segment
""".split())
SHAPES = {
    "rectangle", "ellipse", "rhombus", "triangle", "hexagon", "cylinder",
    "cylinder3", "swimlane", "parallelogram", "trapezoid", "actor", "cloud",
    "line", "text", "label", "note", "process", "step", "cross", "document",
    "partialRectangle", "umlFrame", "cube", "folder", "internalStorage",
}
EXTERNAL = re.compile(r"(?i)(?:https?|ftps?|file|data|javascript|vbscript):|(?:^|[\s=\"'])//|\\\\")
HTML = re.compile(r"</?[A-Za-z][^>]*>")
IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]+$")
AWS_SHAPE = re.compile(r"^mxgraph\.aws4\.[A-Za-z0-9_]+$")
AWS_RESOURCE_ICON = "mxgraph.aws4.resourceIcon"


class InvalidDiagram(Exception):
    pass


def require(condition, message):
    if not condition:
        raise InvalidDiagram(message)


def number(element, attribute, default=None, positive=False):
    raw = element.get(attribute, default)
    require(raw is not None, f"{element.tag}: {attribute} がありません")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise InvalidDiagram(f"{element.tag}: {attribute}={raw!r} は数値ではありません") from None
    require(math.isfinite(value), f"{element.tag}: {attribute} は有限値にしてください")
    if positive:
        require(value > 0, f"{element.tag}: {attribute} は正の値にしてください")
    return value


def check_tree(element):
    require(element.tag in ATTRIBUTES, f"未対応の要素: {element.tag!r}")
    unknown = set(element.attrib) - ATTRIBUTES[element.tag]
    require(not unknown, f"{element.tag}: 未対応の属性 {', '.join(sorted(unknown))}")
    require(not (element.text or "").strip(), f"{element.tag}: テキスト本文は使用できません（非圧縮XMLのみ）")
    require(not (element.tail or "").strip(), f"{element.tag}: 要素外のテキストは使用できません")
    for key, value in element.attrib.items():
        require(not EXTERNAL.search(value), f"{element.tag}.{key}: URL・外部参照・埋込データは使用できません")
        require(not HTML.search(value), f"{element.tag}.{key}: HTMLは使用できません")
    for child in element:
        require(child.tag in CHILDREN[element.tag], f"{element.tag} 内に {child.tag!r} は置けません")
        check_tree(child)


def check_style(cell):
    properties = {}
    for entry in cell.get("style", "").split(";"):
        if not entry:
            continue
        require("=" in entry, f"セル {cell.get('id')}: 名前付きスタイルは未対応です")
        key, value = entry.split("=", 1)
        require(key in STYLE_KEYS, f"セル {cell.get('id')}: 未対応のスタイル {key!r}")
        require(key not in properties, f"セル {cell.get('id')}: スタイル {key!r} が重複しています")
        properties[key] = value
    require(properties.get("html") == "0", f"セル {cell.get('id')}: style に html=0 が必要です")
    if "shape" in properties:
        shape = properties["shape"]
        require(shape in SHAPES or AWS_SHAPE.fullmatch(shape), f"セル {cell.get('id')}: 未対応の shape {shape!r}")
    if "resIcon" in properties:
        require(AWS_SHAPE.fullmatch(properties["resIcon"]) and properties["resIcon"] != AWS_RESOURCE_ICON, f"セル {cell.get('id')}: resIcon はresourceIcon以外のローカルAWS図形IDにしてください")
    if properties.get("shape") == AWS_RESOURCE_ICON:
        require("resIcon" in properties, f"セル {cell.get('id')}: shape={AWS_RESOURCE_ICON} にはAWS図形の resIcon が必要です")
    return properties


def check_required_aws_icons(root, requested_ids):
    """Check explicitly identified service nodes; do not infer services from labels.

    The AWS namespace is checked here. Existence in the installed draw.io
    library must be confirmed locally by the diagram author.
    """
    candidates = {}
    qualified = {}
    for page in root:
        for cell in page[0][0]:
            cell_id = cell.get("id")
            qualified_id = f"{page.get('id')}/{cell_id}"
            qualified[qualified_id] = cell
            candidates.setdefault(cell_id, []).append(qualified_id)
    for requested in requested_ids:
        if "/" in requested:
            matches = [requested] if requested in qualified else []
        else:
            matches = candidates.get(requested, [])
        require(matches, f"AWSアイコン必須セル {requested!r} が存在しません")
        require(len(matches) == 1, f"AWSアイコン必須セル {requested!r} は複数ページで曖昧です。page-id/cell-id で指定してください: {', '.join(matches)}")
        qualified_id = matches[0]
        cell = qualified[qualified_id]
        require(cell.get("vertex") == "1", f"AWSアイコン必須セル {qualified_id!r} はvertexである必要があります")
        properties = check_style(cell)
        shape = properties.get("shape", "")
        require(AWS_SHAPE.fullmatch(shape), f"AWSアイコン必須セル {qualified_id!r}: shape に mxgraph.aws4.* の組み込み図形が必要です")
        # check_style already requires a distinct AWS resIcon for resourceIcon.


def ancestors(cell_id, cells):
    result = []
    current = cells[cell_id].get("parent")
    while current is not None:
        require(current not in result, f"セル {cell_id}: 親参照が循環しています")
        require(current in cells, f"セル {cell_id}: 親 {current!r} が存在しません")
        result.append(current)
        current = cells[current].get("parent")
    return result


def check_geometry(cell):
    geometry = list(cell)
    require(len(geometry) == 1, f"セル {cell.get('id')}: mxGeometry が1個必要です")
    geometry = geometry[0]
    require(geometry.get("as") == "geometry", f"セル {cell.get('id')}: mxGeometry に as=geometry が必要です")
    number(geometry, "x", "0")
    number(geometry, "y", "0")
    if cell.get("vertex") == "1":
        require(geometry.get("relative", "0") == "0", f"セル {cell.get('id')}: 相対ポートは未対応です。親の座標系でx/yを指定してください")
        number(geometry, "width", positive=True)
        number(geometry, "height", positive=True)
        require(not list(geometry), f"セル {cell.get('id')}: vertex の追加geometry要素は未対応です")
    else:
        require(geometry.get("relative") == "1", f"辺 {cell.get('id')}: mxGeometry に relative=1 が必要です")
        for dimension in ("width", "height"):
            if dimension in geometry.attrib:
                number(geometry, dimension)
        used = set()
        for child in geometry:
            child_as = child.get("as")
            require(child_as not in used, f"辺 {cell.get('id')}: geometry の {child_as!r} が重複しています")
            used.add(child_as)
            if child.tag == "Array":
                require(child_as == "points", f"辺 {cell.get('id')}: Array は as=points のみ対応します")
                for point in child:
                    require("as" not in point.attrib, f"辺 {cell.get('id')}: waypoint に as は不要です")
                    number(point, "x")
                    number(point, "y")
            else:
                require(child_as == "offset", f"辺 {cell.get('id')}: mxPoint はラベルoffsetのみ対応します")
                number(child, "x")
                number(child, "y")


def check_page(page):
    require(len(page) == 1, "diagram に mxGraphModel が1個必要です")
    model = page[0]
    require(len(model) == 1, "mxGraphModel に root が1個必要です")
    for name in ("dx", "dy"):
        if name in model.attrib:
            number(model, name)
    for name in ("gridSize", "pageScale", "pageWidth", "pageHeight"):
        if name in model.attrib:
            number(model, name, positive=True)
    require(model.get("math", "0") == "0", "数式レンダリングは未対応です（math=0）")
    cells = {}
    for cell in model[0]:
        cell_id = cell.get("id", "")
        require(IDENTIFIER.fullmatch(cell_id), f"不正なセルID: {cell_id!r}")
        require(cell_id not in cells, f"セルID {cell_id!r} が重複しています")
        cells[cell_id] = cell
    require("0" in cells and "1" in cells, "ルートセル0と既定レイヤー1が必要です")
    require(cells["0"].attrib == {"id": "0"} and len(cells["0"]) == 0, "セル0は id=0 のみ指定してください")
    require(cells["1"].attrib == {"id": "1", "parent": "0"} and len(cells["1"]) == 0, "セル1は id=1、parent=0 のみ指定してください")
    for cell_id, cell in cells.items():
        if cell_id in {"0", "1"}:
            continue
        vertex = cell.get("vertex") == "1"
        edge = cell.get("edge") == "1"
        require(vertex != edge, f"セル {cell_id}: vertex=1 または edge=1 の一方が必要です")
        require(not (vertex and "edge" in cell.attrib) and not (edge and "vertex" in cell.attrib), f"セル {cell_id}: vertex/edge属性を併記しないでください")
        parent = cell.get("parent")
        require(parent in cells and parent != "0", f"セル {cell_id}: 有効な親セルまたはレイヤー1を指定してください")
        require(parent == "1" or cells[parent].get("vertex") == "1", f"セル {cell_id}: 辺を親にはできません")
        ancestors(cell_id, cells)
        check_style(cell)
        check_geometry(cell)
        if vertex:
            require("source" not in cell.attrib and "target" not in cell.attrib, f"セル {cell_id}: vertex に source/target は指定できません")
        else:
            for endpoint in ("source", "target"):
                target = cell.get(endpoint)
                require(target in cells and cells[target].get("vertex") == "1", f"辺 {cell_id}: {endpoint} は存在するvertexを参照してください")
    for cell_id, cell in cells.items():
        if cell.get("edge") == "1":
            source_parents = ancestors(cell.get("source"), cells)
            target_parents = ancestors(cell.get("target"), cells)
            common = next(item for item in source_parents if item in target_parents)
            require(cell.get("parent") == common, f"辺 {cell_id}: parent は両端の最も近い共通祖先 {common!r} にしてください")
    return len(cells) - 2


def validate(path, required_aws_icons=None):
    data = path.read_bytes()
    try:
        xml = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise InvalidDiagram("UTF-8形式で保存してください") from None
    require(not re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", xml, re.I), "DTD・ENTITYは使用できません")
    declaration = re.match(r"<\?xml\s+[^?]*\?>", xml)
    if declaration:
        encoding = re.search(r"encoding\s*=\s*['\"]([^'\"]+)['\"]", declaration[0])
        require(not encoding or encoding[1].lower() in {"utf-8", "utf8"}, "XML宣言のencodingはUTF-8にしてください")
        remainder = xml[declaration.end():]
    else:
        remainder = xml
    require("<?" not in remainder, "XML宣言以外の処理命令は使用できません")
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as error:
        raise InvalidDiagram(f"XML構文エラー: {error}") from None
    require(root.tag == "mxfile", "最上位要素は mxfile にしてください")
    check_tree(root)
    require(root.get("compressed", "false") == "false", "非圧縮XMLのみ対応します（compressed=false）")
    require(len(root) > 0, "diagram が1個以上必要です")
    if "pages" in root.attrib:
        require(root.get("pages") == str(len(root)), "mxfile.pages と実際のページ数が一致しません")
    page_ids = set()
    total = 0
    for page in root:
        page_id = page.get("id", "")
        require(IDENTIFIER.fullmatch(page_id), f"不正なページID: {page_id!r}")
        require(page_id not in page_ids, f"ページID {page_id!r} が重複しています")
        page_ids.add(page_id)
        require(page.get("name", "").strip(), f"ページ {page_id}: name が必要です")
        try:
            total += check_page(page)
        except InvalidDiagram as error:
            raise InvalidDiagram(f"ページ {page_id}: {error}") from None
    if required_aws_icons:
        check_required_aws_icons(root, required_aws_icons)
    return data, len(root), total


def main():
    parser = argparse.ArgumentParser(description="drawio-local専用の非圧縮・ローカルXMLを読み取り専用で検証します。汎用draw.ioファイルは対象外です。")
    parser.add_argument("files", nargs="+", type=Path, help="検証対象の.drawio/.xmlファイル")
    parser.add_argument("--same", action="store_true", help="指定した2個以上のファイルがバイト単位で一致することも検査")
    parser.add_argument("--require-aws-icons", nargs="+", metavar="ID", help="各ファイルの指定セルにAWS組み込み図形を要求。複数ページでは page-id/cell-id を使用。ファイル名はこのオプションより前に指定")
    args = parser.parse_args()
    if args.same and len(args.files) < 2:
        parser.error("--same には2個以上のファイルが必要です")
    failed = False
    valid = []
    for path in args.files:
        try:
            data, pages, cells = validate(path, args.require_aws_icons)
            valid.append((path, data))
            print(f"OK: {path} ({pages}ページ、{cells}セル)")
        except (OSError, InvalidDiagram) as error:
            failed = True
            print(f"ERROR: {path}: {error}", file=sys.stderr)
    if args.same and not failed:
        reference_path, reference = valid[0]
        for path, data in valid[1:]:
            if data != reference:
                failed = True
                print(f"ERROR: {path} と {reference_path} はバイト単位で一致しません", file=sys.stderr)
        if not failed:
            print("OK: 指定したファイルの内容はバイト単位で一致しています")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
