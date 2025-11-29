from typing import Optional
import os
import base64

import aiohttp
import asyncio
from dotenv import load_dotenv
import numpy as np
import cv2

from ..util.logconf import logging
from ..data.model import Table, Status

logger = logging.getLogger(__name__)
load_dotenv()


class AsyncApiClient:
    def __init__(self, web_url: str, classify_url: str, timeout: int = 10):
        self.web_url = web_url
        self.classify_url = classify_url
        self.timeout = timeout
    
    async def start_table_session(self, table: Table) -> bool:
        try:
            data = {'table_id': table.id}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.web_url}arrival/",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 201:
                        response_data = await response.json()
                        table.session_id = response_data.get('id')
                        table.status = Status.Await
                        logger.debug(
                            f"Session started for table {table.id}")
                        return True
                    else:
                        text = await response.text()
                        logger.error(f"Failed to start session for table {table_id}: {response.status} - {text}")
                        
                        return False
        except asyncio.TimeoutError:
            logger.error(f"API request timeout for table {table.id}")
            return False
        except Exception as e:
            logger.error(f"API request failed for table {table.id}: {str(e)}")
            return False
    
    async def check_table_clean(self, img: np.ndarray) -> bool:
        try:
            _, buffer = cv2.imencode('.jpg', img)
            image_bytes = buffer.tobytes()
            
            form_data = aiohttp.FormData()
            form_data.add_field(
                'image',
                image_bytes,
                filename='image.jpg',
                content_type='image/jpeg'
            )
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.classify_url,
                    data=form_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        pred = response_data.get('prediction')
                        return pred
                    else:
                        text = await response.text()
                        logger.error(f"Failed check clean for table: {response.status} - {text}")
                        
                        return 'dirty'
        except asyncio.TimeoutError:
            logger.error("API request timeout for table")
            return 'dirty'
        except Exception as e:
            logger.error(f"API request failed for table: {str(e)}")
            return 'dirty'


api_client = AsyncApiClient(os.getenv('WEB_API_URL'),
                            os.getenv('CLASSIFY_API_URL'))