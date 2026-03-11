# STDF / CSV 互转 Windows 小工具

一个可直接运行的 Python 小工具，支持 **STDF 与 CSV 双向转换**：

- `STDF -> CSV`
- `CSV -> STDF`

并提供图形界面（Tkinter），适合在 Windows 上打包为单文件 EXE 使用。

## 转换格式说明

本工具按 STDF 二进制记录头进行可逆转换：

- `REC_LEN` (2 bytes, little-endian)
- `REC_TYP` (1 byte)
- `REC_SUB` (1 byte)
- `payload` (`REC_LEN` bytes)

导出的 CSV 固定列：

```csv
index,offset,rec_len,rec_typ,rec_sub,payload_hex
```

其中 `payload_hex` 为大写十六进制字符串。只要 CSV 不被破坏，支持无损回写为 STDF。

## 运行方式

### 1) 图形界面

```bash
python stdf_csv_converter.py
```

### 2) 命令行

```bash
# STDF -> CSV
python stdf_csv_converter.py stdf2csv input.stdf output.csv

# CSV -> STDF
python stdf_csv_converter.py csv2stdf input.csv output.stdf
```

## Windows 打包（可选）

建议使用 `pyinstaller`：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name STDF_CSV_Converter stdf_csv_converter.py
```

输出文件在：

- `dist/STDF_CSV_Converter.exe`

## 注意事项

- 本工具做的是“记录级二进制可逆转换”，不是按 STDF 语义字段（如 MIR/PTR 各字段）展开成业务 CSV。
- 如果你后续需要“语义级展开 CSV”（每类记录拆字段），可以在此工具基础上追加 STDF 记录字典解析。
