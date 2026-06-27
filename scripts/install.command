#!/bin/bash

APP_NAME="PropCrew"
APP_DIR="${HOME}/Applications/${APP_NAME}.app"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🚀 正在安装 ${APP_NAME}..."
echo ""

# 1. 检查 Python
PYTHON_PATH=$(command -v python3)
if [ -z "$PYTHON_PATH" ]; then
    echo "❌ 未找到 Python3"
    echo "   请先安装：brew install python"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# 2. 安装依赖
echo "📦 安装 Python 依赖..."
cd "${PROJECT_DIR}"
pip3 install -r requirements.txt -q 2>/dev/null
echo "✅ 依赖安装完成"

# 3. 创建 ~/Applications 目录（如果没有的话）
mkdir -p "${HOME}/Applications"

# 4. 创建 .app 包
echo "📁 创建 ${APP_NAME}.app..."
rm -rf "${APP_DIR}"
mkdir -p "${APP_DIR}/Contents/MacOS"
mkdir -p "${APP_DIR}/Contents/Resources"

# 创建启动脚本
cat > "${APP_DIR}/Contents/MacOS/${APP_NAME}" << 'APPSCRIPT'
#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "$0")/../../../.." && pwd)"

cd "${PROJECT_DIR}"

# 启动 Streamlit（后台运行）
echo "🚀 PropCrew 启动中..."
nohup python3 -m streamlit run app.py \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.port=8501 \
    > /tmp/propcrew.log 2>&1 &

# 等待后打开浏览器
sleep 3
open http://localhost:8501

# 保持前台进程，双击时 Terminal 不自动关闭
echo ""
echo "✅ PropCrew 已启动！"
echo "   浏览器已自动打开 http://localhost:8501"
echo ""
echo "   按 Ctrl+C 停止服务"
wait
APPSCRIPT

chmod +x "${APP_DIR}/Contents/MacOS/${APP_NAME}"

# 创建 Info.plist
cat > "${APP_DIR}/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.propcrew.app</string>
    <key>CFBundleName</key>
    <string>PropCrew</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

# 复制项目到 .app 内（软链也可以，但拷贝更稳定）
echo "📂 复制项目代码..."
cp -R "${PROJECT_DIR}" "${APP_DIR}/Contents/Resources/PropCrew"

# 修正启动脚本里的路径（因为项目被拷贝到 app 内部了）
cat > "${APP_DIR}/Contents/MacOS/${APP_NAME}" << 'APPSCRIPT'
#!/bin/bash
APP_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${APP_DIR}/Contents/Resources/PropCrew"

# 启动 Streamlit
nohup python3 -m streamlit run app.py \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.port=8501 \
    > /tmp/propcrew.log 2>&1 &

sleep 3
open http://localhost:8501

echo ""
echo "✅ PropCrew 已启动！浏览器已自动打开"
echo "   按 Ctrl+C 停止服务"
wait
APPSCRIPT

chmod +x "${APP_DIR}/Contents/MacOS/${APP_NAME}"

echo ""
echo "✅ ${APP_NAME}.app 已安装到 ${APP_DIR}"
echo ""
echo "📌 使用方法："
echo "   1. 打开 Finder → 左侧「应用程序」→ 找到 PropCrew"
echo "   2. 双击打开（首次可能需右键→打开）"
echo "   3. 浏览器自动弹出 http://localhost:8501"
echo ""
echo "⚙️  配置 API Key：启动后页面右上角输入 DeepSeek Key"
echo ""
echo "📂 项目原始位置：${PROJECT_DIR}"
