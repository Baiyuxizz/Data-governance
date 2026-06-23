import pandas as pd

# 配置文件
EXCEL_NAME = [
    "INV01.xlsx",
    "INV02.xlsx",
    "INV03.xlsx",
    "INV04.xlsx",
    "INV05.xlsx",
    "INV06.xlsx"
]

FOLDER_NAME = "8000（已拆分）"

FILE_PATHS = [
    rf"D:\5.2\任务文件\{FOLDER_NAME}\INV_AGE\Merge\{EXCEL_NAME[0]}",
    rf"D:\5.2\任务文件\{FOLDER_NAME}\INV_AGE\Merge\{EXCEL_NAME[1]}",
    rf"D:\5.2\任务文件\{FOLDER_NAME}\INV_AGE\Merge\{EXCEL_NAME[2]}",
    rf"D:\5.2\任务文件\{FOLDER_NAME}\INV_AGE\Merge\{EXCEL_NAME[3]}",
    rf"D:\5.2\任务文件\{FOLDER_NAME}\INV_AGE\Merge\{EXCEL_NAME[4]}",
    rf"D:\5.2\任务文件\{FOLDER_NAME}\INV_AGE\Merge\{EXCEL_NAME[5]}",
]

OUTPUT_FILE = rf"D:\5.2\任务文件\{FOLDER_NAME}\INV_AGE\Merge\boundary_conflicts.xlsx"

KEY_COLS = ["工厂", "库位", "物料", "批次/评估类型"]        # 标识列

# ====================================================================

def parse_start_month():
    


