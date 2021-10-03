import actjson
from datetime import datetime, timedelta, timezone
UTC = timezone(timedelta(hours=+2))
import random
import tdform as tdf

import discord
#from discord.ext import commands
#from discord_slash import SlashCommand, SlashContext
#from discord_slash.utils.manage_commands import create_option #, create_choice

def diaria(message):
  lexos = actjson.abrir_json("MontseApr/lexos.json")
  #Recogemos la información del usuario y del día
  usuario = message.author.name
  fecha = datetime.now(UTC).date().isoformat()
  
  #Si el usuario está registrado en el JSON, vemos cuándo le tocaba su próximo diaria
  if (usuario in lexos):
    next_diaria = lexos[usuario]["next_diaria"]
    nuevo_next_diaria = datetime.now(UTC).date() + timedelta(days=1)
    #Si ya le toca el siguiente diaria:
    if fecha >= next_diaria:
      #Calculamos los datos nuevos,
      dinero_actual = lexos[usuario]["lexos"]
      ganancia = random.randint(80, 120)
      racha= lexos[usuario]["diaria_racha"]
      ganancia_racha = round(ganancia*(1+0.1*racha))
      dinero_final = dinero_actual + ganancia_racha
      racha = racha + 1
      #almacenamos en el objeto JSON
      lexos[usuario]["next_diaria"] = nuevo_next_diaria.isoformat()
      lexos[usuario]["diaria_racha"] = racha 
      lexos[usuario]["lexos"] = dinero_final
      #y scribimos el mensaje que mandará el bot.
      respuesta = "Racha de " + str(racha) + " días.\n+"+ str(ganancia_racha) + " lexos :coin:.\nTienes " + str(dinero_final) + " lexos :coin:."
    #Si no le toca aún, escribimos el acceso denegado.
    else:
      respuesta = ":no_entry: Hoy ya has pedido tu diaria.\n:calendar: Próxima diaria: "+ next_diaria
  #Si el usuario no está registrado:
  else:
    #Calculamos su primer ingreso, su next_diaria, inicializamos su racha a 1 y le inscribimos con esos datos.
    ganancia =  random.randint(80, 120)
    dinero_final = ganancia
    next_diaria = datetime.now(UTC).date() + timedelta(days=1)
    next_diaria_json = next_diaria.isoformat()       
    racha = 1
    el_nuevo={usuario: {"lexos" : dinero_final,"diaria_racha" : racha, "next_diaria" : next_diaria_json}}
    lexos = {**lexos,**el_nuevo}
    respuesta = ":wave_tone2: *¡Bienvenido al sistema financiero de la Countspiración*!\nHas ganado tus primeros "+ str(ganancia) + " lexos :coin:.\n:calendar_spiral: Vuelve mañana a por más."
  #Finalmente guardamos los datos en el JSON.
  actjson.actualizar_lexos(lexos)
  return respuesta

  


def currar(message):
  usuario = message.author.name
  lexos = actjson.abrir_json("MontseApr/lexos.json")
  if ("trabajando" in lexos[usuario]):
    trabajando = lexos[usuario]["trabajando"]["status"]
    if(trabajando == "no"):
      trabajando = "si"
      sueldo = random.randint(180,300)
      lexos[usuario]["trabajando"]["status"] = trabajando
      lexos[usuario]["trabajando"]["sueldo"] = sueldo
      lexos[usuario]["trabajando"]["start"] = datetime.now(UTC).isoformat()
      respuesta = "¡Comienzas a trabajar! En 1h reclama tu sueldo de {:n} :coin:.".format(sueldo)
    else:
      respuesta = "¡Ya estás trabajando!"
  else:
    trabajando = "si"
    sueldo = random.randint(190,250)
    ahora = datetime.now(UTC).isoformat()
    lexos[usuario]["trabajando"]={"status" : "si", "sueldo" : sueldo, "start" : ahora}
    respuesta = "¡Comienzas a trabajar! En 1h reclama tu sueldo de {:n} Lexos :coin:.".format(sueldo)
  actjson.actualizar_lexos(lexos)
  return respuesta



