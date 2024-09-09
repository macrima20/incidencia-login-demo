import logging

# Evita que los logs de la aplicación ensucien la salida de las pruebas.
logging.getLogger().addHandler(logging.NullHandler())
