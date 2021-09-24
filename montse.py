#IMPORTS
import os
import random
from datetime import timedelta, timezone, time, datetime
import discord
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option #, create_choice
import asyncio
import youtube_dl
import urllib.parse, urllib.request, re
from discord.ext import commands, tasks
import logging

#Custom imports
import actjson
import funciones_montse as f_m
from tdform import timedeltaformatter
from pathlib import Path

#CONFIGURACION
hora_antigua = datetime.now()
start = hora_antigua
canales_habilitados= {879396354525397053}


#client = discord.Client(intents=discord.Intents.all())
Bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())

voice_client='None'
slash = SlashCommand(Bot, sync_commands=True) # Declares slash commands through the client.
guild_ids = [320694020328390666, 708283729528750171] # Put your server ID in this array.
UTC = timezone(timedelta(hours=+2))
Generales ={
  320694020328390666
}
FFMPEG_OPTIONS = {
    'options': '-vn'
}

#si nada se rompe, borrar
'''async def hora():
  while True:
      quehora = quehoraes()
      global hora_antigua
      han_pasado = quehora - hora_antigua
      tiempo = timedeltaformatter(han_pasado)
      hora_antigua = quehora
      respuesta = str(round(tiempo[3])) + " segundos"
      print(respuesta)
      await asyncio.sleep(30)
      await hora()

def quehoraes():
  hora = datetime.now()
  return hora'''

@slash.slash(name = "uptime",
  guild_ids=guild_ids)
async def uptime(ctx):
  global start
  now = datetime.now()
  elapsed = now - start
  [dias, horas, minutos, segundos] = timedeltaformatter(elapsed)
  respuesta = "Llevo conectada "
  if dias != 0:
    respuesta += str(dias) + " días, " 
  if horas!= 0:
    respuesta += str(horas) + " horas, " 
  if minutos != 0:
    respuesta += str(minutos) + " minutos, " 
  if segundos != 0:
    respuesta += str(round(segundos)) + " segundos."
  await ctx.reply(respuesta)


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

async def ensure_voice(ctx):
    if not ctx.author.voice:
        # "Fist join a Voice Channel, you man!"
        await ctx.reply("Conéctate primero a un canal de voz.", delete_after=10)
        raise Exception

@tasks.loop(seconds=4)
async def save_number_loop():
    global number
    with number_txt_file.open('w') as fp:
        fp.write(str(number))
    if len(list(waves_folder.iterdir())) > 10:
        print("Deleting recording files as the recording file's count got above 10.")
        for item in waves_folder.iterdir():
            # print(item)
            item.unlink()
        number = 0

########## UNIR ##########
@slash.slash(
  name="unir",
  description = "Montse se une al canal de voz.",
  guild_ids=guild_ids)
async def _unir(ctx):
  try:
    channel = ctx.author.voice.channel
  except Exception as ex:
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(ex).__name__, ex.args)
    print(message)
    await ctx.reply("Conéctate primero a un canal de voz.", delete_after=10)
    return
  voice = discord.utils.get(Bot.voice_clients, guild= ctx.guild)
  if voice == None:
    await channel.connect()
    await ctx.reply("Voy", delete_after=5)
  else:
    if (voice.channel == channel):
      await ctx.reply("Ya estoy en tu canal.", delete_after=5)
    else:
      await voice.move_to(channel)
      await ctx.reply("Me movi.", delete_after=5)

######################## busqueda de palabras en youtube ##########      
######################## de momento aqui se queda #################
def buscar_yt(busqueda):
    query_string = urllib.parse.urlencode({'search_query': busqueda})
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string)
    search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())  
    link = "http://www.youtube.com/watch?v=" + search_results[0]
    return link


############### PLAY PERO PUESTO DE ESTEROIDES ##########
@slash.slash(
  name="play",
  description = "Reproduce una canción.",
  guild_ids=guild_ids)
