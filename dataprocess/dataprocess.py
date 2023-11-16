# -*- coding: utf-8 -*-
"""Main module template with example functions."""


from typing import List, Any, Dict
from google.cloud import bigquery
from google.oauth2.service_account import Credentials


class ClienteCoberturaMovil:
    """Cliente para analizar la cobertura de la red móvil en áreas con baja cobertura de grandes operadoras.

    Esta clase se conecta a BigQuery y permite realizar consultas específicas y generar KPIs útiles para identificar
    oportunidades de mercado en la provisión de servicios de telecomunicaciones.

    Atributos:
        cliente (bigquery.Client): Una instancia del cliente de BigQuery.
        nombre_tabla (str): Nombre de la tabla en BigQuery con los datos de cobertura.
    """

    def __init__(self, nombre_tabla: str, credenciales: Credentials):
        """Inicializa el cliente de BigQuery.

        Args:
            nombre_tabla (str): El nombre de la tabla en BigQuery con los datos de cobertura.
            credenciales (service_account.Credentials): Credenciales del proyecto
        """
        self.cliente = bigquery.Client(
            project=credenciales.project_id, credentials=credenciales
        )
        self.nombre_tabla = nombre_tabla

    def seleccionar_datos(self, parametros_busqueda: Dict[str, Any]) -> List[Any]:
        """Realiza una consulta a BigQuery basada en parámetros de búsqueda específicos.

        Args:
            parametros_busqueda (Dict[str, Any]): Diccionario con los parámetros de búsqueda.

        Returns:
            List[Any]: Una lista de resultados de la consulta.
        """
        # Construir la consulta SQL basada en los parámetros de búsqueda
        consulta = f"SELECT * FROM `{self.nombre_tabla}` WHERE "
        condiciones = " AND ".join(
            [f"{key} = '{value}'" for key, value in parametros_busqueda.items()]
        )
        consulta_completa = consulta + condiciones

        # Realizar la consulta y retornar los resultados
        tarea_consulta = self.cliente.query(consulta_completa)
        return [fila for fila in tarea_consulta]

    def generar_kpi_cobertura(self) -> dict:
        """Genera KPIs relacionados con la cobertura de la red móvil.

        Returns:
            dict: Un diccionario con los KPIs calculados.
        """
        # Implementación de ejemplo para calcular KPIs de interés
        consulta_kpi = f"""
        SELECT town_name, AVG(signal) as avg_signal
        FROM `{self.nombre_tabla}`
        GROUP BY town_name
        ORDER BY avg_signal
        """
        tarea_consulta = self.cliente.query(consulta_kpi)
        return {fila["town_name"]: fila["avg_signal"] for fila in tarea_consulta}

    def identificar_zonas_baja_cobertura(self) -> List[str]:
        """Identifica zonas con baja cobertura de red móvil.

        Returns:
            List[str]: Lista de nombres de ciudades con baja cobertura.
        """
        # Implementación de ejemplo para identificar zonas con baja cobertura
        limite_cobertura = 10  # Valor de umbral para considerar baja cobertura
        consulta_baja_cobertura = f"""
        SELECT town_name
        FROM `{self.nombre_tabla}`
        GROUP BY town_name
        HAVING AVG(signal) < {limite_cobertura}
        """
        tarea_consulta = self.cliente.query(consulta_baja_cobertura)
        return [fila["town_name"] for fila in tarea_consulta]
