from sopel import  *
from ddg import ddg
from extract_blade_info import query_bhq_knife,KnifeFormatter

@module.commands('knife')
def knife(bot, trigger):
    query = trigger.group(2)
    d = ddg()
    d.query(query, site="bladehq.com")
    #use the first result
    if not d.results:
        bot.reply("I couldn't find anything with the search term {}".format(query))
        return
    url = d.results[0]
    knife = query_bhq_knife(url)
    if not knife:
        bot.reply('Sorry I didn\'t find anything at {url}'.format(url=url))
    else:
        d = replaceDictKeys(BHQNAME_TO_DBNAME,knife)
        kf = KnifeFormatter()
        results_string = kf.formattedKnife(d)
        bot.reply(results_string)

