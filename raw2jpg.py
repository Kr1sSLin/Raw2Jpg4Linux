#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAW 格式批量转换为 JPEG 的图形界面工具。"""

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import rawpy
from PIL import Image
from tkinterdnd2 import DND_FILES, TkinterDnD

RAW_EXTENSIONS = {
    ".cr2", ".cr3", ".nef", ".nrw", ".arw", ".srf", ".sr2", ".dng",
    ".raf", ".orf", ".rw2", ".pef", ".x3f", ".iiq", ".3fr", ".raw",
    ".rwl", ".srw", ".kdc", ".dcr", ".mef", ".mrw", ".erf", ".mos",
    ".cap", ".tif", ".tiff",
}

FILE_TYPES = [
    ("RAW 文件", "*" + " *".join(sorted(RAW_EXTENSIONS))),
    ("所有文件", "*.*"),
]


class Raw2JpgApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RAW 转 JPEG 批量转换工具")
        self.root.geometry("720x560")
        self.root.minsize(600, 480)

        self.files = []
        self.output_dir = tk.StringVar()
        self.quality = tk.IntVar(value=95)
        self.use_camera_wb = tk.BooleanVar(value=True)
        self._build_ui()
        self._enable_dnd()

    def _enable_dnd(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self._on_drop)
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drop(self, event):
        try:
            paths = self.root.tk.splitlist(event.data)
        except Exception:
            paths = event.data.split()
        for p in paths:
            self._add_path(p)
        self._update_count()

    def _add_path(self, p):
        if os.path.isdir(p):
            for root_dir, _, names in os.walk(p):
                for n in sorted(names):
                    if Path(n).suffix.lower() in RAW_EXTENSIONS:
                        self._add_file(os.path.join(root_dir, n))
        elif os.path.isfile(p):
            self._add_file(p)

    def _add_file(self, p):
        if p not in self.files:
            self.files.append(p)
            self.listbox.insert(tk.END, p)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(main)
        top.pack(fill=tk.X)
        ttk.Button(top, text="添加文件", command=self.add_files).pack(side=tk.LEFT)
        ttk.Button(top, text="清空列表", command=self.clear_files).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Label(top, text="（可拖拽文件/文件夹到此处）", foreground="gray").pack(side=tk.LEFT, padx=10)

        # 文件列表
        list_frame = ttk.LabelFrame(main, text="待转换文件", padding=6)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 6))

        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=list_scroll.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.count_label = ttk.Label(main, text="共 0 个文件")
        self.count_label.pack(anchor=tk.W, pady=(0, 6))

        # 输出目录
        out_frame = ttk.Frame(main)
        out_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(out_frame, text="输出目录:").pack(side=tk.LEFT)
        ttk.Entry(out_frame, textvariable=self.output_dir).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=6
        )
        ttk.Button(out_frame, text="浏览...", command=self.choose_output_dir).pack(side=tk.RIGHT)

        # 选项
        opt_frame = ttk.Frame(main)
        opt_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(opt_frame, text="JPEG 质量:").pack(side=tk.LEFT)
        ttk.Spinbox(opt_frame, from_=1, to=100, textvariable=self.quality, width=6).pack(
            side=tk.LEFT, padx=(6, 12)
        )
        ttk.Checkbutton(opt_frame, text="使用相机白平衡", variable=self.use_camera_wb).pack(side=tk.LEFT)

        # 进度与按钮
        self.progress = ttk.Progressbar(main, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 6))

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X)
        self.convert_btn = ttk.Button(btn_frame, text="开始转换", command=self.start_convert)
        self.convert_btn.pack(side=tk.LEFT)
        self.status_label = ttk.Label(btn_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=10)

        # 日志
        log_frame = ttk.LabelFrame(main, text="日志", padding=4)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def add_files(self):
        paths = filedialog.askopenfilenames(title="选择 RAW 文件", filetypes=FILE_TYPES)
        for p in paths:
            self._add_file(p)
        self._update_count()

    def clear_files(self):
        self.files.clear()
        self.listbox.delete(0, tk.END)
        self._update_count()

    def choose_output_dir(self):
        d = filedialog.askdirectory(title="选择输出目录")
        if d:
            self.output_dir.set(d)

    def _update_count(self):
        self.count_label.config(text=f"共 {len(self.files)} 个文件")

    def _log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_convert(self):
        if not self.files:
            messagebox.showwarning("提示", "请先添加要转换的文件。")
            return
        out_dir = self.output_dir.get().strip()
        if not out_dir:
            messagebox.showwarning("提示", "请选择输出目录。")
            return
        if not os.path.isdir(out_dir):
            try:
                os.makedirs(out_dir, exist_ok=True)
            except OSError as e:
                messagebox.showerror("错误", f"无法创建输出目录:\n{e}")
                return

        self.convert_btn.config(state=tk.DISABLED)
        self.progress.config(maximum=len(self.files), value=0)
        self.status_label.config(text="转换中...")

        worker = threading.Thread(
            target=self._convert_worker, args=(list(self.files), out_dir), daemon=True
        )
        worker.start()

    def _convert_worker(self, files, out_dir):
        quality = self.quality.get()
        use_camera_wb = self.use_camera_wb.get()
        success = 0
        failed = 0

        for i, src in enumerate(files, 1):
            name = os.path.basename(src)
            stem = Path(src).stem
            dst = os.path.join(out_dir, stem + ".jpg")
            try:
                with rawpy.imread(src) as raw:
                    rgb = raw.postprocess(use_camera_wb=use_camera_wb)
                Image.fromarray(rgb).save(dst, "JPEG", quality=quality)
                success += 1
                self.root.after(0, self._log, f"[{i}/{len(files)}] OK: {name}")
            except Exception as e:
                failed += 1
                self.root.after(0, self._log, f"[{i}/{len(files)}] 失败: {name} -> {e}")

            self.root.after(0, self._update_progress, i)

        self.root.after(0, self._finish, success, failed)

    def _update_progress(self, value):
        self.progress.config(value=value)

    def _finish(self, success, failed):
        self.convert_btn.config(state=tk.NORMAL)
        self.status_label.config(text=f"完成: 成功 {success} 个, 失败 {failed} 个")
        self._log(f"转换结束: 成功 {success}, 失败 {failed}")
        messagebox.showinfo("完成", f"转换完成。\n成功: {success}\n失败: {failed}")


def main():
    root = TkinterDnD.Tk()
    Raw2JpgApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