#@commands.before_invoke(ensure_voice)
async def _play(ctx, url=""):
  ##UNIRSE SI HACE FALTA
  try:
    channel = ctx.author.voice.channel
  except Exception as ex:
    print(ex)
    await ctx.reply("Conéctate primero a un canal de voz.", delete_after=10)
    return
  voice = discord.utils.get(Bot.voice_clients, guild= ctx.guild)
  if voice == None:
    await channel.connect()
  if (ctx.voice_client.is_paused()):
    ctx.voice_client.resume()
    await ctx.reply("Reanudando...", delete_after = 5)
  elif (ctx.voice_client.is_playing()):
    ###AQUI IRIA EL AÑADIR A LA QUEUE UN TEMITA
    
    if not(url.startswith("https://youtu") or url.startswith("https://www.youtu")):
      url = buscar_yt(url)
    respuesta = "Añadío a la lista:\n" + url
    await ctx.reply(respuesta)
    #######PROBANDO A DUPLICAR ESTE TROZO
    player = YTDLSource.from_url(url, loop=Bot.loop, stream=True) #await quitao
    #####apuntar en playlist
    titulo = player.title
    playlist = actjson.abrir_json('MontseApr/playlist.json') 
    longitud = len(playlist)
    tema = {'titulo': titulo, 'url': url}
    playlist[longitud+1] = tema
    actjson.actualizar_playlist(playlist)
    ###########################
  else:
    if not(url.startswith("https://youtu") or url.startswith("https://www.youtu")):
      url = buscar_yt(url)
    async with ctx.channel.typing():
      respuesta = "Reproduciendo: \n"+ url
      await ctx.reply(respuesta)
      #####apuntar en playlist
      
      player = YTDLSource.from_url(url, loop=Bot.loop, stream=True)
      titulo = player.title
      playlist = actjson.abrir_json('MontseApr/playlist.json') 
      longitud = len(playlist)
      tema = {'titulo': titulo, 'url': url}
      playlist[longitud+1] = tema
      actjson.actualizar_playlist(playlist)
      play_next(ctx)
      ###########################
puntero_playlist = 1
def play_next(ctx):
  playlist = actjson.abrir_json('MontseApr/playlist.json')
  global puntero_playlist
  puntero = "Puntero: " + str(puntero_playlist)
  print(puntero)
  if len(playlist) >= puntero_playlist:
    #get the first url
    m_url = playlist[str(puntero_playlist)]['url']
    player = YTDLSource.from_url(m_url, loop=Bot.loop, stream=True)
    ctx.voice_client.play(player, after=lambda e: play_next(ctx))
    puntero_playlist += 1
  else:
    print("Se terminó la playlist")
    return

############### PLAYLIST ##############
@slash.slash(
  name="playlist",
  guild_ids=guild_ids)
async def _playlist(ctx):
  playlist = actjson.abrir_json('MontseApr/playlist.json')
  longitud = len(playlist)
  respuesta = "Playlist: " + str(longitud) + " temas. \n"
  i = 1
  for tema in playlist:
    respuesta += tema + ". " + playlist[tema]["titulo"] + "\n"
    i += 1
  await ctx.reply(respuesta)

################-PAUSE-##################
@slash.slash(
  name="pause",
  guild_ids=guild_ids)
async def _pause(ctx):
  if ctx.voice_client.is_playing():
    ctx.voice_client.pause()
    await ctx.reply("Pausando...", delete_after = 5)

################-13ECHAR-################
@slash.slash(
  name="echar",
  description = "Montse se va del canal de voz.",
  guild_ids=guild_ids)
async def _echar(ctx):
  voice = discord.utils.get(Bot.voice_clients, guild = ctx.guild)
  if voice is not None:
    await ctx.voice_client.disconnect()
    await ctx.reply("Ok. Ya veo que sobro.",delete_after = 5)
  else:
    await ctx.reply("No me puedes echar si no estoy.",delete_after = 5)
  playlist = {}
  global puntero_playlist
  puntero_playlist = 1
  actjson.actualizar_playlist(playlist)

############### NEXT ###################
@slash.slash(
  name="next",
  guild_ids=guild_ids)
