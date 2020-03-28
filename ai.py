import assign
import discord
import join
import respond
import storage
import emote
import sys
import drone_mode

bot = discord.ext.commands.Bot('')

# register Cogs
bot.add_cog(join.Join(bot))
bot.add_cog(assign.Assign(bot))
bot.add_cog(respond.Respond(bot))
bot.add_cog(emote.Emote(bot))
bot.add_cog(drone_mode.Drone_Mode(bot))
# bot.add_cog(storage.Storage(bot))

bot.run(sys.argv[1])
