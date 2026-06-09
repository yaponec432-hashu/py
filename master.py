#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
"""A discord bot."""

from asyncio import wait_for, Runner
from os import environ

from discord.abc import Messageable
from uvloop import new_event_loop
from discord import (
    app_commands,
    Intents,
    Client,
    Embed,
    Color,
    Game,
    Interaction,
    TextChannel,
    ClientUser,
    Message,
    Member,
    HTTPException,
    RateLimited,
    Forbidden
)


class MasterBot(Client):
    user: ClientUser

    def __init__(self) -> None:
        activity = Game("трахает робонене")
        intents = Intents.default()
        intents.message_content = True
        super().__init__(
            intents=intents,
            activity=activity,
            max_ratelimit_timeout=30.0,
            chunk_guilds_at_startup=False)
        self.tree = app_commands.CommandTree(self)
        self.sync_enabled = int(environ["BOT_SYNC_ENABLED"])
        self.channel_name_len = 8
        self.sekai_code_len = 5
        self.room_letter = "g"
        self.manager_roles = {
            "Раннер ростера",
            "Лид-менеджер",
            "Менеджер",
            "Интерн"
        }

    async def setup_hook(self) -> None:
        with open("master_id", "w") as file:
            file.write(f"{self.user.id}\n")
        if self.sync_enabled:
            await self.tree.sync()

    async def on_message(self, message: Message) -> None:
        """Highlight the sekai room code."""
        channel = message.channel
        author = message.author
        if not is_human_in_text_channel(author, channel):
            return
        message_text = message.content
        if not is_sekai_code(message_text):
            return
        channel_name = channel.name
        if message_text == channel_name[-self.sekai_code_len:]:
            return
        room_prefix = get_room_prefix(channel_name)
        if not room_prefix:
            return
        if not is_manager(author):
            return
        content = embed = None
        try:
            description = f"# `{message_text}`\nНовый код румы"
            color = Color.green()
            name = room_prefix + message_text
            async with channel.typing():
                await wait_for(channel.edit(name=name), timeout=2.0)
        except (TimeoutError, RateLimited, HTTPException):
            content = "z" + name
        except Forbidden:
            description = "**У меня нет прав** на управление каналами"
            color = Color.red()
        if not content:
            embed = Embed(description=description, color=color)
        await message.reply(content=content, embed=embed, mention_author=False)


bot = MasterBot()


@bot.tree.context_menu(name="Перевести с кристалийского")
async def translate_from_crystalian(
    ctx: Interaction,
    message: Message
) -> None:
    description = message.jump_url + "\n"
    message_text = message.content
    if message_text:
        qwerty = (
            "qwertyuiop[]asdfghjkl;'zxcvbnm,./"
            "QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?"
        )
        russian = (
            "йцукенгшщзхъфывапролджэячсмитьбю."
            "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,"
        )
        table = str.maketrans(qwerty, russian)
        description += message_text.translate(table)
        color = Color.green()
    else:
        description += "Пусто"
        color = Color.red()
    embed = Embed(description=description, color=color)
    await ctx.response.send_message(embed=embed)


@bot.tree.command(description="Данные сервака")
@app_commands.choices(
    item=[
        app_commands.Choice(name="Иконка", value="icon"),
        app_commands.Choice(name="Баннер", value="banner"),
        app_commands.Choice(name="ID", value="id")
    ]
)
@app_commands.describe(item="Докс сват спортики")
async def server_data(ctx: Interaction, item: str) -> None:
    data = + getattr(ctx.guild, item)
    content = f"```{data}```" if item == "id" else "> " + data
    await ctx.response.send_message(content=content)


@bot.tree.command(description="Данные профиля чела")
@app_commands.choices(
    item=[
        app_commands.Choice(name="Ава", value="display_avatar"),
        app_commands.Choice(name="Username", value="name"),
        app_commands.Choice(name="ID", value="id")
    ]
)
@app_commands.describe(member="Чел", item="Докс сват спортики")
async def member_data(ctx: Interaction, member: Member, item: str) -> None:
    data = getattr(member, item)
    content = "> " + data if item == "display_avatar" else f"```{data}```"
    await ctx.response.send_message(content=content)


@bot.tree.command(description="Посчитать длину строки")
@app_commands.describe(text="Пиши свою строку")
async def length(ctx: Interaction, text: str) -> None:
    description = f"Длина {len(text)}"
    embed = Embed(description=description, color=Color.green())
    await ctx.response.send_message(embed=embed)


@bot.tree.command(description="Проверить синхронизацию")
async def check_sync(ctx: Interaction) -> None:
    description = "Ага" if bot.sync_enabled else "Нет нихуя"
    embed = Embed(description=description, color=Color.green())
    await ctx.response.send_message(embed=embed)


def is_human_in_text_channel(
    author: Member,
    channel: Messageable
) -> bool:
    return not author.bot and isinstance(channel, TextChannel)


def is_sekai_code(text: str) -> bool:
    return len(text) == bot.sekai_code_len and text.isdecimal()


def is_manager(author: Member) -> bool:
    return any(role.name in bot.manager_roles for role in author.roles)


def get_room_prefix(channel_name: str) -> str:
    if len(channel_name) != bot.channel_name_len:
        return ""
    if channel_name[0] != bot.room_letter:
        return ""
    if channel_name[2] != "-":
        return ""
    room_number = channel_name[1]
    if not room_number.isdecimal():
        return ""
    return f"{bot.room_letter}{room_number}-"


async def main() -> None:
    token = environ["MASTER_TOKEN"]
    async with bot:
       await bot.start(token)


if __name__ == "__main__":
    with Runner(loop_factory=new_event_loop) as runner:
        runner.run(main())
