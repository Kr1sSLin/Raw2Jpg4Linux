# Raw2Jpg

一个在 Linux 上运行的 RAW 格式批量转 JPEG 图形界面工具。

基于 Tkinter 构建 GUI，使用 [rawpy](https://pypi.org/project/rawpy/)（libraw 封装）+ [Pillow](https://python-pillow.org/) 解码与输出。

## 功能特性

- 批量导入 RAW 文件，支持**拖拽**文件/文件夹到窗口（自动递归收集文件夹内所有 RAW 文件）
- 支持常见 RAW 格式：CR2/CR3（佳能）、NEF/NRW（尼康）、ARW（索尼）、DNG、RAF、ORF、RW2、PEF、X3F 等
- 指定输出目录，可选自动创建
- JPEG 输出质量可调（1–100，默认 95）
- 可选使用相机白平衡
- 后台线程转换，界面不卡顿，带进度条与日志
- 自动去重，失败文件单独记录并继续

## 环境要求

- Linux（Ubuntu/Debian 等）
- Python 3.10+
- 显示环境（Tkinter 需要图形界面）

## 安装

在项目根目录创建虚拟环境并安装依赖：

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

### 常见问题

- **`No module named 'tkinter'`**：Ubuntu/Debian 需安装系统包：

  ```bash
  sudo apt install python3-tk python3-pip python3-venv
  ```

- **PEP 668（externally-managed-environment）错误**：系统 Python 受保护，请务必使用上面的虚拟环境方式安装，不要直接 `pip install`。

## 使用

```bash
./.venv/bin/python raw2jpg.py
```

操作步骤：

1. 通过「添加文件」选择文件，或直接把文件/文件夹拖入窗口
2. 选择「输出目录」
3. 按需调整 JPEG 质量与白平衡选项
4. 点击「开始转换」，完成后在日志和弹窗中查看结果

输出文件以原文件名保存为 `.jpg`（如 `IMG_0001.CR2` → `IMG_0001.jpg`）。

## 项目结构

```
raw2jpg.py        主程序
requirements.txt  Python 依赖
.gitignore        git 忽略规则
```

## 依赖

| 包 | 用途 |
| --- | --- |
| rawpy | RAW 解码（libraw） |
| Pillow | 图像保存为 JPEG |
| tkinterdnd2 | 拖拽导入支持 |
