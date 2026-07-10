"""
마크다운 형식의 EDA 보고서를 엑셀(xlsx) 파일로 변환하는 스크립트.

이 스크립트는 yes24/docs/eda_report.md 파일을 읽어
각 항목(제목, 리스트, 이미지 등)을 엑셀 서식에 맞게
yes24/docs/eda_report.xlsx 로 저장합니다.
"""
import xlsxwriter
import os

md_path = 'eda_report.md'
xlsx_path = 'eda_report.xlsx'

workbook = xlsxwriter.Workbook(xlsx_path)
worksheet = workbook.add_worksheet('EDA Report')

# Define formats
header_format = workbook.add_format({'bold': True, 'font_size': 14, 'bg_color': '#D9E1F2', 'border': 1})
subheader_format = workbook.add_format({'bold': True, 'font_size': 12, 'bg_color': '#FCE4D6', 'border': 1})
normal_format = workbook.add_format({'text_wrap': True, 'valign': 'vcenter'})
bold_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'vcenter'})
quote_format = workbook.add_format({'italic': True, 'text_wrap': True, 'font_color': '#555555'})

worksheet.set_column('A:A', 30)
worksheet.set_column('B:B', 60)

with open(md_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

row = 0
for line in lines:
    line = line.strip()
    if not line or line == '---':
        continue
    
    if line.startswith('# '):
        worksheet.merge_range(row, 0, row, 1, line[2:], header_format)
        worksheet.set_row(row, 30)
        row += 2
    elif line.startswith('## '):
        worksheet.merge_range(row, 0, row, 1, line[3:], subheader_format)
        worksheet.set_row(row, 25)
        row += 2
    elif line.startswith('### '):
        worksheet.merge_range(row, 0, row, 1, line[4:], bold_format)
        row += 1
    elif line.startswith('- **'):
        parts = line.split('**: ')
        if len(parts) == 2:
            key = parts[0].replace('- **', '')
            val = parts[1]
            worksheet.write(row, 0, key, bold_format)
            worksheet.write(row, 1, val, normal_format)
            row += 1
        else:
            worksheet.merge_range(row, 0, row, 1, line.replace('- **', '').replace('**', ''), normal_format)
            row += 1
    elif line.startswith('> '):
        worksheet.merge_range(row, 0, row, 1, line[2:], quote_format)
        row += 1
    elif line.startswith('![') and '](' in line:
        # Handle image
        img_path_start = line.find('](') + 2
        img_path_end = line.find(')', img_path_start)
        img_rel_path = line[img_path_start:img_path_end]
        img_abs_path = os.path.join(os.path.dirname(md_path) if os.path.dirname(md_path) else '.', img_rel_path)
        img_abs_path = os.path.normpath(img_abs_path)
        
        if os.path.exists(img_abs_path):
            worksheet.insert_image(row, 0, img_abs_path, {'x_scale': 0.6, 'y_scale': 0.6})
            row += 20 # approximate space for image
        else:
            worksheet.write(row, 0, f"[Image missing: {img_rel_path}]", normal_format)
            row += 1
    else:
        worksheet.merge_range(row, 0, row, 1, line, normal_format)
        row += 1

workbook.close()
