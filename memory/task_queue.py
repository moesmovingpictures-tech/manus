import asyncio
import collections

class DebouncedTaskQueue:
    def __init__(self, delay_seconds=5, max_queue_size=10):
        self.queue = collections.deque()
        self.delay_seconds = delay_seconds
        self.max_queue_size = max_queue_size
        self._processing_task = None
        self._last_activity_time = asyncio.get_event_loop().time()

    async def add_task(self, func, *args, **kwargs):
        self.queue.append((func, args, kwargs))
        if len(self.queue) > self.max_queue_size:
            await self._process_queue_now()
        else:
            self._last_activity_time = asyncio.get_event_loop().time()
            if not self._processing_task or self._processing_task.done():
                self._processing_task = asyncio.create_task(self._debounce_and_process())

    async def _debounce_and_process(self):
        while True:
            await asyncio.sleep(self.delay_seconds)
            current_time = asyncio.get_event_loop().time()
            if current_time - self._last_activity_time >= self.delay_seconds:
                await self._process_queue_now()
                break # Exit after processing if no new tasks were added

    async def _process_queue_now(self):
        if not self.queue:
            return
        print(f"Processing {len(self.queue)} debounced tasks...")
        tasks_to_process = []
        while self.queue:
            tasks_to_process.append(self.queue.popleft())
        
        for func, args, kwargs in tasks_to_process:
            try:
                await func(*args, **kwargs)
            except Exception as e:
                print(f"Error processing debounced task {func.__name__}: {e}")
        print("Debounced tasks processed.")

# Global instance for background tasks
background_task_queue = DebouncedTaskQueue(delay_seconds=10, max_queue_size=5)


