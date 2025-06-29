import os
from dotenv import load_dotenv
from supabase import create_client, Client
from file_ocr_upload.ocr import ocr_attachment, extract_fields_from_ocr
from file_ocr_upload.insert_data import ReceiptDataPreparer
import logging



load_dotenv()

url: str = os.getenv("SUPABASE_URL") or ""
key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""
supabase: Client = create_client(url, key)


logger = logging.getLogger(__name__)


def upload_to_supabase(public_url, user_id):
    logger.info(f"Starting upload_to_supabase for {public_url}")

    try:

        ocr = ocr_attachment(public_url)
        logger.info(f"Performed OCR on {public_url}.")
        fields = extract_fields_from_ocr(ocr)
        logger.info("Extracted fields from OCR.")

        preparer = ReceiptDataPreparer(fields, user_id, public_url, ocr)
        receipt_row = preparer.build_receipt_data()
        supabase.table("receipt_items_cleaned").insert(receipt_row).execute()
        logger.info("Inserted data for receipt_items_cleaned successed!")

    except Exception as e:
        error_msg = f"{public_url} - Error: {str(e)}"
        logger.info(f"Failed to process attachment: {error_msg}")
        raise  Exception(error_msg) from e

        
 