"""Base cron."""

from abc import ABC, abstractmethod
from asyncio import sleep as asyncio_sleep
from typing import Any

from app.core.config import AppConfig


class BaseCron(ABC):
    """Base cron class providing a structure for cron jobs.

    This class serves as a base for creating cron jobs that run at regular intervals.
    Subclasses must implement the `_cron_func` method.
    """

    async def run(self, interval: float) -> None:
        """Run the cron job with a specified interval.

        Args:
            interval (float): The time interval in seconds between each execution of the cron function.

        """
        while True:
            await self._cron_func()
            await asyncio_sleep(interval)

    @classmethod
    @abstractmethod
    async def create_and_run(cls, config: AppConfig, interval: float, *args: Any, **kwargs: Any) -> None:
        """Create and run a cron job instance.

        Args:
            config (AppConfig): The application configuration object.
            interval (float): The time interval in seconds between each execution of the cron function.
            *args (Any): Additional positional arguments for initialization.
            **kwargs (Any): Additional keyword arguments for initialization.

        """
        raise NotImplementedError

    @abstractmethod
    async def _cron_func(self) -> None:
        """The cron function to be implemented by subclasses.

        This method should contain the logic that needs to be executed at each interval.
        """
        raise NotImplementedError
