from typing import Optional
import os

import aiohttp
import asyncio
from dotenv import load_dotenv

from ..util.logconf import logging
from ..data.model import Table, Status

logger = logging.getLogger(__name__)
load_dotenv()


class AsyncApiClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
    
    async def start_table_session(self, table: Table) -> bool:
        try:
            data = {'table_id': table.id}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}arrival/",
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


api_client = AsyncApiClient(os.getenv('API_URL'))
