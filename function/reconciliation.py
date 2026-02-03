import pandas as pd
from pathlib import Path
from collections import defaultdict
import re
from openpyxl import load_workbook
from openpyxl.styles import Border, Side, Font
from openpyxl.utils import get_column_letter

# ===============================
# 路径配置
# ===============================
desktop = Path.home() / "Desktop"
data_folder = desktop / "数据汇总"
mapping_file = desktop / "编码.xlsx"

# ===============================
# 读取编码表
# ===============================
map_df = pd.read_excel(mapping_file)

code_info = {}
for _, row in map_df.iterrows():
    code = str(row["货品商家编码"])
    code_info[code] = {
        "name": str(row["名称"]),
        "type": str(row["产品类型"]),
        "price": float(row["供货价"])
    }

# ===============================
# 样式
# ===============================
thin = Side(style="thin")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
red_font = Font(color="FF0000")

# ===============================
# 处理文件
# ===============================
for file in data_folder.glob("*.xls*"):
    try:
        df = pd.read_excel(file, sheet_name="分销汇总")
        if "商家编码" not in df.columns:
            continue

        code_counter = defaultdict(int)
        unmatched_codes = set()
        missing_price_names = set()

        # ===============================
        # 解析商家编码
        # ===============================
        for cell in df["商家编码"].dropna():
            items = str(cell).split(";")
            normal_total = 0
            gift_items = []

            for item in items:
                m = re.match(r"(.+?)(?:\*(\d+))?$", item.strip())
                if not m:
                    continue

                code = m.group(1)
                qty = int(m.group(2)) if m.group(2) else 1

                info = code_info.get(code)
                if not info:
                    unmatched_codes.add(code)
                    continue

                if info["type"] == "赠品":
                    gift_items.append((code, qty))
                else:
                    normal_total += qty
                    code_counter[code] += qty

            gift_total = sum(q for _, q in gift_items)

            if normal_total == 0:
                for code, qty in gift_items:
                    code_counter[code] += qty
                continue

            extra = gift_total - normal_total
            if extra > 0:
                for code, qty in gift_items:
                    use = min(qty, extra)
                    code_counter[code] += use
                    extra -= use
                    if extra <= 0:
                        break

        # ===============================
        # 汇总到【名称】
        # ===============================
        final = {}
        for code, qty in code_counter.items():
            info = code_info[code]
            name = info["name"]
            price = info["price"]

            # 👇 供货价缺失判断
            if pd.isna(price) or price == 0:
                missing_price_names.add(name)

            if name not in final:
                final[name] = {
                    "数量": 0,
                    "供货价": price if not pd.isna(price) else ""
                }

            final[name]["数量"] += qty

        # ===============================
        # 打开 Excel
        # ===============================
        wb = load_workbook(file)
        ws = wb["分销汇总"]

        # 找「商家编码」列
        code_col = None
        for c in range(1, ws.max_column + 1):
            if ws.cell(1, c).value == "商家编码":
                code_col = c
                break
        if not code_col:
            continue

        start_col = code_col + 4  # 间隔 3 列

        # ===============================
        # 解除旧合并（关键）
        # ===============================
        for rng in list(ws.merged_cells.ranges):
            if rng.min_col >= start_col:
                ws.unmerge_cells(str(rng))

        # ===============================
        # 清空旧结果区
        # ===============================
        for r in range(1, ws.max_row + 1):
            for c in range(start_col, ws.max_column + 1):
                ws.cell(r, c).value = None
                ws.cell(r, c).border = Border()

        # ===============================
        # 表头
        # ===============================
        headers = ["分销商", "名称", "供货价", "数量", "售后处理费", "金额"]
        for i, h in enumerate(headers):
            cell = ws.cell(1, start_col + i, h)
            cell.border = border

        # ===============================
        # 列字母（一次算好）
        # ===============================
        price_col = get_column_letter(start_col + 2)
        qty_col   = get_column_letter(start_col + 3)
        fee_col   = get_column_letter(start_col + 4)
        amt_col   = get_column_letter(start_col + 5)

        # ===============================
        # 写数据
        # ===============================
        start_row = 2
        r = start_row

        for name, info in final.items():
            ws.cell(r, start_col + 1, name)
            ws.cell(r, start_col + 2, info["供货价"])
            ws.cell(r, start_col + 3, -info["数量"])

            ws.cell(r, start_col + 4, f"={qty_col}{r}*1")
            ws.cell(
                r,
                start_col + 5,
                f"={price_col}{r}*{qty_col}{r}-{fee_col}{r}"
            )
            r += 1

        end_row = r - 1

        # ===============================
        # 分销商合并（安全）
        # ===============================
        if end_row >= start_row:
            ws.cell(start_row, start_col).value = file.stem
            ws.merge_cells(
                start_row=start_row,
                start_column=start_col,
                end_row=end_row,
                end_column=start_col
            )
            # 添加垂直水平居中样式（修复弃用警告）
            from openpyxl.styles import Alignment

            ws.cell(start_row, start_col).alignment = Alignment(
                horizontal='center',
                vertical='center'
            )

        # ===============================
        # 汇总行
        # ===============================
        total_row = end_row + 1
        ws.cell(total_row, start_col + 1, "合计")
        ws.cell(
            total_row,
            start_col + 3,
            f"=SUM({qty_col}{start_row}:{qty_col}{end_row})"
        )
        ws.cell(
            total_row,
            start_col + 4,
            f"=SUM({fee_col}{start_row}:{fee_col}{end_row})"
        )
        ws.cell(
            total_row,
            start_col + 5,
            f"=SUM({amt_col}{start_row}:{amt_col}{end_row})"
        )

        # ===============================
        # 边框（表头 + 数据 + 合计）
        # ===============================
        for row in range(1, total_row + 1):
            for col in range(start_col, start_col + len(headers)):
                ws.cell(row, col).border = border

        # ===============================
        # 列宽
        # ===============================
        ws.column_dimensions[get_column_letter(start_col)].width = 18   # 分销商
        ws.column_dimensions[get_column_letter(start_col + 1)].width = 22
        ws.column_dimensions[get_column_letter(start_col + 2)].width = 12

        for i in range(1, 4):  # 间隔列
            ws.column_dimensions[get_column_letter(code_col + i)].width = 6

        # ===============================
        # 未匹配编码提示（不影响列宽）
        # ===============================
        warn_row = total_row + 2

        # 未匹配编码
        if unmatched_codes:
            ws.cell(
                warn_row,
                start_col,
                "⚠ 以下商家编码未在编码表中匹配，请人工核对"
            ).font = red_font
            ws.cell(
                warn_row + 1,
                start_col,
                ", ".join(sorted(unmatched_codes))
            ).font = red_font
            warn_row += 3

        # 缺失供货价
        if missing_price_names:
            ws.cell(
                warn_row,
                start_col,
                "⚠ 以下商品未配置供货价，请补充后重新计算"
            ).font = red_font
            ws.cell(
                warn_row + 1,
                start_col,
                ", ".join(sorted(missing_price_names))
            ).font = red_font

        wb.save(file)
        print(f"✅ 已处理：{file.name}")

    except Exception as e:
        print(f"❌ 处理失败：{file.name} → {e}")
