import json
#################-ACTUALIZAR LEXOS-#################
#Esta función guarda el objeto JSON "lexos" en el archivo "lexos.json".
def actualizar_lexos(lexos):
  out_file = open("MontseApr/lexos.json", "w") 
  json.dump(lexos, out_file, indent = 4) 
  out_file.close()    

#################-ACTUALIZAR INVENTARIO-#################
#Esta función guarda el objeto JSON "lexos" en el archivo "lexos.json".
def actualizar_inventarios(inventarios):
  out_file = open("MontseApr/inventario.json", "w") 
  json.dump(inventarios, out_file, indent = 4) 
  out_file.close() 


#################-ACTUALIZAR PLAYLIST-#################
#Esta función guarda el objeto JSON "lexos" en el archivo "lexos.json".
def actualizar_playlist(playlist):
  out_file = open("MontseApr/playlist.json", "w") 
  json.dump(playlist, out_file, indent = 4) 
  out_file.close() 

#################-ABRIR JSON-#################
#Esta función abre un archivo json y carga su contenido en la variable que devuelve.
def abrir_json(nombre_archivo):
  with open(nombre_archivo) as jsonFile:
    objeto_json = json.load(jsonFile)
    jsonFile.close()
  return objeto_json