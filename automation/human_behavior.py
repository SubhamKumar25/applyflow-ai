"""Human-like behavior utilities — random delays, typing simulation, mouse movements,
scroll patterns. Used by all platform adapters to avoid bot detection."""
from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Page


async def human_delay(min_ms: int = 800, max_ms: int = 2500) -> None:
    """Random pause to mimic human reading/thinking time."""
    await asyncio.sleep(random.uniform(min_ms, max_ms) / 1000.0)


async def human_type(page: "Page", selector: str, text: str) -> None:
    """Type text with realistic per-character delay, occasional pauses."""
    element = await page.wait_for_selector(selector, timeout=10000)
    if not element:
        raise RuntimeError(f"Could not find selector: {selector}")
    await element.click()
    await human_delay(100, 400)

    for ch in text:
        await element.type(ch, delay=random.uniform(50, 180))
        # Occasionally pause as if thinking
        if random.random() < 0.04:
            await human_delay(300, 900)


async def human_scroll(page: "Page", direction: str = "down", steps: int = 4) -> None:
    """Scroll the page in small, irregular increments."""
    for _ in range(steps):
        delta = random.randint(150, 450) * (1 if direction == "down" else -1)
        await page.mouse.wheel(0, delta)
        await human_delay(400, 1200)


async def human_click(page: "Page", selector: str, timeout: int = 10000) -> None:
    """Move to element with a small offset, then click."""
    element = await page.wait_for_selector(selector, timeout=timeout)
    if not element:
        raise RuntimeError(f"Could not find selector: {selector}")
    box = await element.bounding_box()
    if box:
        x = box["x"] + box["width"] / 2 + random.uniform(-5, 5)
        y = box["y"] + box["height"] / 2 + random.uniform(-3, 3)
        await page.mouse.move(x, y, steps=random.randint(5, 15))
        await human_delay(150, 500)
    await element.click()


async def random_jitter(page: "Page") -> None:
    """Tiny mouse movement to look alive."""
    x = random.randint(100, 800)
    y = random.randint(100, 600)
    await page.mouse.move(x, y, steps=random.randint(3, 8))
    await human_delay(200, 700)
