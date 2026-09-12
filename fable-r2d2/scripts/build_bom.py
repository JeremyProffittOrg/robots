"""Build bom/bill-of-materials.xlsx from the CSV sources with live totals and source links.

Inputs: bom/electronics.csv, bom/hardware.csv (columns: reference, quantity, item,
part_number, supplier, url, unit_usd, price_basis, notes) and bom/printed-parts.csv
(written by scripts/export_cad.py) plus cad/h2d-slice-check.json for filament mass.
Output: bom/bill-of-materials.xlsx with sheets Summary, Electronics, Hardware, Printed
parts, Filament, Sources. Formulas compute line and sheet totals so the operator can edit
quantities or prices in Excel and see totals update.
"""
import csv
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "bom/bill-of-materials.xlsx"
HEAD_FILL = PatternFill("solid", fgColor="1F3A5F")
HEAD_FONT = Font(bold=True, color="FFFFFF")
TOTAL_FONT = Font(bold=True)
THIN = Side(style="thin", color="B8C2CC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
COLUMNS = ["reference", "quantity", "item", "part_number", "supplier", "url", "unit_usd", "price_basis", "notes"]
TITLES = ["Ref", "Qty", "Item", "Part number", "Supplier", "Source URL", "Unit USD", "Price basis", "Notes / use"]


def read_csv(name):
    path = ROOT / "bom" / name
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def style_header(sheet, titles):
    for col, title in enumerate(titles, 1):
        cell = sheet.cell(row=1, column=col, value=title)
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        cell.border = BORDER
    sheet.freeze_panes = "A2"
    sheet.row_dimensions[1].height = 30


def purchased_sheet(book, title, rows):
    sheet = book.create_sheet(title)
    style_header(sheet, TITLES + ["Line USD"])
    for index, row in enumerate(rows, 2):
        for col, key in enumerate(COLUMNS, 1):
            value = row.get(key, "")
            if key == "quantity":
                value = int(float(value)) if value else 0
            elif key == "unit_usd":
                value = float(value) if value else 0.0
            cell = sheet.cell(row=index, column=col, value=value)
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=key in ("item", "notes"))
            if key == "url" and value:
                cell.hyperlink = value
                cell.font = Font(color="0B5394", underline="single")
            if key == "unit_usd":
                cell.number_format = "$#,##0.00"
        line = sheet.cell(row=index, column=len(COLUMNS) + 1, value=f"=B{index}*G{index}")
        line.number_format = "$#,##0.00"
        line.border = BORDER
    total_row = len(rows) + 2
    sheet.cell(row=total_row, column=3, value="Sheet total").font = TOTAL_FONT
    total = sheet.cell(row=total_row, column=len(COLUMNS) + 1, value=f"=SUM(J2:J{total_row - 1})")
    total.number_format = "$#,##0.00"
    total.font = TOTAL_FONT
    widths = [8, 6, 34, 20, 14, 46, 10, 12, 52, 11]
    for col, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(col)].width = width
    return sheet, total_row


def printed_sheet(book, rows, slices):
    sheet = book.create_sheet("Printed parts")
    titles = ["STL file", "Qty", "Material", "Mirror for 2nd", "X mm", "Y mm", "Z mm", "Solid mass g (bound)",
              "Sliced mass g (H2D, incl. support)", "Sliced time h", "Orientation", "Notes"]
    style_header(sheet, titles)
    by_part = {Path(r["part"]).stem: r for r in slices.get("rows", [])}
    for index, row in enumerate(rows, 2):
        sliced = by_part.get(row["part"], {})
        values = [f"stl/{row['part']}.stl", int(row["quantity"]), row["material"],
                  "yes" if str(row.get("mirror_for_second", "")).lower() == "true" else "no",
                  float(row["x_mm"]), float(row["y_mm"]), float(row["z_mm"]), float(row["solid_mass_g"]),
                  round(float(sliced.get("predicted_mass_g", 0)), 1), float(sliced.get("predicted_time_h", 0)),
                  row.get("orientation", ""), row.get("notes", "")]
        for col, value in enumerate(values, 1):
            cell = sheet.cell(row=index, column=col, value=value)
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=col >= 11)
    total_row = len(rows) + 2
    sheet.cell(row=total_row, column=1, value="Totals (qty x per-part)").font = TOTAL_FONT
    sheet.cell(row=total_row, column=9, value=f"=SUMPRODUCT(B2:B{total_row - 1},I2:I{total_row - 1})").font = TOTAL_FONT
    sheet.cell(row=total_row, column=10, value=f"=SUMPRODUCT(B2:B{total_row - 1},J2:J{total_row - 1})").font = TOTAL_FONT
    for col, width in enumerate([24, 6, 10, 12, 9, 9, 9, 14, 16, 12, 30, 60], 1):
        sheet.column_dimensions[get_column_letter(col)].width = width
    return sheet, total_row


