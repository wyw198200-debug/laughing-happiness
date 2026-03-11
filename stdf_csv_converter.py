#!/usr/bin/env python3
"""STDF <-> CSV converter with a small Tkinter GUI for Windows.

CSV schema used by this tool:
index,offset,rec_len,rec_typ,rec_sub,payload_hex

The converter parses STDF at the binary record-header level and preserves
record payload bytes, allowing reliable round-trip conversion.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


CSV_FIELDS = ["index", "offset", "rec_len", "rec_typ", "rec_sub", "payload_hex"]


class STDFFormatError(ValueError):
    """Raised when the input STDF or CSV format is invalid."""


def parse_stdf_records(data: bytes) -> list[dict[str, int | str]]:
    """Parse STDF bytes into record rows for CSV export."""
    records: list[dict[str, int | str]] = []
    pos = 0
    index = 0

    while pos < len(data):
        if pos + 4 > len(data):
            raise STDFFormatError(f"残缺的记录头，偏移 {pos}")

        rec_len = int.from_bytes(data[pos : pos + 2], "little")
        rec_typ = data[pos + 2]
        rec_sub = data[pos + 3]

        payload_start = pos + 4
        payload_end = payload_start + rec_len
        if payload_end > len(data):
            raise STDFFormatError(
                f"记录声明长度超出文件末尾：偏移 {pos}，长度 {rec_len}"
            )

        payload = data[payload_start:payload_end]
        records.append(
            {
                "index": index,
                "offset": pos,
                "rec_len": rec_len,
                "rec_typ": rec_typ,
                "rec_sub": rec_sub,
                "payload_hex": payload.hex().upper(),
            }
        )

        index += 1
        pos = payload_end

    return records


def build_stdf_bytes_from_rows(rows: list[dict[str, str]]) -> bytes:
    """Build STDF bytes from CSV rows."""
    out = bytearray()

    for i, row in enumerate(rows):
        try:
            rec_len = int(row["rec_len"])
            rec_typ = int(row["rec_typ"])
            rec_sub = int(row["rec_sub"])
            payload_hex = row["payload_hex"].strip()
        except KeyError as exc:
            raise STDFFormatError(f"CSV 缺少必要列: {exc}") from exc

        if not (0 <= rec_len <= 0xFFFF):
            raise STDFFormatError(f"第 {i + 1} 行 rec_len 超出范围: {rec_len}")
        if not (0 <= rec_typ <= 0xFF):
            raise STDFFormatError(f"第 {i + 1} 行 rec_typ 超出范围: {rec_typ}")
        if not (0 <= rec_sub <= 0xFF):
            raise STDFFormatError(f"第 {i + 1} 行 rec_sub 超出范围: {rec_sub}")

        try:
            payload = bytes.fromhex(payload_hex) if payload_hex else b""
        except ValueError as exc:
            raise STDFFormatError(f"第 {i + 1} 行 payload_hex 不是合法16进制") from exc

        if len(payload) != rec_len:
            raise STDFFormatError(
                f"第 {i + 1} 行 rec_len={rec_len} 与 payload 实际长度 {len(payload)} 不匹配"
            )

        out.extend(rec_len.to_bytes(2, "little"))
        out.append(rec_typ)
        out.append(rec_sub)
        out.extend(payload)

    return bytes(out)


def stdf_to_csv(stdf_path: pathlib.Path, csv_path: pathlib.Path) -> int:
    data = stdf_path.read_bytes()
    rows = parse_stdf_records(data)
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def csv_to_stdf(csv_path: pathlib.Path, stdf_path: pathlib.Path) -> int:
    with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise STDFFormatError("CSV 文件为空")
        missing = [name for name in CSV_FIELDS if name not in reader.fieldnames]
        if missing:
            raise STDFFormatError(f"CSV 缺少列: {', '.join(missing)}")

        rows = list(reader)

    data = build_stdf_bytes_from_rows(rows)
    stdf_path.write_bytes(data)
    return len(rows)


class ConverterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("STDF / CSV 互转工具")
        self.root.geometry("700x320")
        self.root.minsize(660, 280)

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="stdf_to_csv")
        self.status_var = tk.StringVar(value="请选择转换方向与文件路径。")

        self._build_ui()

    def _build_ui(self) -> None:
        frm = ttk.Frame(self.root, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        mode_box = ttk.LabelFrame(frm, text="转换方向", padding=10)
        mode_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(
            mode_box,
            text="STDF -> CSV",
            variable=self.mode_var,
            value="stdf_to_csv",
            command=self._refresh_suggested_output,
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            mode_box,
            text="CSV -> STDF",
            variable=self.mode_var,
            value="csv_to_stdf",
            command=self._refresh_suggested_output,
        ).pack(side=tk.LEFT)

        self._path_row(frm, "输入文件", self.input_var, self._choose_input)
        self._path_row(frm, "输出文件", self.output_var, self._choose_output)

        ttk.Button(frm, text="开始转换", command=self._run_convert).pack(pady=14)

        ttk.Label(
            frm,
            text="说明：该工具按 STDF 二进制记录头（REC_LEN/REC_TYP/REC_SUB）级别做可逆转换。",
            foreground="#444",
        ).pack(anchor=tk.W)

        ttk.Label(frm, textvariable=self.status_var, foreground="#005A9C").pack(
            anchor=tk.W, pady=(8, 0)
        )

    @staticmethod
    def _path_row(parent: ttk.Frame, label: str, var: tk.StringVar, browse_cmd) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text=label, width=8).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        ttk.Button(row, text="浏览", command=browse_cmd).pack(side=tk.LEFT)

    def _choose_input(self) -> None:
        if self.mode_var.get() == "stdf_to_csv":
            path = filedialog.askopenfilename(
                title="选择 STDF 文件",
                filetypes=[("STDF files", "*.stdf *.std"), ("All files", "*.*")],
            )
        else:
            path = filedialog.askopenfilename(
                title="选择 CSV 文件",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            )

        if path:
            self.input_var.set(path)
            self._refresh_suggested_output()

    def _choose_output(self) -> None:
        if self.mode_var.get() == "stdf_to_csv":
            path = filedialog.asksaveasfilename(
                title="保存 CSV 文件",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
            )
        else:
            path = filedialog.asksaveasfilename(
                title="保存 STDF 文件",
                defaultextension=".stdf",
                filetypes=[("STDF files", "*.stdf *.std"), ("All files", "*.*")],
            )

        if path:
            self.output_var.set(path)

    def _refresh_suggested_output(self) -> None:
        in_path = self.input_var.get().strip()
        if not in_path:
            return
        p = pathlib.Path(in_path)

        if self.mode_var.get() == "stdf_to_csv":
            self.output_var.set(str(p.with_suffix(".csv")))
        else:
            self.output_var.set(str(p.with_suffix(".stdf")))

    def _run_convert(self) -> None:
        input_path = self.input_var.get().strip()
        output_path = self.output_var.get().strip()

        if not input_path or not output_path:
            messagebox.showerror("错误", "请先选择输入与输出路径")
            return

        try:
            src = pathlib.Path(input_path)
            dst = pathlib.Path(output_path)
            if self.mode_var.get() == "stdf_to_csv":
                count = stdf_to_csv(src, dst)
                self.status_var.set(f"转换成功：共 {count} 条记录，输出 {dst}")
            else:
                count = csv_to_stdf(src, dst)
                self.status_var.set(f"转换成功：共 {count} 条记录，输出 {dst}")
        except Exception as exc:  # surface all errors in GUI
            messagebox.showerror("转换失败", str(exc))
            self.status_var.set(f"转换失败：{exc}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="STDF 与 CSV 互转工具")
    sub = parser.add_subparsers(dest="cmd")

    p1 = sub.add_parser("stdf2csv", help="将 STDF 转为 CSV")
    p1.add_argument("input", type=pathlib.Path, help="输入 STDF 文件")
    p1.add_argument("output", type=pathlib.Path, help="输出 CSV 文件")

    p2 = sub.add_parser("csv2stdf", help="将 CSV 转为 STDF")
    p2.add_argument("input", type=pathlib.Path, help="输入 CSV 文件")
    p2.add_argument("output", type=pathlib.Path, help="输出 STDF 文件")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "stdf2csv":
        count = stdf_to_csv(args.input, args.output)
        print(f"OK: exported {count} records -> {args.output}")
        return
    if args.cmd == "csv2stdf":
        count = csv_to_stdf(args.input, args.output)
        print(f"OK: built {count} records -> {args.output}")
        return

    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
