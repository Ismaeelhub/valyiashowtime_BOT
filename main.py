import telebot
import json
import requests
import telegram

TMDB_API = "5307bf927319fafbb85a482634b37473"
old = '1004646133:AAFan1Fh3Ke4KsiEcmiCYbTkUBSe5WO9WZc'
bot = telebot.TeleBot("5023163546:AAENN6w5oJXRB4594-Nu-ihMc3YjmOj4Gww")
types = telebot.types
data_ids = []
data_names = []
data_types = []
type = ''
MY_CHAT_ID = 156956400
def search_in_valyria(key):
    return f"https://stoic-poitras-d9ed33.netlify.app/search/{key}"
def image_handler(url):
    return f'https://image.tmdb.org/t/p/original{url}'
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "https://stoic-poitras-d9ed33.netlify.app/Home")
# @bot.message_handler(commands=['search'])
# def search(message):
#     welcome = bot.reply_to(message, "Type World here")
#     bot.register_next_step_handler( welcome, Searching )


def Searching(message):
    data = requests.get(
        f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API}&language=en-US&page=1&include_adult=false&query={message.text}" ).text
    for i in json.loads(data)['results']:
        try:
            print(i['original_title'])
            bot.send_message(message.chat.id, i['original_title'])
        except KeyError:
            print(i['name'])
            bot.send_message(message.chat.id, i['name'])
    print(f"==>{message.text}")
    bot.send_message(message.chat.id, search_in_valyria(message.text))

@bot.message_handler(commands=['search'])
def Search(message):
    name = bot.reply_to(message, "Send The Name Movie, TVShow and Actors")
    bot.register_next_step_handler(name, pack_in_btns)
    bot.send_message(MY_CHAT_ID, str(message.json))
    print(f"==>Search")

@bot.message_handler(commands=['trending'])
def Trending(message):
    keyboard = types.InlineKeyboardMarkup()
    data_ids.clear()
    data_names.clear()
    data_types.clear()
    day = types.InlineKeyboardButton( text='Day', callback_data='day' )
    week = types.InlineKeyboardButton( text='Week', callback_data="week" )
    keyboard.add( day )
    keyboard.add( week )
    bot.send_message(MY_CHAT_ID, str(message.json))
    print(f"==>Trending")

    bot.send_message( message.chat.id, "Choose one:", reply_markup=keyboard )
@bot.message_handler(commands=['most_popular'])
def popular(message):
    keyboard = types.InlineKeyboardMarkup()
    moviek = types.InlineKeyboardButton( text='Movies', callback_data='movie' )
    keyboard.add( moviek )
    tv = types.InlineKeyboardButton( text='TVShows', callback_data='tv')
    keyboard.add(tv)
    print(f"==>Popular")
    bot.send_message( message.chat.id, "Choose one:", reply_markup=keyboard )
    bot.send_message(MY_CHAT_ID, str(message.json))
def get_data(message):
    data = requests.get(
        f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API}&language=en-US&page=1&include_adult=false&query={message.text}" ).text
    for n, movie in enumerate(json.loads( data )['results']):
        id = movie['id']
        if movie['media_type'] == "movie":
            base_type = 'original_title'
        if movie['media_type'] == 'tv':
            base_type = 'name'
        if movie['media_type'] == "person":
            base_type = "name"

        name = movie[base_type]
        data_names.append(name)
        data_ids.append(movie['id'])
        data_types.append(movie['media_type'])


    return data_names
def runtime_handle(arr):
    count = 0
    for i in arr:
        count+=i
    return count / len(arr)
def format_Time(time):
    if time > 60:
        hours = time / 60
        if time %60 > 9:
            res = time %60
        else:
            res = f"0{time%60}"
        time = f"{int(hours)}:{res}"
    else:
        time = time
    return time

