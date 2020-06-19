from discord.ext import commands
from ESEA_scraper import EseaScraper

class ESEA_cog:

    def __init__(self, client):
        self.bot = client

    """
    .esea command
    retrieve basic player information from play.esea.net, format, reply in Discord
    """
    @commands.command(pass_context=True, no_pm=False)
    async def esea(self, ctx, esea_username, *args):
        scraper = EseaScraper()
        placeholder = await self.bot.say('_Attempting to retrieve info for {} . . ._'.format(esea_username))

        #TODO
        #bad way to organize data, clean up in future
        opts = {
            'all_values': False,  # return all values scraped from profile
            'specific_value': False,
            'specific_value_key': None,
            'specific_values': False,
            'specific_values_keys': [],
            'header': True,
            'profile_info': True,
            'buddies': False,
        }

        for arg in args:
            if arg in scraper.single_keys:  # then we want to send back a single value
                opts['specific_values'] = False
                opts['specific_value'] = True
                opts['specific_value_key'] = arg
                break

            elif arg[1:] in scraper.single_keys:  # assuming no single keys, we want to send back several specific values
                if arg[1:] in scraper.info['profileTab']['profile']:
                    opts['profile_info'] = False

                opts['specific_values'] = True
                opts['specific_values_keys'].append(arg[1:])

            # else, we send back the default values

        info = scraper.scrape_esea(esea_username, opts)

        await self.bot.delete_message(placeholder)
        await self.bot.say(ctx.message.author.mention + '\n' + info)