async def _next(ctx):
  respuesta = "Saltando tema..."
  await ctx.reply(respuesta, delete_after=5)
  if(ctx.voice_client.is_playing()):
    ctx.voice_client.stop()
  
############### PREV ###################
@slash.slash(
  name="prev",
  guild_ids=guild_ids)
async def _prev(ctx):
  respuesta = "Retrocediendo al tema anterior tema..."
  await ctx.reply(respuesta, delete_after=5)
  if(ctx.voice_client.is_playing()):
    ctx.voice_client.stop()
  global puntero_playlist
  puntero_playlist -= 2 #1 por cancelar el avance y 1 para retroceder
  
############### SONANDO ###################
@slash.slash(
  name="sonando",
  guild_ids=guild_ids)
async def _sonando(ctx):
  respuesta = "Sonando: \n"
  global puntero_playlist
  playlist = actjson.abrir_json('MontseApr/playlist.json')
  url = playlist[str(puntero_playlist-1)]['url']
  respuesta += url
  await ctx.reply(respuesta, delete_after=5)


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)



###clase del descargador
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
    @classmethod
    def from_url(cls, url, *, loop=None, stream=False):#
        loop = loop or asyncio.get_event_loop()
        data = ytdl.extract_info(url, download=not stream)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

######################################################
@Bot.event
async def on_ready():
  print('Sesión iniciada como {0.user}'.format(Bot))
  channel = Bot.get_channel(879396354525397053) #Parche
  await channel.send("¡Me he quedao' traspuesta un ratito, pero ya estoy de vuelta!")

#BIENVENIDA
@Bot.event
async def on_member_join(member):
  channelid = member.guild.text_channels[0].id
  channel = Bot.get_channel(channelid)
  print("Recognized that " + member.name + " joined")
  usuario = member.name
  server = member.guild

  ###### MENCIONAR AL USUARIO Y POSIBLE CANAL DE BIENVENIDAS

  try:
    await channel.send('*¡El **Conejo de Ministros** le da la bienvenida a {user} a **{server}**!*'.format(user=usuario, server=server))
  except:
    channel = Bot.get_channel(879396354525397053) #Parche
    await channel.send('*¡El **Conejo de Ministros** le da la bienvenida a {user} a **{server}**!*'.format(user=usuario, server=server))


#RETIRADA
@Bot.event
async def on_member_remove(member):
  channelid = member.guild.text_channels[0].id
  channel = Bot.get_channel(channelid)
  usuario = member.name
  print("Recognized that " + usuario + " left")
  try:
    await channel.send('**' + usuario + '** acaba de largarse. Soltad a los perros 🐕🐕🐕🐕🐕🐕🐕🐕🐕🐕🐕🐕.')
  except:
    channel = Bot.get_channel(879396354525397053) #Parche
    await channel.send('**' + usuario + '** acaba de largarse. Soltad a los perros 🐕🐕🐕🐕🐕🐕🐕🐕🐕🐕🐕🐕.')

votacion = {}

@Bot.event
async def on_message(message):
  #msg = message.author.name + ": " + message.content
  #print(msg)
  if ("montse" in message.content.lower()) or ("<@!878749645898149908>" in message.content.lower()) :
    fm = open("MontseApr/frasesmontseras.txt", "r")
    frasesmontse = fm.readlines()
    n_frases=len(frasesmontse)
    frasemontse = frasesmontse[random.randint(0,n_frases-1)]
    await message.reply(str(frasemontse))

#################-1COMANDOS-#################
@slash.slash(
  name="comandos",
  description = "Da una lista de los comandos que ofrece el bot",
  guild_ids=guild_ids)
async def _comandos(message):
  respuesta = discord.Embed(title="__**COMANDOS**__" , color= 0x2a59a1)
  comandos = get_comandos()
  lista_comandos = comandos.split("#")
  comandos_ocio = lista_comandos[0]
  comandos_musica = lista_comandos[1]
  comandos_economia = lista_comandos[2]
  respuesta.add_field(name="Ocio:", value = comandos_ocio)
  respuesta.add_field(name="Música:", value = comandos_musica)
  respuesta.add_field(name="Economía:", value = comandos_economia)
  await message.reply(embed=respuesta)

