from sopel import  *
from extract_blade_info import query_bhq_knife,KnifeFormatter

@module.commands('knife')
def knife(bot, trigger):
    query = trigger.group(2)
    d = ddg()
    url = d.query(query, site="bladehq.com")
    knife = query_bhq_knife(url)
    if not knife:
        bot.reply('Sorry I didn\'t find anything at {url}'.format(url=url))
    else:
        d = replaceDictKeys(BHQNAME_TO_DBNAME,knife)
        kf = KnifeFormatter()
        results_string = kf.formattedKnife(d)
        bot.reply(results_string)

