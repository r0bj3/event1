from discord.ext import commands
from datetime import datetime, timedelta
import discord
from data.event import Event
import random
import string
import asyncio
import data.data as data


def generate_code():
    return ''.join(random.choices(string.digits, k=4))


class Manager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.events = []
        self.bot.loop.create_task(self.check_events())

    @commands.group(pass_context=True)
    async def event(self, ctx):
        """Says if a user is cool.
        In reality this just checks if a subcommand is being invoked.
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))

    @event.command(pass_context=True)
    async def create(self, ctx):
        """<Title> Creates a new event"""
        author = ctx.message.author
        channel = ctx.message.channel

        await self.bot.say('Ok, let\'s start. Give me the title.')
        title_message = await self.bot.wait_for_message(timeout=30, author=author, channel=channel)
        if title_message is None:
            await self.bot.say('Timeout! Please, start creating the event again.')
            return
        title = title_message.content
        await self.bot.say('Give me the date of your event with this format'
                           'Hours:Minutes day-month-days, for example, 10:00 10-10-2018')
        start_date_text = await self.bot.wait_for_message(timeout=60, author=author, channel=channel)
        if start_date_text is None:
            await self.bot.say('Timeout! Please, start creating the event again.')
            return

        start_date = datetime.strptime(start_date_text.content, '%H:%M %d-%m-%Y')

        await self.bot.say('Give me the date of your deadline, with this format, N for not having one: '
                           'Hours:Minutes day-month-days, for example, 10:00 10-10-2018')
        deadline_text = await self.bot.wait_for_message(timeout=60, author=author, channel=channel)
        if deadline_text is None:
            await self.bot.say('Timeout! Please, start creating the event again.')
            return
        if deadline_text.content == 'N':
            deadline = start_date
        else:
            deadline = datetime.strptime(deadline_text.content, '%H:%M %d-%m-%Y')

        await self.bot.say('Now give me the duration in hours')
        duration_message = await self.bot.wait_for_message(timeout=30, author=author, channel=channel)
        if duration_message is None:
            await self.bot.say('Timeout! Please, start creating the event again.')
            return
        duration = duration_message.content

        await self.bot.say('Now give me the max members')
        max_message = await self.bot.wait_for_message(timeout=30, author=author, channel=channel)
        if max_message is None:
            await self.bot.say('Timeout! Please, start creating the event again.')
            return
        max_members = max_message.content

        await self.bot.say('Now give me the description')
        description_message = await self.bot.wait_for_message(timeout=60, author=author, channel=channel)
        if description_message is None:
            await self.bot.say('Timeout! Please, start creating the event again.')
            return
        description = description_message.content

        await self.bot.say('Now give me the tags, separate them with spaces. Type N if you do not want any tag')
        tags_message = await self.bot.wait_for_message(timeout=45, author=author, channel=channel)
        if tags_message is None:
            await self.bot.say('Timeout! Please, start creating the event again.')
            return
        if tags_message.content is 'N':
            tags = None
        else:
            tags = tags_message.content.split(' ')

        code = generate_code()
        self.events.append(Event(code=code, creator=author.id, title=title, start_date=start_date,
                                 duration_time=duration, max_members=max_members, text=description, deadline=deadline,
                                 tags=tags))

        embed = discord.Embed(title=code + ' - ' + title, description=description, color=0X2971e5)
        embed.add_field(name='Start date', value=start_date.strftime('%I:%M%p %d-%m-%Y'))
        embed.add_field(name='Duration', value=duration + ' hours')
        embed.add_field(name='Max members', value=max_members)
        embed.add_field(name='Tags', value=tags_message.content)
        await self.bot.send_message(channel, embed=embed)
        await self.bot.say('Event created!')

    @event.command(pass_context=True)
    async def show(self, ctx, event_id=None):
        if event_id is None:
            output = '**Event list**\n'
            if self.events.__len__() == 0:
                await self.bot.say('There are no events right now. Why don\'t you create one?')
                return
            output += '\n'.join(str(event) for event in self.events)
            await self.bot.say(output)
            return

        for event in self.events:
            if event.code == event_id:
                embed = discord.Embed(title=event.code + ' - ' + event.title, description=event.text, color=0X2971e5)
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                embed.add_field(name='Start date',
                                value=days[event.start_date.weekday()] + ' ' + event.start_date.strftime(
                                    '%I:%M%p %d-%m-%Y'))
                embed.add_field(name='Duration', value=event.duration_time + ' hours')
                embed.add_field(name='Tags', value=' '.join(event.tags))
                creator = discord.utils.get(ctx.message.server.members, id=event.creator)
                embed.add_field(name='Creator', value=creator.display_name)
                embed.add_field(name='Max members', value='{} / {}'.format(event.participants.__len__(),
                                                                           event.max_members))
                members_text = ''
                if event.participants.__len__() == 0:
                    members_text = 'No one'
                for member_id in event.participants:
                    member = discord.utils.get(ctx.message.server.members, id=member_id)
                    members_text += member.display_name + '\n'

                embed.add_field(name='Participants', value=members_text, inline=False)
                await self.bot.send_message(ctx.message.channel, embed=embed)
                return
        await self.bot.say('Event ID not found, please, use ``!event show`` for seeing the correct ID and'
                           'try again!')

    @event.command(pass_context=True)
    async def join(self, ctx, event_id):
        for event in self.events:
            if event.code == event_id:
                if event.participants.__len__() == event.max_members:
                    await self.bot.say('Sorry, but the max capacity has been reached!')
                    return
                if ctx.message.author.id in event.participants:
                    await self.bot.say('You already are inscribed!')
                    return
                now = datetime.now()
                if now > event.deadline:
                    await self.bot.say('Sorry, but the deadline has been passed')
                    return
                event.participants.append(ctx.message.author.id)
                await self.bot.say('You are now inscribed!')
                return
        await self.bot.say('Event ID not found, please, use ``!event show`` for seeing the correct ID and'
                           'try again!')

    @event.command(pass_context=True)
    async def leave(self, ctx, event_id):
        for event in self.events:
            if event.code == event_id:
                if ctx.message.author.id not in event.participants:
                    await self.bot.say('You are not inscribed!')
                    return
                event.participants.remove(ctx.message.author.id)
                await self.bot.say('Event leaved!!')
                return
        await self.bot.say('Event ID not found, please, use ``!event show`` for seeing the correct ID and'
                           'try again!')

    @event.command(pass_context=True)
    async def delete(self, ctx, event_id):
        remove_event = None
        for event in self.events:
            if event.code == event_id:
                if not ctx.message.author.id == ctx.message.author.id:
                    await self.bot.say('You are not the creator!')
                    return
                remove_event = event
                await self.bot.say('Event removed!!')
        if remove_event is not None:
            self.events.remove(remove_event)
        else:
            await self.bot.say('Event ID not found, please, use ``!event show`` for seeing the correct ID and'
                               'try again!')

    async def check_events(self):
        while not self.bot.is_closed:
            await asyncio.sleep(5)
            now = datetime.now()
            old_events = []
            for event in self.events:
                if event.start_date < now:
                    old_events.append(event)
                    for participant in event.participants:
                        member = discord.utils.get(data.server.members, id=participant)
                        await self.bot.send_message(member, '{} has started! GO!'.format(event.title))

                minuti_30: datetime = event.start_date - timedelta(minutes=30)
                now = datetime.now()
                if minuti_30.year == now.year and minuti_30.month == now.month and now.day == minuti_30.day \
                        and minuti_30.hour == now.hour and minuti_30.minute == now.minute:
                    for participant in event.participants:
                        member = discord.utils.get(data.server.members, id=participant)
                        await self.bot.send_message(member, 'Only 30 minutes remaining for {}, prepare yourself!!'
                                                    .format(event.title))
            for old_event in old_events:
                self.events.remove(old_event)


def setup(bot: commands.Bot):
    bot.add_cog(Manager(bot))