def get_comandos():
    comandos = actjson.abrir_json('MontseApr/comandos.json')

    str_ocio = comandos["ocio"]
    str_ocio = str_ocio.replace(",","`\n`/")
    str_ocio = "`/" + str_ocio + "`"

    str_musica = comandos["musica"]
    str_musica = str_musica.replace(",","`\n`/")
    str_musica = "`/" + str_musica + "`"

    str_economia = comandos["economia"]
    str_economia = str_economia.replace(",","`\n`/")
    str_economia = "`/" + str_economia + "`"

    string_completa = str_ocio + "#" + str_musica + "#" + str_economia

    return string_completa


#########EL REY REINANDO A DECRETAZO LIMPIO

@slash.slash(
  name="impuestos",
  description="Impuestos del reino a las grandes fortunas.",
  guild_ids=guild_ids
)
async def _impuestos(ctx):
  roles = f_m.get_roles(ctx)  
  roles_privilegiados = set(["👑 SU MAJESTAD 👑","Prime Minister"])
  rp_usuario = roles_privilegiados.intersection(roles)
  if len(rp_usuario) == 0:
    respuesta = "No tienes el rol necesario para ejecutar esta acción."
    await ctx.reply(respuesta) 
  else:
    lexos = actjson.abrir_json("MontseApr/lexos.json")
    respuesta = ""
    for usuario in lexos:
      dinero = lexos[usuario]['lexos']
      if int(dinero) >= 10000 and usuario != "Alexander Alex":
        impuesto = round(dinero*0.85)
        dinero = dinero - impuesto
        arcas_reales = lexos["Alexander Alex"]["lexos"] + impuesto
        lexos[usuario]['lexos'] = dinero
        lexos["Alexander Alex"]["lexos"] = arcas_reales
        respuesta += ":chart_with_downwards_trend: **{}** ha recibido un gravamen del **85%** ({} lexos).\n".format(usuario,impuesto)
    if len(respuesta)>0:
      respuesta += "👑 SU MAJESTAD 👑 lo gestionará con sabiduría. :crown: :blush:"
      await ctx.reply(respuesta)
    #actjson.actualizar_lexos(lexos)




#################-2HOLA-#################
@slash.slash(
  name="hola",
  description="Es Montse Apr, ¿qué va a decir?",
  guild_ids=guild_ids
)
async def _hola(ctx:SlashContext):
  if check_canal(ctx):
    await ctx.send("Hola, Blisset", delete_after = 15)
  else:
    await ctx.send("Canal prohibido.", delete_after = 5)
  

#################-3DIARIA-#################
@slash.slash(
  name="diaria",
  description = "Te da dinero y te dice la fecha.",
  guild_ids=guild_ids)
async def _diaria(message):
  await message.reply(f_m.diaria(message))

#################-4CURRAR-#################
@slash.slash(
  name="currar",
  description = "Trabajar para cobrar dineros un rato más tarde.",
  guild_ids=guild_ids)
async def _currar(message):
  await message.reply(f_m.currar(message))

#################-5COBRAR-#################
@slash.slash(
  name="cobrar",
  description = "Cobrar dinerito por currar.",
  guild_ids=guild_ids)
async def _cobrar(message):   
  await message.reply(f_m.cobrar(message))

#################-6DAR-#################
@slash.slash(
  name="dar",
  description = "Da dinero al destinatario",
  guild_ids=guild_ids,
  options = [
    create_option(
      name = "destinatario",
      description = "a quién le das dinero",
      option_type = 6,
      required = True),
    create_option(
      name = "cantidad",
      description = "cuánto dinero",
      option_type = 4,
      required = True)
  ]
)
async def _dar(message,destinatario: str, cantidad: int):
  await message.reply(f_m.dar(message,destinatario,cantidad))

