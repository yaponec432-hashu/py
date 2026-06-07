#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
"""A discord bot."""

from asyncio import wait_for, Runner
from os import environ
from uvloop import new_event_loop
from discord import (
    Intents,
    Client,
    Embed,
    Color,
    Game,
    ClientUser,
    Message,
    Member,
    HTTPException,
    RateLimited,
    Forbidden
)

class SlaveBot(Client):
    user: ClientUser
    def __init__(self) -> None:
        activity = Game("я робот долбаеб")
        intents = Intents.default()
        intents.message_content = True
        super().__init__(
            intents=intents,
            activity=activity,
            max_ratelimit_timeout=30.0,
            chunk_guilds_at_startup=False)
        self.master_id = int(environ["MASTER_ID"])
        self.sekai_code_len = 5

    async def on_message(self, message: Message) -> None:
        """Backup sekai room code highlighting."""
        if not is_master(message.author):
            return
        message_text = message.content
        if message_text[0] != "z":
            return
        name = message_text[1:]
        channel = message.channel
        channel_name = channel.name
        if name == channel_name:
            return
        new_code = name[-self.sekai_code_len:]
        try:
            content = None
            description = f"# `{new_code}`"
            embed = Embed(description=description, color=Color.green())
            async with channel.typing():
                await wait_for(channel.edit(name=name), timeout=2.0)
        except (TimeoutError, RateLimited, HTTPException):
            content = (
                f"# :warning: Используй эту команду:\n```%rm {new_code}```"
            )
            embed = None
        except Forbidden:
            content = None
            description = "**У меня нет прав** на управление каналами"
            embed = Embed(description=description, color=Color.red())
        await message.reply(content=content, embed=embed, mention_author=False)

bot = SlaveBot()

def is_master(author: Member) -> bool:
    return author.bot and author.id == bot.master_id

async def main() -> None:
    token = environ["SLAVE_TOKEN"]
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    with Runner(loop_factory=new_event_loop) as runner:
        runner.run(main())
