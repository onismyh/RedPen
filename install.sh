#!/bin/bash
set -e

echo "========================================="
echo "  RedPen 安装脚本"
echo "  Word 文档修订标记工具"
echo "========================================="
echo ""

# 1. 检查 Python
if command -v python3 &>/dev/null; then
    PY=python3
elif command -v python &>/dev/null; then
    PY=python
else
    echo "❌ 未找到 Python，请先安装 Python 3.10+"
    echo ""
    echo "  macOS:   brew install python3"
    echo "  Windows: https://www.python.org/downloads/"
    echo "  Linux:   sudo apt install python3 python3-pip"
    echo ""
    exit 1
fi

# 2. 检查 Python 版本
PY_VERSION=$($PY -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$($PY -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PY -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    echo "❌ Python 版本过低: $PY_VERSION (需要 3.10+)"
    exit 1
fi

echo "✅ Python $PY_VERSION"

# 3. 安装 RedPen
echo ""
echo "正在安装 RedPen..."
cd "$(dirname "$0")"
$PY -m pip install -e . --quiet 2>&1 | tail -1

# 4. 验证安装
if command -v redpen &>/dev/null; then
    echo "✅ 安装成功！"
else
    echo "✅ 安装成功！（可能需要重启终端）"
fi

echo ""
echo "========================================="
echo "  快速体验"
echo "========================================="
echo ""
echo "  # 查看示例文档内容"
echo "  redpen read examples/sample.docx"
echo ""
echo "  # 用示例修改生成带修订的文档"
echo "  redpen apply examples/sample.docx @examples/edits.json -o output.docx"
echo ""
echo "  # 查看修订内容"
echo "  redpen show output.docx"
echo ""
echo "  # 在 Word 中打开 output.docx，审阅 → 所有标记 即可看到修订"
echo ""