#################-7TIENDA-#################
@slash.slash(
  name="tienda",
  description = "Te da una lista de los objetos que puedes comprar y su precio.",
  guild_ids=guild_ids)
async def _tienda(message):
  await message.reply(embed=f_m.tienda(message))

#################-8COMPRAR-#################
@slash.slash(
  name="comprar",
  description = "Te permite comprar objetos de la tienda.",
  guild_ids=guild_ids,
  options=[
      create_option(
      name = "objeto",
      description = "objeto que compras en la tienda",
      option_type = 3,
      required=True
  )]
)
async def _comprar(message,objeto):
  await message.reply(f_m.comprar(message, objeto))

#################-9INVENTARIO-#################
@slash.slash(
  name="inventario",
  description = "Te enseña tu inventario.",
  guild_ids=guild_ids)
async def _inventario(message):
  await message.reply(embed=f_m.inventario(message))

#################-10FRASE-#################
@slash.slash(
  name = "frase",
  description = "Frases Blisseras aleatorias.",
  guild_ids=guild_ids) 
async def _frase(message):
  await  message.reply(str(f_m.frase(message)))

#################-14USAR-#################
@slash.slash(
  name="usar",
  description = "Usas un objeto consumible.",
  guild_ids=guild_ids)
async def _usar(message, objeto: str):
  await message.reply(f_m.usar(message,objeto))

#################-15BANCO-#################
@slash.slash(
  name="banco",
  description = "Te dice cuánto dinero tienes.",
  guild_ids=guild_ids)
async def _banco(message):
  await message.reply(f_m.banco(message))

############ SECCION CASINO #############

'''
@slash.slash(
  name = "ruleta",
  description = "Jugar a la ruleta rusa",
  guild_ids = guild_ids)
async def _ruleta(ctx, apuesta = 0):
  if apuesta<100:
    respuesta = "La apuesta mínima es de 100 Lexos."
    await ctx.reply(respuesta
 '''  

@slash.slash(
  name = "dados",
  description = "Te permite apostar Lexos contra la máquina tirando dos dados cada uno. El que más puntos sume, gana.",
  guild_ids=guild_ids)
async def _dados(ctx, apuesta = 0):
  if esunnumero(apuesta):
    await ctx.reply(f_m.dados(ctx,int(apuesta)))
  else:
    await ctx.reply("La apuesta debe ser un número.",delete_after = 5)

@slash.slash(
  name = "caraocruz",
  description = "Te permite apostar Lexos contra la máquina tirando una moneda al aire.",
  guild_ids=guild_ids)
async def _caraocruz(ctx, apuesta):
  if esunnumero(apuesta):
    respuesta = "Apuestas " + str(apuesta)+" :coin:. Elige: 'cara' o 'cruz' para tirar la moneda."
    await ctx.reply(respuesta)
    opciones = ["cara","cruz"]
    
    def check(selec_usuario):
      return selec_usuario.author == ctx.author and selec_usuario.channel == ctx.channel and \
      selec_usuario.content.lower() in opciones
    selec_usuario = (await Bot.wait_for("message", check=check)).content.lower()
    
    await ctx.reply(f_m.caraocruz(ctx,int(apuesta),selec_usuario))
  else:
    await ctx.reply("La apuesta debe ser un número.",delete_after = 5)
 
@slash.slash(
  name="rps",
  description = "Rock, paper and scissors",
  guild_ids=guild_ids)
async def _rps(ctx, apuesta = 0):
  if esunnumero(apuesta):
    respuesta = "Apuestas " + str(apuesta)+" :coin:. Elige: r, p, s (:rock:, :page_facing_up:, :scissors:): "
    await ctx.reply(respuesta)

    def check(selec_usuario):
      return selec_usuario.author == ctx.author and selec_usuario.channel == ctx.channel and \
      selec_usuario.content.lower() in ["r", "p", "s"]
    
    cosas = ["r", "p", "s"]
    selec_usuario = (await Bot.wait_for("message", check=check)).content.lower()
    selec_maquina = random.choice(cosas)
    await ctx.reply(f_m.rps(ctx,int(apuesta),selec_usuario,selec_maquina))
  else:
    await ctx.reply("La apuesta debe ser un número.",delete_after = 5)