def cobrar(message):
  usuario = message.author.name
  lexos = actjson.abrir_json("MontseApr/lexos.json")
  hora = datetime.now(UTC)
  start = lexos[usuario]["trabajando"]["start"]
  start_time = datetime.fromisoformat(start) 
  transcurrido = hora - start_time
  if("trabajando" in lexos[usuario]):
    if(lexos[usuario]["trabajando"]["status"] == "si"):
      if(transcurrido >= timedelta(hours=1)):
        dinero_actual = lexos[usuario]["lexos"]
        sueldo = lexos[usuario]["trabajando"]["sueldo"]
        lexos[usuario]["trabajando"]["status"] = "no"
        lexos[usuario]["lexos"] = dinero_actual + sueldo 
        respuesta = "¡Buen trabajo! Toma tu sueldo: {:n} Lexos :coin:.".format(sueldo)
      else:
        restante = timedelta(minutes=60) - transcurrido
        restante_minutos = tdf.timedeltaformatter(restante)[2]
        respuesta = "No has terminado de trabajar. Quedan " + str(restante_minutos) + " minutos :clock1:."
    else:
      respuesta = "No estás currando. Para currar usa /currar."
  else:
    respuesta = "No estás currando. Para currar usa /currar."
  actjson.actualizar_lexos(lexos)
  return respuesta

def dar(message, destinatario: str, cantidad: int):  
  lexos = actjson.abrir_json("MontseApr/lexos.json")
  usuario = message.author.name
  dinero_usuario = lexos[usuario]["lexos"]
  destino = destinatario.name
  if (usuario in lexos):
    if (dinero_usuario >= cantidad and cantidad >0):
      lexos[usuario]["lexos"] = lexos[usuario]["lexos"] - cantidad
      respuesta = usuario + " ha dado " + str(cantidad) + " Lexos :coin: a " + destino + "."
      if (destino in lexos):
        lexos[destino]["lexos"] = lexos[destino]["lexos"] + cantidad
      else: #Le registramos y hacemos la transacción
        dinero_final = cantidad
        next_diaria_json = datetime.now(UTC).date().isoformat()
        racha = 0
        el_nuevo={destino: {"lexos" : dinero_final,"diaria_racha" : racha, "next_diaria" : next_diaria_json}}
        lexos = {**lexos,**el_nuevo}
    elif (dinero_usuario < cantidad):
      respuesta = "Sólo tienes "+str(dinero_usuario)+" Lexos :coin:. No son suficientes para efectuar la transacción." 
    elif(cantidad < 0):
      respuesta = "¿Intentando robar? ¿Por qué no te presentas a las elecciones?"
  else:
    respuesta = "No tienes Lexos :coin: en tu cuenta. ¡Usa el comando /diaria para conseguir tu primer montón!"
  actjson.actualizar_lexos(lexos)
  return respuesta


def tienda(message):
  tienda = actjson.abrir_json("MontseApr/tienda.json")
  lista = ""
  precios = ""
  for objeto in tienda:
    lista = lista + tienda[objeto]["nombre"] + "\n"
    precios =precios + str(tienda[objeto]["precio"]) + ":coin:\n"
  respuesta=discord.Embed(title=":moneybag: Tienda" , color= 0xffd500)
  respuesta.add_field(name="Objetos:", value = lista, inline=True)
  respuesta.add_field(name="Precios:",value = precios, inline = True)
  return respuesta



