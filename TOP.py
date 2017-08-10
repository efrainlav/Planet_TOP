
#!/usr/bin/env python
# -*- coding: utf-8

"""# Basado en los script originalmente publicado en #https://www.planet.com/docs/guides/quickstart-ndvi/
#https://joseguerreroa.wordpress.com/2013/10/20/lista-con-el-nombre-de-los-archivos-de-una-determinada-extension-en-un-directorio-mediante-python/



#Inicialmente se tienes las imagenes a corregir con los metadatos en una misma ruta.
#Esta correcion funciona unicamente para los archivos sometidos al script de Clic&Ship, los cuales vienen con la extension *_clip.tif"""

#Se importan las librerias requeridas

import os
import rasterio
import numpy
from xml.dom import minidom

#Crear listado de la carpeta donde estan los .tif
 
#Variable para la ruta al directorio
path = 'C:\Users\elaverde\Downloads\Planet\FENALCE\Fenalce\PS\August232016'
 
#Lista vacia para incluir los ficheros
lstFiles = []
 
#Lista con todos los ficheros del directorio:
lstDir = os.walk(path)   #os.walk()Lista directorios y ficheros
  
#Crea una lista de los ficheros jpg que existen en el directorio y los incluye a la lista.
 #Importante, tener solo los archivos a corregir, es decir, eliminar lso acrchivos *_DN_udm.tif si estan presentes
for root, dirs, files in lstDir:
    for fichero in files:
        (nombreFichero, extension) = os.path.splitext(fichero)
        if(extension == ".tif"):
            lstFiles.append(nombreFichero+extension)

			
#Empieza el codigo para realizar la correcion del TOP

#Listar los archivos a corregir.
for file in lstFiles:
	# Download clip when active, check that image doesn't exist already
	item=file
#Quita	
	item=item[:len(item)-9]
	
#Renombrar xml para extraer los metadatos	
	xmldoc = minidom.parse(item+"_metadata_clip.xml")

#Renombrar imagen para abrirl xml y extraer los metadatos	
	image_file = item+"_clip.tif"

	
# Cargar infomacion de las bandas RGB e Infrerojo cercano - Es importante evidenciar que todas las imagenes de PlanetScope con 4-bandas tienen el orden de las bandas como BGRN
#Con rasterio.open(image_file) as src: se dispone a acceder la imagen y consultar cada banda
	
	with rasterio.open(image_file) as src:
		band_blue = src.read(1)
		band_green = src.read(2)
		band_red = src.read(3)
		band_nir = src.read(4)	
		
		
		
#La conversión de los valores de píxeles en reflectancia TOA hace que el análisis sea más preciso y comparable con otras escenas. Para ello se carga los coeficientes de reflectancia TOA del activo XML de metadatos.

#Se consulta l aparte del metadato que da la informacion especifica por bandas	
	nodes = xmldoc.getElementsByTagName("ps:bandSpecificMetadata")

#Se captura el valor de coeficiente para cada banda
	coeffs = {}
	for node in nodes:
		bn = node.getElementsByTagName("ps:bandNumber")[0].firstChild.data
		if bn in ['1', '2', '3', '4']:
			i = int(bn)
			value = node.getElementsByTagName("ps:reflectanceCoefficient")[0].firstChild.data
			coeffs[i] = float(value)
		
		
		

#Se multiplica por el valor del coeficiente
	band_blue = band_blue * coeffs[1] * 0.01
	band_green = band_green * coeffs[2] * 0.01
	band_red = band_red * coeffs[3] * 0.01
	band_nir = band_nir * coeffs[4] * 0.01



#Finalmente, enviamos estos nuevos valores de píxeles a un nuevo archivo de imagen, asegurándonos de que reflejamos los metadatos espaciales del GeoTIFF de entrada

# Establezca las características espaciales del objeto de salida para simular el de entrada
	kwargs = src.meta
	kwargs.update(
		dtype=rasterio.float32,compress='lzw')
	
	kwargs.update(
		dtype=rasterio.float32,
		count=4,
		compress='lzw')
		

# Crea el nuevo archivo
	with rasterio.open(item+'_clip_TOP.tif', 'w', **kwargs) as dst:
	 dst.write_band(1, band_blue.astype(rasterio.float32))
	 dst.write_band(2, band_green.astype(rasterio.float32))
	 dst.write_band(3, band_red.astype(rasterio.float32))
	 dst.write_band(4, band_nir.astype(rasterio.float32))
