import argparse
import os
import sys

import requests
from dotenv import load_dotenv

from src.video_stream_processor import VideoStreamProcessor
from src.util.logconf import logging

load_dotenv()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

if __name__ == "__main__":
    sys_argv = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--monitor',
        help="Monitor video",
        action='store_true',
        default=False,
    )
    cli_args = parser.parse_args(sys_argv)
    
    try:
        response = requests.get(os.getenv("API_URL") + 'cameras-with-zones/')
        data = response.json()
        log.info(f'Получено камер: {len(data)}')
    except Exception:
        log.error(f'Ошибка ответа: {response.status_code}')
    
    try:
        stream = VideoStreamProcessor(data, cli_args.monitor)
        stream.run()
    except KeyboardInterrupt:
        log.info(' Завершение по Ctrl+C')
    # except Exception as e:
    #     log.error(e)
    finally:
        log.info('Система выключена')