def comprar(message, objeto):
  objeto_low = objeto.lower()
  tienda = actjson.abrir_json("MontseApr/tienda.json")
  lexos = actjson.abrir_json("MontseApr/lexos.json")
  inventarios = actjson.abrir_json("MontseApr/inventario.json")
  usuario=message.author.name
  if (objeto_low in tienda):
    precio = tienda[objeto_low]["precio"]
    if (usuario in lexos):
        dinero_usuario = lexos[usuario]["lexos"]
        if (dinero_usuario >= precio):
          lexos[usuario]["lexos"] = lexos[usuario]["lexos"] - precio
          respuesta = usuario + " ha comprado 1 " + tienda[objeto_low]["nombre"]
          if(usuario in inventarios):
            if (objeto_low in inventarios[usuario]):
              inventarios[usuario][objeto_low] += 1
            else:
              inventarios[usuario][objeto_low] = 1
          else:
            inventarios[usuario]={objeto_low : 1}

          actjson.actualizar_lexos(lexos)
          actjson.actualizar_inventarios(inventarios)
        else:
          respuesta = "No tienes suficientes Lexos :coin:."
    else:
      respuesta = "Aún no tienes Lexos. ¡Usa la función /diaria para conseguir tu primer ingreso!"
  else:
    respuesta = "Objeto no encontrado en la tienda. Para saber qué puede comprarse, usa /tienda"
  return respuesta




def inventario(message):
  usuario = message.author.name
  inventarios = actjson.abrir_json("MontseApr/inventario.json")
  if (usuario in inventarios):
    inventario_usuario = inventarios[usuario]
    lista =""
    for objeto in inventario_usuario:
      lista = lista + str(inventario_usuario[objeto])+ " " + objeto + "(s)\n"
    titulo =":package: Inventario de " + usuario
    respuesta = discord.Embed(title = titulo,
    color = 0x34eb5f)
    respuesta.add_field(name="Lista de objetos:", value = lista, inline = False)
    
  else:
    respuesta = discord.Embed(title=":x: Error" , color= 0xd41111)
    respuesta.add_field(name="Error:", value = "Aún no tienes objetos.\nPuedes comprarlos con el comando /comprar.")
  return respuesta



def frase(message):
  f = open("MontseApr/frasesblisseras.txt", "r")
  frases = f.readlines()
  n_frases=len(frases)
  frase = frases[random.randint(0,n_frases-1)] +"*-Tony Domenech*"
  return frase



def usar(message, objeto):  
  usuario = message.author.name
  inventarios = actjson.abrir_json("MontseApr/inventario.json")
  tienda = actjson.abrir_json("MontseApr/tienda.json")
  if objeto in inventarios[usuario]:
    if tienda[objeto]["consumible"] == "si":
      cantidad = inventarios[usuario][objeto]
      cantidad = cantidad - 1
      inventarios[usuario][objeto] = cantidad
      if cantidad == 0:
        inventarios[usuario].pop(objeto, None)        
        #borrar del registro
      obj_nombre = tienda[objeto]["nombre"]
      obj_frase = tienda[objeto]["frase_consumir"]
      respuesta = usuario + " consume:" + obj_nombre + "\n" + obj_frase
      actjson.actualizar_inventarios(inventarios)
    else:
      respuesta = "El objeto " + objeto + " no es consumible."
  else:
    respuesta = "No posees " + objeto + "."
  return respuesta


def banco(message):  
  usuario = message.author.name
  lexos = actjson.abrir_json("MontseApr/lexos.json")
  if (usuario in lexos):
    dinero_actual = lexos[usuario]["lexos"]
    respuesta = "Tienes " + str(dinero_actual) + " lexos :coin:."
  else:
    respuesta = "Aún no tienes Lexos. ¡Usa la función /diaria para conseguir tu primer ingreso!"
  return respuesta


