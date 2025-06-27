---

# Receipt n8n Transfer

## 项目简介

本项目是一个基于 FastAPI 的发票/收据 OCR 识别与结构化数据入库服务。它接收来自 n8n 等自动化平台的文件 URL，自动完成 OCR 识别、字段提取，并将结构化数据写入 Supabase 数据库。支持图片和 PDF 格式的发票/收据。

## 目录结构

```
receipt-n8n-transfer/
├── app.py                      # FastAPI 主应用，提供 /upload 接口
├── docker-compose.yml          # Docker Compose 配置
├── dockerfile                  # Docker 镜像构建文件
├── requirements.txt            # Python 依赖列表
└── file_ocr_upload/
    ├── main.py                 # 业务主流程，OCR+字段提取+入库
    ├── ocr.py                  # OCR 及字段提取相关方法
    └── insert_data.py          # 数据清洗、唯一性 hash、入库数据结构
```

## 主要功能

- **/upload API**：接收包含 `public_url`（文件地址）和 `user_id` 的 POST 请求，自动完成 OCR 识别、字段提取、数据入库。
- **OCR 识别**：支持图片和 PDF，调用 OpenRouter/Deepseek 等大模型 API 进行内容识别和字段抽取。
- **字段结构化**：自动提取发票号、日期、买方、卖方、金额、币种、类别、地址等字段，输出为标准 JSON。
- **数据去重**：通过关键字段生成 hash_id，防止重复入库。
- **日志记录**：详细记录处理流程和异常，日志按天分文件存储。

## 依赖环境

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- requests
- supabase

详见 `requirements.txt`。

## 快速开始

### 1. 环境变量

请在项目根目录下创建 `.env` 文件，内容示例：

```
SUPABASE_URL=你的Supabase地址
SUPABASE_SERVICE_ROLE_KEY=你的Supabase服务密钥
OPENROUTER_API_KEY=你的OpenRouter API Key
OPENROUTER_URL=OpenRouter API地址
MODEL=大模型名称
DEEPSEEK_URL=Deepseek API地址
DEEPSEEK_API_KEY=Deepseek API Key
```

### 2. Docker 一键部署

```bash
docker-compose up --build
```

服务将默认运行在 `8002` 端口（容器内为 8000）。

### 3. 本地开发运行

```bash
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## API 说明

### POST /upload

- **请求体**（JSON）:
  ```json
  {
    "public_url": "文件公网可访问地址",
    "user_id": "用户ID"
  }
  ```
- **返回**:
  - 成功: `{ "status": "success", "message": "Processed ..." }`
  - 失败: HTTP 500 + 错误信息

## 处理流程

1. 接收上传请求，记录日志。
2. 根据文件类型（图片/PDF）调用对应 OCR 方法。
3. 使用大模型 API 进行内容识别和字段抽取。
4. 清洗、校验字段，生成唯一 hash_id。
5. 组装数据，写入 Supabase 数据库。
6. 返回处理结果。

