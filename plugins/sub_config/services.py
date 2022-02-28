from utils.config_util import SubConfig

c_schedule_sub = SubConfig('cs_sub')
honor_sub = SubConfig('honor_sub')
good_night = SubConfig('night_sub')

key_words = {'每日课表': c_schedule_sub,
             '龙王提醒': honor_sub,
             '熄灯提醒': good_night}