@slash.slash(
  name = "roles",
  description = "Te dice qué roles tienes.",
  guild_ids = guild_ids)
async def _roles(ctx):
  roles = f_m.get_roles(ctx)
  respuesta = "Tus roles son:\n"
  for i in roles:
    if i != "@everyone":
      respuesta +=  i + "\n"
  print(respuesta)
  await ctx.reply(respuesta)

def esunnumero(mensaje):
  loes=True
  for caracter in mensaje:
    if not caracter.isdigit():
      loes = False
  return loes


##############QUEMAR#################

@slash.slash(
  name = "quemar",
  guild_ids = guild_ids)
async def _quemar(ctx, combustible):
  tipo = type(combustible)
  string = type("a")

  usuario = ctx.author.name
  es_un_numero = esunnumero(combustible)
  if not es_un_numero and tipo == string:
    inventario = actjson.abrir_json('MontseApr/inventario.json')
    
    if combustible in inventario[usuario]:
      cantidad = inventario[usuario][combustible]
      cantidad -= 1
      if cantidad == 0:
        inventario[usuario][combustible].pop(combustible)
      else:
        inventario[usuario][combustible] = cantidad
      actjson.actualizar_inventarios(inventario)
      respuesta = "Quemando {objeto}.".format(objeto=combustible)
    else: 
      respuesta = "No posees el objeto '{objeto}'.".format(objeto=combustible)
     
  elif es_un_numero:
    combustible = int(combustible)
    lexos = actjson.abrir_json('MontseApr/lexos.json')
    dinero_usuario = lexos[usuario]['lexos']
    if dinero_usuario >= combustible:
      dinero_usuario -= combustible
      lexos[usuario]['lexos'] = dinero_usuario
      actjson.actualizar_lexos(lexos)
      respuesta = "Quemando {quemados} Lexo(s) en una hoguera. Te quedan {dinero} Lexos :coin:.".format(quemados=combustible, dinero=dinero_usuario)
    else:
      respuesta = "No tienes tantos lexos, fantasma."
  else:
    respuesta = "Error en la funcion quemar."
  await ctx.reply(respuesta)

################# COMANDOS CON ROLES ##################
#################-16BORRAR-################# 

@slash.slash(
  name = "borrar",
  description = "Borra los últimos n mensajes del bot en este chat. Necesitas ser ministro para ello.",
  guild_ids=guild_ids)
async def _borrar(ctx, limit:int):
  roles = f_m.get_roles(ctx)
  roles_privilegiados = set(["🛡 Lugarteniente  ⚔️","Prime Minister","👑 SU MAJESTAD 👑", "⚙️ Mezclaor 🗡"])
  rp_usuario = roles_privilegiados.intersection(roles)
  if len(rp_usuario) == 0:
    respuesta = "No tienes el rol necesario para ejecutar esta acción."
  else:
    if 0 < limit <= 100:
      with ctx.channel.typing():
        await ctx.channel.purge(limit=limit)
        respuesta = "Borrados " + str(limit) + " mensajes."
  await ctx.reply(respuesta, delete_after = 5)

def check_canal(ctx):
  canal_id = ctx.channel.id
  global canales_habilitados
  permiso = canal_id in canales_habilitados
  return permiso

#Futuras MODIFICACIONES.
#cambiar /diaria a /semanal y cantidad fija (con racha) y baja.
#implementar /burn /ruleta 
#implementar funcion check canal
#implementar sorteo de la lista
#distintos canales #musica #finanzas #bienvenida #funcionariado
#implementar banca
#implementar ofertas musicales
#roles de DJ?
##IMPLEMENTAR EMPLEOS DE servicios prestados a la comunidad
  #programador
  #mandar tema
  #verificador
#aprender a usar Cogs (conjuntos de comandos)
token = actjson.abrir_json('MontseApr/token_montse.json')
Bot.run(token['montse_token']) #token