def get_details(msgid, id, type):
    res = requests.get(f"https://api.themoviedb.org/3/{type}/{id}?api_key={TMDB_API}&language=en-US&append_to_response=external_ids`").text
    data = json.loads(res)
    if len(data) > 0:
        clock_list = ['🕐', '🕑', '🕒', '🕓', '🕔']
        genres = ''
        if type == "movie":
            name = f"🎥{data['original_title']}🎥"
            seasons = ""
            episodes = ""
            started = f"{data['release_date']}"
            runtime = f"{clock_list[int( data['runtime'] / 60 ) - 1]}{format_Time( int( data['runtime'] ) )}{clock_list[int( data['runtime'] / 60 ) - 1]}"
            network = f" Produced by {data['production_companies'][0]['name']}" if len(data['production_companies']) > 0 else ''
            for gen in data['genres']:
                genres += f" {gen['name']}"
            tagline = f"🎤<i>{data['tagline']}</i>🎤" if len( data['tagline'] ) > 0 and data['tagline'] != 'null' else ''
            votes = f"⭐{data['vote_average']} / 10 ({data['vote_count']}) Votes⭐"
            desc = f"📝{data['overview']}📝"
            poster = data['poster_path']
            backdrop = data['backdrop_path']
        if type == "tv":
            name = f"📺{data['name']}📺"
            seasons = f"{data['number_of_seasons']} Season"
            episodes = f"{data['number_of_episodes']} Episodes"
            started = f"{data['first_air_date']} ➡️{data['last_air_date']}"
            runtime = int( runtime_handle( data['episode_run_time'] ) )
            tagline = f"🎤<i>{data['tagline']}</i>🎤" if len( data['tagline'] ) > 0 and data['tagline'] != 'null' else ''
            network = f" Produced by {data['networks'][0]['name']}"
            desc = f"📝{data['overview']}📝"
            poster = data['poster_path']
            backdrop = data['backdrop_path']
            votes = f"⭐{data['vote_average']} / 10 ({data['vote_count']}) Votes⭐"

        if type == "person":
            name = f"👱{data['name']}👱‍" if data['gender'] == 1 else  f"👱‍{data['name']}👱‍‍"
            desc = data['biography']
            seasons = data['birthday']
            episodes = data['deathday'] if data['deathday'] != 'null' or data['deathday'] != 'None' else ''
            poster = data['profile_path']
            tagline = data['known_for_department']
            network = data['place_of_birth']
            votes, runtime, started = '', '', ''
            try:

                backdrop = data['backdrop_path']
            except KeyError:
                backdrop = ''
        print( f"==>{name}" )
        msg = f"""<a href='{data['homepage']}'><b>{name}</b></a>:\r\n
        ----------------------------\r\n{desc}\r\n{tagline}\r\n{votes}\r\n{runtime}\r\n{seasons}\r\n{episodes}\r\n{started}\r\n{network}\r\n
        """
        if len(msg) > 1024:
            bot.send_message(msgid, msg,  parse_mode=telegram.constants.PARSEMODE_HTML)
            if poster != '':
                bot.send_photo( msgid, image_handler( poster ) )
        else:
            bot.send_photo( msgid, image_handler(poster ), msg,  parse_mode=telegram.constants.PARSEMODE_HTML)
        if backdrop != '':
            bot.send_photo( msgid, image_handler( backdrop ) )
        bot.send_message( msgid, f"https://stoic-poitras-d9ed33.netlify.app/Movie/{type}/{data['id']}" )

def pack_in_btns(message):
    keyboard = types.InlineKeyboardMarkup()
    data_ids.clear()
    data_names.clear()
    data_types.clear()
    for n, d in enumerate(get_data(message)):
        button_x64 = types.InlineKeyboardButton( text=data_names[n], callback_data=f"{data_ids[n]}*|*{data_types[n]}" )
        keyboard.add( button_x64 )
    bot.send_message( message.chat.id,"Choose one:", reply_markup=keyboard )
def datas_handler(id, data):
    for n, movie in enumerate(data['results']):
        poster = movie['poster_path'] if movie['poster_path'] != 'null' and movie['poster_path'] != '' else ''
        votes = f"⭐{movie['vote_average']}⭐" if movie['vote_average'] != 'null' and movie['vote_average'] != '' else ''
        desc = f"📝{movie['overview']}📝" if movie['overview'] != 'null' and movie['overview'] != '' else ''
        try:  # movie
            name = f"🎥{movie['original_title']}🎥"
            release_date = movie['release_date'] if movie['release_date'] != 'null' and movie['release_date'] != '' else ''
            url = f"------https://stoic-poitras-d9ed33.netlify.app/Movie/movie/{movie['id']}"
        except KeyError:  # tv
            name = f"📺{movie['original_name']}📺"
            release_date = movie['first_air_date'] if movie['first_air_date'] != 'null' and movie['first_air_date'] != '' else ''
            url = f"------https://stoic-poitras-d9ed33.netlify.app/Movie/tv/{movie['id']}"

        msg = f"""#{n+1}{name}\r\n{release_date}\r\n{votes}\r\n{desc}\r\n{url}"""
        if len( msg ) > 1024:
            bot.send_message( id, msg, parse_mode=telegram.constants.PARSEMODE_HTML )
            if poster != '' and poster != 'null':
                bot.send_photo( id, image_handler( poster ) )
        else:
            bot.send_photo( id, image_handler( poster ), msg, parse_mode=telegram.constants.PARSEMODE_HTML )
        if movie['backdrop_path'] != '' and movie['backdrop_path'] != 'null':
            bot.send_photo( id, image_handler( movie['backdrop_path'] ) )
    bot.send_message(id, "End Results...")
@bot.callback_query_handler( func=lambda call: True )
def callback_worker(call):
    bot.send_message( MY_CHAT_ID, f"{str( call.message.json)} ")
    if call.data.find("*|*") > -1:
        datas = call.data.split("*|*")
        print(datas)
        print(call.message.chat.id)
        get_details(call.message.chat.id, datas[0], datas[1])
    if call.data == "day" or call.data == "week":
        datas = requests.get(f"https://api.themoviedb.org/3/trending/all/{call.data}?api_key={TMDB_API}").text
        data = json.loads(datas)
        datas_handler(call.message.chat.id, data)
    if call.data == 'movie' or call.data == 'tv':
        datas = requests.get(f"https://api.themoviedb.org/3/discover/{call.data}?api_key={TMDB_API}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_watch_monetization_types=flatrate").text
        data = json.loads(datas)
        datas_handler(call.message.chat.id, data)

bot.polling()
