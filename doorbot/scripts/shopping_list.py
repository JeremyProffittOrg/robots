"""Build the one list you shop from: bom/shopping-list.csv and bom/shopping-list.xlsx.

The three BOM files are organised the way the machine is built (electronics, hardware, printed
parts). This one is organised the way it is bought: grouped by supplier, one row per thing to
order, with a running total and the source link on every row. Generated from the same
bom/*.csv, so it cannot disagree with them.

    python scripts/shopping_list.py            # write both files
    python scripts/shopping_list.py --open     # write them, then open the spreadsheet
"""
import argparse
import csv
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from scad_params import ROOT, params

BOM = ROOT / "bom"

# Which supplier each vendor maps to, and the order the groups appear in.
GROUPS = [
    ("Adafruit", "adafruit.com - one cart", "Adafruit"),
    ("LilyGO", "LilyGO, AliExpress or Amazon", "LilyGO"),
    ("K&J Magnetics", "kjmagnetics.com", "K&J Magnetics"),
    ("Bambu Lab", "Bambu Lab store", "Bambu Lab"),
    ("generic", "any hardware shop or Amazon", "generic"),
]


# Where to actually buy each line. For Adafruit, K&J and Bambu Lab the product page IS the
# shop page, so the buy link is that page. The generic hardware has no single product to cite,
# so those are vendor search URLs - honest about being a search rather than a specific listing.
def search(vendor, terms):
    q = urllib.parse.quote_plus(terms)
    return {"amazon": f"https://www.amazon.com/s?k={q}",
            "aliexpress": f"https://www.aliexpress.com/w/wholesale-{q}.html",
            "mcmaster": f"https://www.mcmaster.com/products/?q={q}"}[vendor]


BUY_LINKS = {
    # sku -> (buy link, is it a search rather than a specific listing)
    "T-Display": (search("amazon", "TTGO T-Display ESP32 1.14 ST7789"), True),
    "D84": ("https://www.kjmagnetics.com/proddetail.asp?prod=D84", False),
    "dyneema-150": (search("amazon", "braided dyneema fishing line 150 lb 1.2 mm"), True),
    "dowel-4x35": (search("amazon", "4mm x 35mm steel dowel pin"), True),
    "screw-8x32": (search("amazon", "#8 x 1-1/4 in countersunk wood screw"), True),
    "screw-8x25": (search("amazon", "#8 x 1 in countersunk wood screw"), True),
    "screw-6x20": (search("amazon", "#6 x 3/4 in countersunk wood screw"), True),
    "m3x10": (search("amazon", "M3 x 10 mm self tapping screw plastic"), True),
    "m3x8": (search("amazon", "M3 x 8 mm self tapping screw plastic"), True),
    "pla-tough-plus": ("https://us.store.bambulab.com/collections/pla", True),
}


def buy_link(sku, source):
    """The link to order from, and whether it is a search rather than one listing."""
    if sku in BUY_LINKS:
        return BUY_LINKS[sku]
    if source.startswith("https://www.adafruit.com/product/"):
        return source, False        # Adafruit's product page is its shop page
    return source, False


def check(url, timeout=20):
    """Does this URL answer? Reported as measured, including when a shop blocks bots."""
    if not url:
        return "no link"
    request = urllib.request.Request(url, method="GET", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) doorbot-bom-check",
        "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return f"HTTP {response.status}"
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}"
    except Exception as e:                       # DNS, TLS, timeout
        return type(e).__name__


