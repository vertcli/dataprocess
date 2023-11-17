===========
DataProcess
===========


## Descripción

`dataprocess` es una biblioteca de Python diseñada para procesar datos geolocalizados. Facilita la conexión con BigQuery para la base de datos cobertura de telefonía móvil en Cataluña y la generación de KPIs útiles para identificar oportunidades de mercado en la provisión de servicios de telecomunicaciones.

## Instalación

Para instalar `dataprocess`, simplemente ejecute el siguiente comando:

```bash
pip install git+https://github.com/vertcli/dataprocess
```

## Uso

### Configuración Inicial

Antes de comenzar, necesitará un archivo de credenciales de Google Cloud. Una vez que tenga este archivo, puede cargar sus credenciales de la siguiente manera:

```python
from dataprocess import load_credentials

credenciales = load_credentials('ruta/a/tu/archivo/credenciales.json')
```

### Creando una Instancia del Cliente

Para interactuar con los datos de cobertura, cree una instancia de `ClienteCoberturaMovil`:

```python
from dataprocess import ClienteCoberturaMovil

cliente = ClienteCoberturaMovil(
    nombre_tabla='nombre_de_tu_tabla_bigquery',
    credenciales=credenciales
)
```

### Selección de Datos y Generación KPIs

Puede seleccionar datos y generar KPIs de la siguiente manera:

```python
# Seleccionar datos
parametros_busqueda = {'operator': 'Movistar', 'network': '4G'}

# Generar KPIs
kpi_df = cliente.generar_kpi_cobertura(metric='AVG',search_parameters=parametros_busqueda)
```

### Visualización de Datos en Mapas

Para visualizar datos geográficos:

```python
cliente.set_map('ruta/al/archivo/de/mapa.gml')
cliente.generate_map_plot(operation='point_count', aggregated_column='signal')
```

## Contribución

Las contribuciones son bienvenidas. Por favor, lea [CONTRIBUTING.md](CONTRIBUTING.md) para obtener detalles sobre nuestro código de conducta y el proceso para enviarnos solicitudes de extracción.


## Autores

- Albert Climent Bigas - *Trabajo inicial* - [vertcli](https://github.com/vertcli)


Credits
-------

This package was created with Cookiecutter_ and the `pyOpenSci/cookiecutter-pyopensci`_ project template, based off `audreyr/cookiecutter-pypackage`_.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`pyOpenSci/cookiecutter-pyopensci`: https://github.com/pyOpenSci/cookiecutter-pyopensci
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
