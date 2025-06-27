from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from datetime import datetime
import os
from file_ocr_upload.main import upload_to_supabase  

# 创建logs目录
os.makedirs('logs', exist_ok=True)

# 配置日志格式和存储
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)



# 初始化 FastAPI
app = FastAPI()

# 请求体数据结构
class UploadRequest(BaseModel):
    public_url: str
    user_id: str

@app.post("/upload")
async def upload_handler(req: UploadRequest):
    logger.info(f"📩 Received upload request: {req.public_url} from user {req.user_id}")
    try:
        # 调用同步处理函数（OCR + Supabase 写入）
        upload_to_supabase(req.public_url, req.user_id)
        return {"status": "success", "message": f"Processed {req.public_url}"}
    except Exception as e:
        logger.exception("❌ Error processing upload")
        raise HTTPException(status_code=500, detail=str(e))
