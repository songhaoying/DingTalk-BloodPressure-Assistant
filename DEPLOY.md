# 🚀 DingTalk Robot 部署指南

本指南将帮助你从零开始部署钉钉血压监测机器人。

## 📋 目录

1. [准备工作](#1-准备工作)
2. [钉钉开发者后台配置](#2-钉钉开发者后台配置)
3. [阿里云百炼配置](#3-阿里云百炼配置)
4. [服务器部署](#4-服务器部署)
5. [常见问题](#5-常见问题)

---

## 1. 准备工作

- **服务器**: 一台 Linux/macOS/Windows 服务器（推荐 Ubuntu/Debian）。
  - **网络要求**: 需要能访问外网（连接钉钉和阿里云接口），**不需要公网 IP**（使用 Stream 模式）。
- **Python**: 3.8 或更高版本。
- **数据库 (可选)**: SQL Server 2016+ (默认使用内置 SQLite，如需使用 SQL Server 请提前准备数据库实例及 ODBC 驱动)。
- **账号**:
  - 钉钉企业管理员/开发者权限。
  - 阿里云账号（开通 DashScope 模型服务）。

---

## 2. 钉钉开发者后台配置

### 2.1 创建应用
1. 登录 [钉钉开发者后台](https://open-dev.dingtalk.com/)。
2. 进入 **"应用开发" -> "企业内部开发"**。
3. 点击 **"创建应用"**，填写应用名称（如"健康小助手"）、描述等，创建成功。

### 2.2 配置机器人
1. 在应用详情页，左侧菜单点击 **"应用功能" -> "机器人"**。
2. 开启 **"机器人"** 开关。
3. **重要配置**:
   - **消息接收模式**: 选择 **"Stream 模式"**。
     - *注意：不要选择 HTTP 回调，Stream 模式更稳定且无需公网 IP。*
   - 记录下页面上的 **AppKey** 和 **AppSecret**。

### 2.3 权限管理
1. 左侧菜单点击 **"开发配置" -> "权限管理"**。
2. 搜索并申请以下权限（通常机器人默认有基础发消息权限，但建议检查）：
   - `企业内机器人发送消息` (必选)
   - `文件存储` (如果要下载图片，通常需要相关权限，或者直接通过 downloadCode 下载)
   - *注意：如果是新版机器人，通常只要开启了机器人功能即可发送消息。*

### 2.4 获取 AgentID
1. 在应用详情页顶部，找到 **AgentID**（通常在 AppKey 附近，或者是发布后在应用列表中查看）。
2. 记录 **AgentID**。

### 2.5 发布应用
1. 左侧菜单 **"版本管理与发布"**。
2. 创建一个新版本并发布。
3. 只有发布后，企业内的员工才能在钉钉中搜到并使用该机器人。

---

## 3. 阿里云百炼配置

1. 登录 [阿里云百炼控制台](https://bailian.console.aliyun.com/)。
2. 开通 **DashScope** 服务。
3. 进入 **API-KEY 管理**，创建一个新的 API Key。
4. 记录下 **API Key**（以 `sk-` 开头）。
5. 确保账户有余额（Qwen-VL 模型通常有免费额度或按量付费）。

---

## 4. 服务器部署

### 4.1 获取代码
将项目代码上传至服务器：
```bash
# 假设放在 /opt/ding_robot
cd /opt
git clone <your-repo-url> ding_robot
cd ding_robot
```

### 4.2 创建虚拟环境
推荐使用 `venv` 隔离 Python 环境：
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4.3 安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 配置文件
复制示例配置并修改：
```bash
cp .env.example .env
vim .env
```

在 `.env` 中填入之前获取的信息：
```ini
# 钉钉配置
DINGTALK_APP_KEY=dingxxxxxxxxxxxx
DINGTALK_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DINGTALK_AGENT_ID=123456789

# 阿里云配置
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# 数据库配置 (可选, 默认为 sqlite)
# DB_TYPE=sqlite

# SQL Server 配置 (当 DB_TYPE=sqlserver 时必填)
# SQLSERVER_HOST=localhost
# SQLSERVER_PORT=1433
# SQLSERVER_USER=sa
# SQLSERVER_PASSWORD=your_password
# SQLSERVER_DB=DingTalkBP
```

### 4.5 运行测试
在前台运行以验证配置：
```bash
python main.py
```
- 如果看到日志 `Starting DingTalk Stream Client...`，说明连接成功。
- 此时在钉钉给机器人发一条消息，看终端是否有日志输出。
- 按 `Ctrl+C` 停止。

### 4.6 后台运行 (Systemd)
创建 Systemd 服务文件实现开机自启：

`sudo vim /etc/systemd/system/ding_robot.service`

```ini
[Unit]
Description=DingTalk Blood Pressure Robot
After=network.target

[Service]
# 修改为实际用户
User=root
# 修改为实际路径
WorkingDirectory=/opt/ding_robot
# 修改为实际 python 路径
ExecStart=/opt/ding_robot/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable ding_robot
sudo systemctl start ding_robot
```

查看状态：
```bash
sudo systemctl status ding_robot
```

### 4.7 Windows 服务部署 (后台运行)
推荐使用 **NSSM (Non-Sucking Service Manager)** 将机器人作为 Windows 服务运行，实现开机自启和自动重启。

1. **下载 NSSM**:
   - 访问 [NSSM 官网](https://nssm.cc/download) 下载最新版 (如 `nssm-2.24.zip`)。
   - 解压后，将 `win64` (或 `win32`) 目录下的 `nssm.exe` 复制到项目根目录，或添加到系统环境变量 PATH 中。

2. **使用脚本安装**:
   以 **管理员身份** 运行 `install_service.bat`。

   ```bat
   install_service.bat
   ```

3. **手动管理服务**:
   - 启动: `nssm start DingRobot`
   - 停止: `nssm stop DingRobot`
   - 重启: `nssm restart DingRobot`
   - 查看状态: `nssm status DingRobot`
   - 编辑配置: `nssm edit DingRobot`
   - 删除服务: `nssm remove DingRobot`

### 4.8 切换至 SQL Server (可选)
如果需要使用 SQL Server 存储数据：

1. **安装 ODBC 驱动**:
   - 确保服务器已安装 Microsoft ODBC Driver for SQL Server (如 `msodbcsql17` 或 `msodbcsql18`)。
   - 依赖包通常包括 `unixodbc-dev` (Linux) 或 `unixodbc` (macOS)。
   
2. **修改配置**:
   编辑 `.env` 文件，设置 `DB_TYPE=sqlserver` 并填入数据库连接信息。

3. **数据迁移**:
   如果已有 SQLite 数据需要迁移至 SQL Server，请运行：
   ```bash
   python migrate_db.py
   ```
   *注意：迁移前请确保 SQL Server 配置正确且数据库已创建（表会自动创建）。*

---

## 5. 常见问题

### Q1: 机器人不回复消息？
- 检查 `.env` 中的 `DINGTALK_AGENT_ID` 是否正确。
- 检查钉钉后台是否开启了 **Stream 模式**。
- 检查服务器日志 `journalctl -u ding_robot -f` 是否有报错。

### Q2: 图片识别失败？
- 检查 `DASHSCOPE_API_KEY` 是否有效。
- 检查图片是否清晰，是否为血压计屏幕。
- 查看日志中的错误信息（如 `API Error`）。

### Q3: 数据库在哪？
- **SQLite (默认)**: 文件位于项目根目录的 `bp_data.db`。
- **SQL Server**: 取决于 `.env` 中的配置。如需迁移，请参考本文档 4.7 节。