def read(name):
    with (BOM / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--check-links", action="store_true",
                    help="fetch every buy link and record what it answered")
    args = ap.parse_args()
    p = params()

    items = read("electronics.csv") + read("hardware.csv")
    printed = read("printed-parts.csv")

    rows = []
    for _, where, vendor in GROUPS:
        group = [i for i in items if i["vendor"] == vendor]
        for i in sorted(group, key=lambda r: -float(r["line_usd"])):
            link, is_search = buy_link(i["sku"], i["source"])
            rows.append({
                "buy from": where,
                "item": i["item"],
                "part number": i["sku"],
                "qty": int(i["quantity"]),
                "unit $": float(i["unit_usd"]),
                "line $": float(i["line_usd"]),
                "what it is for": i["why"],
                "buy link": link,
                "is search": is_search,
                "datasheet": i["source"] if i["source"] != link else "",
            })
    missing = [i["item"] for i in items
               if i["vendor"] not in {v for _, _, v in GROUPS}]
    if missing:
        raise SystemExit("no supplier group for: " + ", ".join(missing))

    if args.check_links:
        seen = {}
        for r in rows:
            url = r["buy link"]
            if url not in seen:
                seen[url] = check(url)
                print(f"  {seen[url]:<14} {url}")
            r["link check"] = seen[url]
    else:
        for r in rows:
            r["link check"] = "not checked"

    total = sum(r["line $"] for r in rows)
    pieces = sum(r["qty"] for r in rows)
    filament_g = sum(float(r["line_mass_g"]) for r in printed)

    # ---------------------------------------------------------------- CSV
    csv_path = BOM / "shopping-list.csv"
    header = ["buy from", "item", "part number", "qty", "unit $", "line $",
              "what it is for", "buy link", "link is a search", "datasheet", "link check"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["doorbot revision A - everything you need to buy"])
        w.writerow([f"{len(rows)} line items, {pieces} pieces, ${total:.2f} at prices read "
                    f"2026-09-12. Printing needs {filament_g:.0f} g of Bambu Lab PLA Tough+."])
        w.writerow(["Rows marked 'search' link to a vendor search, not one listing: those are "
                    "commodity screws, dowels and line with no single part to cite."])
        w.writerow([])
        w.writerow(header)
        current = None
        for r in rows:
            if r["buy from"] != current:
                current = r["buy from"]
                subtotal = sum(x["line $"] for x in rows if x["buy from"] == current)
                count = sum(x["qty"] for x in rows if x["buy from"] == current)
                w.writerow([])
                w.writerow([current, f"{count} pieces", "", "", "", f"{subtotal:.2f}"])
            w.writerow([r["buy from"], r["item"], r["part number"], r["qty"],
                        f"{r['unit $']:.2f}", f"{r['line $']:.2f}", r["what it is for"],
                        r["buy link"], "search" if r["is search"] else "",
                        r["datasheet"], r["link check"]])
        w.writerow([])
        w.writerow(["", "TOTAL", "", pieces, "", f"{total:.2f}"])

    # ---------------------------------------------------------------- XLSX
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Buy this"
    ink = "FF0B0F19"
    head_fill = PatternFill("solid", fgColor="FFEEF2F7")
    group_fill = PatternFill("solid", fgColor="FFDBEAFE")
    total_fill = PatternFill("solid", fgColor="FFDCFCE7")

    ws.append(["doorbot revision A - everything you need to buy"])
    ws["A1"].font = Font(bold=True, size=15, color=ink)
    ws.append([f"{len(rows)} line items, {pieces} pieces, ${total:.2f} at prices read "
               f"2026-09-12. Printing needs {filament_g:.0f} g of Bambu Lab PLA Tough+, "
               f"which the one spool below covers several times over."])
    ws["A2"].font = Font(size=10, color="FF4B5563")
    ws.append([])

    ws.append(header)
    for c in range(1, len(header) + 1):
        cell = ws.cell(row=ws.max_row, column=c)
        cell.font = Font(bold=True, color=ink)
        cell.fill = head_fill

    current = None
    for r in rows:
        if r["buy from"] != current:
            current = r["buy from"]
            subtotal = sum(x["line $"] for x in rows if x["buy from"] == current)
            count = sum(x["qty"] for x in rows if x["buy from"] == current)
            ws.append([current, f"{count} pieces", "", "", "", subtotal])
            for c in range(1, 7):
                cell = ws.cell(row=ws.max_row, column=c)
                cell.font = Font(bold=True, color=ink)
                cell.fill = group_fill
            ws.cell(row=ws.max_row, column=6).number_format = '"$"#,##0.00'
        ws.append([r["buy from"], r["item"], r["part number"], r["qty"], r["unit $"],
                   r["line $"], r["what it is for"], "", "search" if r["is search"] else "",
                   "", r["link check"]])
        row = ws.max_row
        ws.cell(row=row, column=5).number_format = '"$"#,##0.00'
        ws.cell(row=row, column=6).number_format = '"$"#,##0.00'
        for column, url, label in [(8, r["buy link"], "buy"), (10, r["datasheet"], "datasheet")]:
            if url:
                cell = ws.cell(row=row, column=column)
                cell.hyperlink = url
                cell.value = label
                cell.font = Font(color="FF1D4ED8", underline="single")

    ws.append([])
    ws.append(["", "TOTAL", "", pieces, "", total])
    for c in range(1, 7):
        cell = ws.cell(row=ws.max_row, column=c)
        cell.font = Font(bold=True, size=12, color=ink)
        cell.fill = total_fill
    ws.cell(row=ws.max_row, column=6).number_format = '"$"#,##0.00'

    for col, width in zip("ABCDEFGHIJK", [30, 46, 16, 6, 9, 9, 76, 7, 9, 11, 12]):
        ws.column_dimensions[col].width = width
    for row in ws.iter_rows(min_row=4):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=cell.column_letter == "G")
    ws.freeze_panes = "A5"

    # ---- second sheet: what the printer makes, not what you buy
    ws2 = wb.create_sheet("Print this")
    ws2.append(["Printed parts - Bambu Lab PLA Tough+, 0.2 mm layers, no supports"])
    ws2["A1"].font = Font(bold=True, size=14, color=ink)
    ws2.append([f"{len(printed)} designs, {sum(int(r['quantity']) for r in printed)} pieces, "
                f"{filament_g:.0f} g. Pause magnet_pod at the pocket roof, drop both magnets "
                f"in, let it bridge over them."])
    ws2["A2"].font = Font(size=10, color="FF4B5563")
    ws2.append([])
    ws2.append(["part", "qty", "size mm", "grams", "what it is"])
    for c in range(1, 6):
        cell = ws2.cell(row=ws2.max_row, column=c)
        cell.font = Font(bold=True, color=ink)
        cell.fill = head_fill
    for r in printed:
        ws2.append([r["part"], int(r["quantity"]),
                    f"{float(r['x_mm']):.0f} x {float(r['y_mm']):.0f} x {float(r['z_mm']):.0f}",
                    float(r["solid_mass_g"]), r["purpose"]])
    for col, width in zip("ABCDE", [20, 6, 20, 9, 92]):
        ws2.column_dimensions[col].width = width
    for row in ws2.iter_rows(min_row=4):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=cell.column_letter == "E")
    ws2.freeze_panes = "A5"

    xlsx_path = BOM / "shopping-list.xlsx"
    wb.save(xlsx_path)

    (ROOT / "docs/shopping-list.json").write_text(json.dumps(
        {"line_items": len(rows), "pieces": pieces, "total_usd": round(total, 2),
         "filament_g": round(filament_g, 1),
         "by_supplier": {where: round(sum(x["line $"] for x in rows if x["buy from"] == where), 2)
                         for _, where, _ in GROUPS},
         "links": [{"sku": r["part number"], "buy": r["buy link"],
                    "is_search": r["is search"], "check": r["link check"]} for r in rows],
         "csv": str(csv_path.relative_to(ROOT)).replace("\\", "/"),
         "xlsx": str(xlsx_path.relative_to(ROOT)).replace("\\", "/")}, indent=2))

    print(f"{len(rows)} line items, {pieces} pieces, ${total:.2f}, "
          f"{filament_g:.0f} g of PLA Tough+")
    for _, where, _ in GROUPS:
        sub = sum(x["line $"] for x in rows if x["buy from"] == where)
        n = sum(x["qty"] for x in rows if x["buy from"] == where)
        print(f"  {where:<32} {n:>3} pieces  ${sub:>7.2f}")
    print(f"  {csv_path}")
    print(f"  {xlsx_path}")

    if args.open:
        os.startfile(str(xlsx_path))  # noqa: S606 - user asked for it to be opened
        print("opened the spreadsheet")


if __name__ == "__main__":
    main()
