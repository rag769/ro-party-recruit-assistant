import config
import datetime
import discord
from discord.ext import commands, tasks
import json
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)


@bot.command()
async def show(ctx, event_id: int):
    event = ctx.guild.get_scheduled_event(event_id)
    if event is None:
        await ctx.send("お前の頭を精錬してやろうか！")
        return
    if not os.path.exists(f"{event.id}.json"):
        await ctx.send("クホホホホ...そのイベントは管理してないぞ")
        return
    with open(f"{event.id}.json") as f:
        d = json.load(f)

    confirmed_users = []
    waiting_users = []
    for u in d["confirmed"]:
        confirmed_users.append(ctx.guild.get_member(u).display_name)
    message = f"参加者: {confirmed_users}"

    if len(d["waiting"]) > 0:
        for u in d["waiting"]:
            waiting_users.append(ctx.guild.get_member(u).display_name)
        message += f"\nキャンセル待ち: {waiting_users}"

    await ctx.send(message)


@bot.command()
async def load(ctx, event_id: int):
    event = ctx.guild.get_scheduled_event(event_id)
    if event is None:
        await ctx.send("お前の頭を精錬してやろうか！")
        return

    d = {"confirmed": [], "waiting": []}
    n = event.name.split("@")
    limit = int(n[-1]) if len(n) > 1 else 12

    async for user in event.users():
        if len(d["confirmed"]) < limit:
            d["confirmed"].append(user.id)
        else:
            d["waiting"].append(user.id)

    with open(f"{event.id}.json", "w") as f:
        json.dump(d, f)
    await ctx.send("解析完了")


@bot.event
async def on_ready():
    job.start()


@bot.event
async def on_scheduled_event_create(event):
    if event.guild.id not in config.announce_channel:
        return

    skelton = {"confirmed": [], "waiting": []}
    with open(f"{event.id}.json", "w") as f:
        json.dump(skelton, f)


@bot.event
async def on_scheduled_event_update(before, after):
    await check_event_users(after, None, None)


@bot.event
async def on_scheduled_event_delete(event):
    if not os.path.exists(f"{event.id}.json"):
        return
    os.remove(f"{event.id}.json")


@bot.event
async def on_scheduled_event_user_add(event, user):
    await check_event_users(event, user, None)


@bot.event
async def on_scheduled_event_user_remove(event, user):
    await check_event_users(event, None, user)


async def check_event_users(
    event: discord.ScheduledEvent, add: discord.User, remove: discord.User
):
    if event.guild.id not in config.announce_channel:
        return
    if not os.path.exists(f"{event.id}.json"):
        return

    n = event.name.split("@")
    limit = int(n[-1]) if len(n) > 1 else 12
    with open(f"{event.id}.json") as f:
        d = json.load(f)

    ch = bot.get_channel(config.announce_channel[event.guild.id])

    if len(d["confirmed"]) > limit:
        for _ in range(len(d["confirmed"]) - limit):
            u = d["confirmed"].pop(-1)
            d["waiting"].insert(0, u)
            await ch.send(
                f"{event.guild.get_member(u).mention} クホホホホ...【{event.name}】定員オーバー. キャンセル待ち"
            )
    if add:
        if len(d["confirmed"]) >= limit:
            d["waiting"].append(add.id)
            await ch.send(f"{add.mention} クホホホホ...【{event.name}】定員オーバー. キャンセル待ち")
        else:
            d["confirmed"].append(add.id)
    if remove:
        if remove.id in d["waiting"]:
            d["waiting"].remove(remove.id)
        elif remove.id in d["confirmed"]:
            d["confirmed"].remove(remove.id)

    if limit > len(d["confirmed"]) and len(d["waiting"]) > 0:
        for _ in range(limit - len(d["confirmed"])):
            if len(d["waiting"]) == 0:
                break
            u = d["waiting"].pop(0)
            d["confirmed"].append(u)
            await ch.send(f"{event.guild.get_member(u).mention} 【{event.name}】精算行けます！")

    with open(f"{event.id}.json", "w") as f:
        json.dump(d, f)


@tasks.loop(minutes=1)
async def job():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+9), "JST"))
    guilds = bot.guilds
    if guilds is None:
        return

    for guild in guilds:
        if guild.id not in config.announce_channel:
            continue
        ch = bot.get_channel(config.announce_channel[guild.id])
        for event in guild.scheduled_events:
            if event.status != discord.EventStatus.scheduled:
                continue
            if not os.path.exists(f"{event.id}.json"):
                continue

            if (event.start_time - now < datetime.timedelta(minutes=30)) and (
                event.start_time - now >= datetime.timedelta(minutes=29)
            ):
                with open(f"{event.id}.json") as f:
                    d = json.load(f)
                mentions = []
                for u in d["confirmed"]:
                    mentions.append(event.guild.get_member(u).mention)
                await ch.send(
                    f"{' '.join(mentions)}\n【{event.name}】がもうすぐ開始するようだ。準備はいいかい？"
                )


bot.run(config.DISCORD_TOKEN)
