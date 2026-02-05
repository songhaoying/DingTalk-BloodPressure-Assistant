# 🏥 DingTalk-BloodPressure-Assistant (钉钉血压记录助手)

这是一个基于钉钉机器人和阿里云大模型（Qwen-VL）的智能血压管理助手。员工可以通过钉钉直接发送电子血压计的照片，机器人会自动识别屏幕上的读数（收缩压、舒张压、脉搏）并保存到数据库，方便员工随时查看历史记录。

## ✨ 功能特性

- **📸 智能读图**：利用 Qwen-VL 多模态大模型，无需手动输入，直接拍照上传即可识别血压数据。
- **📊 历史记录**：支持查询个人的血压测量历史，关注健康趋势。
- **🔒 企业内部应用**：专为企业内部钉钉环境设计，数据安全可控。
- **🚀 Stream 模式**：使用钉钉 Stream 模式部署，**无需公网 IP**，内网服务器即可运行。

## 🛠 技术栈

- **语言**: Python 3.8+
- **框架**: `dingtalk-stream` (钉钉 Stream 模式 SDK)
- **AI 模型**: 阿里云百炼 DashScope (Qwen-VL-Max)
- **数据库**: SQLite (默认) / SQL Server (支持)
- **依赖管理**: `pip` / `venv`

## 🚀 快速开始

### 1. 准备工作
你需要拥有：
- 钉钉企业内部开发者权限
- 阿里云百炼 (DashScope) API Key

### 2. 部署运行
详细的部署步骤请参考 [DEPLOY.md](DEPLOY.md)。

简述：
```bash
# 1. 克隆代码
git clone <repo_url>
cd Ding_robot

# 2. 创建环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 Key

# 5. 运行
python main.py
```

## 📱 使用指南

### 🔍 如何找到机器人
1. **搜索查找**：
   - 在钉钉顶部搜索栏输入机器人的名称（即你在钉钉开发者后台设置的应用名称，例如“健康小助手”）。
   - 在“联系人”或“应用”分类下点击该机器人即可进入对话窗口。

2. **工作台查找**：
   - 如果管理员已将应用发布到工作台，你可以在钉钉底部的“工作台”页面中找到该应用图标，点击即可使用。

### 🩺 功能使用
1. **记录血压**：
   - 直接发送电子血压计的**屏幕照片**给机器人。
   - 机器人会自动识别并回复测量结果（收缩压、舒张压、脉搏），同时保存数据。

2. **查询历史**：
   - 发送文字消息 **"历史"**。
   - 机器人将返回你最近的测量记录。

## 📂 项目结构

```
.
├── main.py              # 程序入口
├── config.py            # 配置管理
├── requirements.txt     # 项目依赖
├── services/            # 核心服务模块
│   ├── handlers.py      # 消息处理逻辑
│   ├── image_analyzer.py# 图片识别 (DashScope)
│   ├── database.py      # 数据库操作
│   └── dingtalk_api.py  # 钉钉 API 封装
└── DEPLOY.md            # 部署文档
```

## 📄 License

MIT
