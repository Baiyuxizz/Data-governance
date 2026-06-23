import pandas as pd
from pathlib import Path
import re

# 配置文件
EXCEL_NAME = [
    "INV01.xlsx",
    "INV02.xlsx",
    "INV03.xlsx",
    "INV04.xlsx",
    "INV05.xlsx",
    "INV06.xlsx"
]

FOLDER_NAME = "8100（已拆分）"

BOUNDARY_PAIRS = [
    (10, 0, 1),   # 文件1 vs 文件2
    (19, 1, 2),   # 文件2 vs 文件3
    (28, 2, 3),   # 文件3 vs 文件4
    (37, 3, 4),   # 文件4 vs 文件5
    (46, 4, 5)    # 文件5 vs 文件6
]

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

def parse_start_month(col_name):
    """从列名提取起始月份"""
    m = re.search(r'^(\d+)[-月]', col_name)
    if m:
        return int(m.group(1))
    return -1

def load_and_prepare(file_path, key_cols):
    """读取excel文件，并查找键是否缺失，生成唯一键，匹配后续两个文件的物料"""
    df = pd.read_excel(file_path)
    missing = [k for k in KEY_COLS if k not in df.columns]
    if missing:
        raise ValueError(f"文件{file_path}缺少：{missing} 列")
    df['_key'] = df[key_cols].fillna('').astype(str).apply(
        lambda row: '|'.join(row.astype(str)), axis=1
    )
    return df

def get_above_quantity(df, boundary):
    qty_cols = [c for c in df.columns if '月' in c and c.endswith('数量') and c != '库存数量']
    selected = []
    for col in qty_cols:
        start = parse_start_month(col)
        if start >= boundary:
            selected.append(col)
    if not selected:
        return pd.Series(0, index=df.index)
    return df[selected].sum(axis=1)


def main():
    dfs = []
    for path in FILE_PATHS:
        if not Path(path).exists():
            print(f"警告：文件{path}不存在，跳过")
            dfs.append(None)
        else:
            dfs.append(load_and_prepare(path, KEY_COLS))

    all_results = []

    for boundary, idx_a, idx_b in BOUNDARY_PAIRS:
        if dfs[idx_a] is None or dfs[idx_b] is None:
            print(f"边界{boundary}所需文件缺失，跳过")
            continue

        print(f"处理边界{boundary}：文件{idx_a+1} vs 文件{idx_b+1}")
        df_a = dfs[idx_a].copy()
        df_b = dfs[idx_b].copy()

        df_a['above_sum'] = get_above_quantity(df_a, boundary)
        df_b['above_sum'] = get_above_quantity(df_b, boundary)

        df_a_keep = df_a[['_key', 'above_sum']].drop_duplicates('_key')
        df_b_keep = df_b[['_key', 'above_sum']].drop_duplicates('_key')
        merged = pd.merge(df_a_keep, df_b_keep, on='_key', how='outer', suffixes=('_A', '_B'))
        merged.fillna(0, inplace=True)
        merged['diff'] = merged['above_sum_A'] - merged['above_sum_B']

        suspicious = merged[merged['diff'] != 0].copy()
        if suspicious.empty:
            print(f"边界 {boundary} 无冲突")
            continue

        # 回填 KEY_COLS 明细
        key_info = {}
        for key in suspicious['_key']:
            row_a = df_a[df_a['_key'] == key]
            if not row_a.empty:
                key_info[key] = row_a[KEY_COLS].iloc[0].to_dict()
            else:
                row_b = df_b[df_b['_key'] == key]
                if not row_b.empty:
                    key_info[key] = row_b[KEY_COLS].iloc[0].to_dict()
                else:
                    key_info[key] = {k: None for k in KEY_COLS}

        for k in KEY_COLS:
            suspicious[k] = suspicious['_key'].map(lambda x: key_info[x][k])
        suspicious['边界'] = boundary
        # result_cols = KEY_COLS + ['边界', 'above_sum_A', 'above_sum_B', 'diff']
        # all_results.append(suspicious[result_cols])

        suspicious.rename(columns={
            'above_sum_A': '边界以上数量',
            'above_sum_B': '实际数量',
            'diff': '差值'
        }, inplace=True)

        result_cols = KEY_COLS + ['边界', '边界以上数量', '实际数量', '差值']
        all_results.append(suspicious[result_cols])

    if all_results:
        final_result = pd.concat(all_results, ignore_index=True)
        final_result.sort_values(['边界'] + KEY_COLS, inplace=True)
        output_path = Path(OUTPUT_FILE)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_result.to_excel(output_path, index=False)
        print(f"发现 {len(final_result)} 条边界冲突记录，已保存至 {output_path.absolute()}")
        print("示例数据：")
        print(final_result.head())
    else:
        print("未发现任何边界冲突记录。")

if __name__ == "__main__":
    main()