def filament_sheet(book, rows, slices):
    sheet = book.create_sheet("Filament")
    style_header(sheet, ["Material", "Sliced mass g (qty applied)", "Spools of 1 kg (with 25 % waste)", "Spool USD", "Cost USD", "Source"])
    by_part = {Path(r["part"]).stem: r for r in slices.get("rows", [])}
    materials = {}
    for row in rows:
        mass = float(by_part.get(row["part"], {}).get("predicted_mass_g", 0)) * int(row["quantity"])
        materials[row["material"]] = materials.get(row["material"], 0) + mass
    prices = {"PETG": (24.99, "https://us.store.bambulab.com/products/petg-hf"),
              "PETG-CF": (34.99, "https://us.store.bambulab.com/products/petg-cf"),
              "PLA": (19.99, "https://us.store.bambulab.com/products/pla-basic")}
    for index, (material, mass) in enumerate(sorted(materials.items()), 2):
        price, url = prices.get(material, (25.0, ""))
        sheet.cell(row=index, column=1, value=material)
        sheet.cell(row=index, column=2, value=round(mass, 1))
        sheet.cell(row=index, column=3, value=f"=ROUNDUP(B{index}*1.25/1000,0)")
        sheet.cell(row=index, column=4, value=price).number_format = "$#,##0.00"
        sheet.cell(row=index, column=5, value=f"=C{index}*D{index}").number_format = "$#,##0.00"
        link = sheet.cell(row=index, column=6, value=url)
        if url:
            link.hyperlink = url
            link.font = Font(color="0B5394", underline="single")
    total_row = len(materials) + 2
    sheet.cell(row=total_row, column=1, value="Total").font = TOTAL_FONT
    sheet.cell(row=total_row, column=5, value=f"=SUM(E2:E{total_row - 1})").number_format = "$#,##0.00"
    for col, width in enumerate([12, 24, 30, 12, 12, 50], 1):
        sheet.column_dimensions[get_column_letter(col)].width = width
    return sheet, total_row


def sources_sheet(book, electronics, hardware):
    sheet = book.create_sheet("Sources")
    style_header(sheet, ["Supplier", "Items", "URLs"])
    suppliers = {}
    for row in electronics + hardware:
        entry = suppliers.setdefault(row["supplier"], {"items": [], "urls": set()})
        entry["items"].append(row["item"])
        if row.get("url"):
            entry["urls"].add(row["url"])
    for index, (supplier, entry) in enumerate(sorted(suppliers.items()), 2):
        sheet.cell(row=index, column=1, value=supplier)
        sheet.cell(row=index, column=2, value="; ".join(entry["items"])).alignment = Alignment(wrap_text=True, vertical="top")
        sheet.cell(row=index, column=3, value="\n".join(sorted(entry["urls"]))).alignment = Alignment(wrap_text=True, vertical="top")
    for col, width in enumerate([22, 70, 70], 1):
        sheet.column_dimensions[get_column_letter(col)].width = width


def main():
    electronics = read_csv("electronics.csv")
    hardware = read_csv("hardware.csv")
    printed = read_csv("printed-parts.csv")
    slices = json.loads((ROOT / "cad/h2d-slice-check.json").read_text(encoding="utf-8")) if (ROOT / "cad/h2d-slice-check.json").exists() else {}
    book = Workbook()
    summary = book.active
    summary.title = "Summary"
    _, e_total = purchased_sheet(book, "Electronics", electronics)
    _, h_total = purchased_sheet(book, "Hardware", hardware)
    printed_sheet(book, printed, slices)
    _, f_total = filament_sheet(book, printed, slices)
    sources_sheet(book, electronics, hardware)
    summary["A1"] = "fable-r2d2 bill of materials"
    summary["A1"].font = Font(bold=True, size=14)
    summary["A2"] = "Prices are list prices read from supplier pages on the date in the notes; tax and shipping excluded. Edit quantities or unit prices on the sheets; totals are formulas."
    summary["A2"].alignment = Alignment(wrap_text=True)
    summary.merge_cells("A2:C2")
    summary.row_dimensions[2].height = 45
    lines = [("Electronics", f"=Electronics!J{e_total}"), ("Mechanical hardware", f"=Hardware!J{h_total}"),
             ("Filament", f"=Filament!E{f_total}"), ("Grand total (USD)", "=SUM(B4:B6)")]
    for offset, (label, formula) in enumerate(lines):
        row = 4 + offset
        summary.cell(row=row, column=1, value=label).font = TOTAL_FONT if offset == 3 else Font()
        cell = summary.cell(row=row, column=2, value=formula)
        cell.number_format = "$#,##0.00"
        if offset == 3:
            cell.font = TOTAL_FONT
    summary["A9"] = "Printed pieces"
    summary["B9"] = f"=SUM('Printed parts'!B2:B{len(printed) + 1})"
    summary["A10"] = "Unique STL files"
    summary["B10"] = len(printed)
    summary["A11"] = "Sliced filament mass, g"
    summary["B11"] = f"='Printed parts'!I{len(printed) + 2}"
    summary["A12"] = "Sliced print time, h"
    summary["B12"] = f"='Printed parts'!J{len(printed) + 2}"
    summary.column_dimensions["A"].width = 28
    summary.column_dimensions["B"].width = 18
    summary.column_dimensions["C"].width = 60
    OUT.parent.mkdir(exist_ok=True)
    book.save(OUT)
    print(f"PASS: {OUT} with {len(electronics)} electronics rows, {len(hardware)} hardware rows, {len(printed)} printed parts")


if __name__ == "__main__":
    main()
