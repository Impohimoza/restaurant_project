import argparse
import os
import sys

import asyncio
import signal
import requests
from dotenv import load_dotenv

from src.video_stream_processor import VideoStreamProcessor
from src.util.logconf import logging

load_dotenv()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Application:
    def __init__(self):
        self.video_processor = None
        self.is_running = False
        self.shutdown_event = asyncio.Event()
    
    async def startup(self, data, monitor):
        self.video_processor = VideoStreamProcessor(data, monitor)
        
        self.is_running = True
    
    async def shutdown(self):
        """Корректное завершение приложения"""
        log.info("Shutting down application...")
        self.is_running = False
        
        if self.video_processor:
            await self.video_processor.stop()
        
        log.info("Application shutdown complete")
        self.shutdown_event.set()
    
    def handle_signal(self):
        """Обработчик сигналов завершения"""
        log.info("Received shutdown signal")
        # Создаем асинхронную задачу для shutdown
        asyncio.create_task(self.shutdown())
    
    async def run(self, data, monitor):
        await self.startup(data, monitor)
        
        try:
            loop = asyncio.get_running_loop()
            for sig in [signal.SIGTERM, signal.SIGINT]:
                loop.add_signal_handler(sig, self.handle_signal)
            
            await self.video_processor.start()
        except KeyboardInterrupt:
            log.info(' Завершение по Ctrl+C')
        except Exception as e:
            log.info(f'Application error: {e}')
        finally:
            if self.is_running:
                await self.shutdown()
        
        await self.shutdown_event.wait()
        
        
async def main(cli_args):
    
    try:
        response = requests.get(os.getenv("API_URL") + 'cameras-with-zones/')
        data = response.json()
        log.info(f'Получено камер: {len(data)}')
    except Exception:
        log.error(f'Ошибка ответа: {response.status_code}')

    app = Application()
    await app.run(data, cli_args.monitor)

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
        asyncio.run(main(cli_args))
    except KeyboardInterrupt:
        print("Application terminated by user")
        sys.exit(1)
        