import re
import json
import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any
import logging



logger = logging.getLogger(__name__)


def clean_and_parse_json(text: str) -> dict:
    logger.info("Cleaning and parsing JSON text.")
    try:
        # 尝试清洗 Markdown 代码块 ```json 或 ``` 包裹的内容
        cleaned = re.sub(r"^```(?:json|python)?\n", "", text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"\n```$", "", cleaned.strip())
        # 加载为 JSON 字典
        result = json.loads(cleaned)
        logger.info("JSON parsed successfully.")
        return result
    except Exception as e:
        logger.exception(f"Failed to clean and parse JSON: {str(e)}")
        raise


class ReceiptDataPreparer:
    def __init__(self, fields: str, user_id: str, public_url: str, ocr: str):
        self.fields = fields
        self.user_id = user_id
        self.public_url = public_url
        self.ocr = ocr

        self.record_id = str(uuid.uuid4())

        # 解析字段
        self.items = self.parse_fields()

    def parse_fields(self) -> Dict[str, Any]:
        """清洗字段并返回 dict"""
        logger.info("Parsing and cleaning fields for receipt data.")
        try:
            items = clean_and_parse_json(self.fields)
        except Exception as e:
            logger.exception(f"Failed to parse fields: {str(e)}")
            raise ValueError(f"Failed to parse fields: {e}")

        # 生成 hash_id，防重复
        hash_input = "|".join([
            str(self.user_id),
            str(items.get("invoice_total", "")),
            str(items.get("buyer", "")),
            str(items.get("seller", "")),
            str(items.get("invoice_date", "")),
            str(items.get("invoice_number", ""))
        ])

        items["hash_id"] = hashlib.md5(hash_input.encode()).hexdigest()
        logger.info(f"Generated hash_id for receipt: {items['hash_id']}")
        return items

    def build_receipt_data(self) -> Dict[str, Any]:
        logger.info("Building receipt data dictionary.")
        try:
            data = {
                "id": self.record_id,
                "user_id": self.user_id,
                "file_url": self.public_url,
                "original_info": "from_n8n_listener",
                "ocr": self.ocr,
                "create_time": datetime.utcnow().isoformat(),
                **self.items  # 合并提取字段
            }
            logger.info("Receipt data built successfully.")
            return data
        except Exception as e:
            logger.exception(f"Failed to build receipt data: {str(e)}")
            raise