def rps(ctx, apuesta, selec_usuario,selec_maquina):
  respuesta = "Seleccion del usuario: " + selec_usuario + "\nSeleeción de la máquina: " + selec_maquina
  lexos = actjson.abrir_json("MontseApr/lexos.json")
  usuario = ctx.author.name
  dinero_usuario = lexos[usuario]['lexos']
  if (dinero_usuario >= apuesta and apuesta>0) :
    if(selec_maquina==selec_usuario):
      respuesta += "\nEMPATE!"
    elif(selec_usuario == "r"):
      if (selec_maquina == "p"):
        respuesta += "\nPIERDES" +"!"
        dinero_usuario -= apuesta
      else:
        respuesta += "\nGANAS!"
        dinero_usuario += apuesta
    elif(selec_usuario == "p"):
      if (selec_maquina == "s" ):
        respuesta += "\nPIERDES!"
        dinero_usuario -= apuesta
      else:
        respuesta += "\nGANAS!"
        dinero_usuario += apuesta
    elif(selec_usuario == "s"):
      if (selec_maquina == "r" ):
        respuesta += "\nPIERDES!"
        dinero_usuario -= apuesta
      else:
        respuesta += "\nGANAS!"
        dinero_usuario += apuesta
    else:
      respuesta += "\nEres tonto."
    lexos[usuario]['lexos'] = dinero_usuario
    actjson.actualizar_lexos(lexos)
  else:
    respuesta = "No tienes suficientes Lexos para apostar esa cantidad."
  return respuesta

def dados(ctx,apuesta):
  lexos = actjson.abrir_json("MontseApr/lexos.json")
  usuario = ctx.author.name
  dinero_usuario = lexos[usuario]['lexos']
  if (dinero_usuario >= apuesta  and apuesta>0):
    dados_usuario = random.sample(range(1,7),2)
    dados_maquina = random.sample(range(1,7),2)
    punt_usuario = sum(dados_usuario)
    punt_maquina = sum(dados_maquina)
    respuesta = "Dados del usuario: "+ str(dados_usuario) + "\n"
    respuesta += "Dados de la máquina: "+ str(dados_maquina) + "\n"
    if (punt_usuario == punt_maquina):
      respuesta += "Empate!"
    elif(punt_usuario > punt_maquina):
      respuesta += "GANAS " + str(apuesta) + " Lexos :coin:!"
      dinero_usuario += apuesta
    else:
      respuesta += "PIERDES " + str(apuesta) + " Lexos :coin:!"
      dinero_usuario -= apuesta
    lexos[usuario]['lexos'] = dinero_usuario
    actjson.actualizar_lexos(lexos)
  else:
    respuesta = "No tienes suficientes Lexos para apostar esa cantidad."
  return respuesta
    
async def caraocruz(ctx,apuesta,Bot):
  lexos = actjson.abrir_json("MontseApr/lexos.json")
  usuario = ctx.author.name
  dinero_usuario = lexos[usuario]['lexos']
  
  def check(selec_usuario):
    return selec_usuario.author == ctx.author and selec_usuario.channel == ctx.channel and \
    selec_usuario.content.lower() in opciones
    
  if (dinero_usuario >= apuesta  and apuesta>0):
    respuesta = "Apuestas {} :coin:. Elige: 'cara' o 'cruz' para tirar la moneda.".format(apuesta)
    selec_usuario = (await Bot.wait_for("message", check=check)).content.lower()
    await ctx.reply(respuesta)
    opciones = ["cara","cruz"]
    moneda = random.choice(["cara","cruz"])
    if moneda == selec_usuario:
      respuesta = "Ha salido: " + moneda +".\nGANAS " + str(apuesta) + " Lexos :coin:!"
      dinero_usuario += apuesta
    else:
      respuesta ="Ha salido: " + moneda + ".\nPIERDES " + str(apuesta) + " Lexos :coin:!"
      dinero_usuario -= apuesta
    lexos[usuario]['lexos'] = dinero_usuario
    actjson.actualizar_lexos(lexos)
  else:
    respuesta = "No tienes suficientes Lexos para apostar esa cantidad."
  return respuesta

def get_roles(ctx):
  respuesta = str(ctx.author.roles)
  lista = respuesta.split("'")
  roles = []
  respuesta =""
  for i in range(0,len(lista)):
    if (i % 2) == 1:
      roles.append(lista[i])
  return roles

  