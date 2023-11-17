# -*- coding: utf-8 -*-
"""Main module template with example functions."""


from typing import Any, Dict, Union, Literal, Tuple
from google.cloud import bigquery
import pandas as pd
from google.oauth2.service_account import Credentials
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib


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
        self.dataframe = pd.DataFrame()
        self.map = None

    def seleccionar_datos(self, parametros_busqueda: Dict[str, Any]) -> pd.DataFrame:
        """Realiza una consulta a BigQuery basada en parámetros de búsqueda específicos.

        Args:
            parametros_busqueda (Dict[str, Any]): Diccionario con los parámetros de búsqueda.

        Returns:
            DataFrame: DataFrame de resultados de la consulta.
        """
        # Construir la consulta SQL basada en los parámetros de búsqueda
        consulta = f"SELECT * FROM `{self.nombre_tabla}` WHERE "
        condiciones = " AND ".join(
            [f"{key} = '{value}'" for key, value in parametros_busqueda.items()]
        )
        consulta_completa = consulta + condiciones

        # Realizar la consulta y retornar los resultados
        tarea_consulta = self.cliente.query(consulta_completa)
        self.dataframe = tarea_consulta.to_dataframe()
        return self.dataframe

    def generar_kpi_cobertura(self, metric: str) -> pd.DataFrame:
        """Genera KPIs relacionados con la cobertura de la red móvil.

        Returns:
            DataFrame: Un DataFrame con los KPIs calculados.
        """
        # Implementación de ejemplo para calcular KPIs de interés
        consulta_kpi = f"""
        SELECT town_name, postal_code, {metric}(signal) as signal
        FROM `{self.nombre_tabla}`
        GROUP BY town_name, postal_code
        """
        tarea_consulta = self.cliente.query(consulta_kpi)
        self.dataframe = tarea_consulta.to_dataframe()
        return self.dataframe

    def set_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Asigna un DataFrame a la clase

        Returns:
            DataFrame: Devuelve el DataFrame.
        """
        self.dataframe = dataframe
        return self.dataframe

    def set_map(self, map_path: str) -> None:
        """Carga un mapa a la clase a partir del path.

        Returns:
            None
        """
        self.map = gpd.read_file(map_path)
        return

    def generar_coordenadas(self) -> pd.DataFrame:
        """Genera una tabla de coordenadas geograficas de los puntos de los pueblos.

        Returns:
            DataFrame: Un DataFrame con las coordenadas calculados.
        """
        # Implementación de ejemplo para calcular KPIs de interés
        consulta_kpi = f"""
        SELECT town_name, postal_code, long, lat
        FROM `{self.nombre_tabla}`
        WHERE town_name IS NOT NULL
        GROUP BY town_name, postal_code, long, lat
        """
        tarea_consulta = self.cliente.query(consulta_kpi)
        self.dataframe = tarea_consulta.to_dataframe()
        self.dataframe = (
            self.dataframe.groupby(["town_name", "postal_code"])[["long", "lat"]]
            .mean()
            .reset_index()
        )
        return self.dataframe

    def generate_map_plot(
        self,
        operation: Union[Literal["point_count", "count", "aggregate"], None] = None,
        aggregated_column: Union[str, None] = None,
        figsize: Tuple[int] = (10, 10),
        color: str = "yellow",
        markersize: int = 5,
        legend_title: str = "",
    ) -> None:
        if "long" not in self.dataframe.columns or "lat" not in self.dataframe.columns:
            raise Exception("Missing columns long or lat in the current DataFrame")
        # Convert the DataFrame to a GeoDataFrame
        gdf_points = gpd.GeoDataFrame(
            self.dataframe,
            geometry=gpd.points_from_xy(self.dataframe["long"], self.dataframe["lat"]),
        )

        # Ensure the CRS of both GeoDataFrames are the same
        gdf_points.crs = self.map.crs

        points_within_cat = gpd.sjoin(
            gdf_points, self.map, how="inner", predicate="within"
        )
        fig, ax = plt.subplots(figsize=figsize)

        if operation is None:
            self.map.plot(ax=ax)  # Plot the base map
            points_within_cat.plot(
                ax=ax, marker="o", color=color, markersize=markersize
            )  # Plot the points

        elif operation == "point_count":
            if aggregated_column not in self.dataframe.columns:
                raise Exception(
                    f"Column not present in dataframe. Looking for {aggregated_column} in a dataframe with columns {self.dataframe.columns}"
                )
            norm = mcolors.Normalize(
                vmin=points_within_cat[aggregated_column].min(),
                vmax=points_within_cat[aggregated_column].max(),
            )
            cmap = plt.cm.RdYlGn

            self.map.plot(ax=ax)  # Plot the base map

            # Create a scatter plot for the points
            scatter = ax.scatter(
                points_within_cat["long"],
                points_within_cat["lat"],
                c=points_within_cat[aggregated_column],
                cmap=cmap,
                norm=norm,
                marker="o",
                linewidth=0.5,
                s=10,
            )
            if legend_title != "":
                # Create a colorbar as a legend
                cbar = fig.colorbar(
                    scatter, ax=ax, orientation="vertical", shrink=0.7, aspect=20
                )
                cbar.set_label(legend_title)
        elif operation == "count":
            # Count the number of points within each polygon and give the series a name
            point_counts = (
                points_within_cat.groupby("index_right").size().rename("point_count")
            )

            # Merge these counts back into the 'cat' GeoDataFrame
            cat_with_counts = self.map.join(point_counts, how="left")
            cat_with_counts.fillna(
                0, inplace=True
            )  # Replace NaN with 0 for polygons with no points

            cat_with_counts.plot(
                column="point_count", ax=ax, legend=False
            )  # Turn off default legend

            # Create a color bar manually
            if legend_title != "":
                norm = matplotlib.colors.Normalize(
                    vmin=cat_with_counts["point_count"].min(),
                    vmax=cat_with_counts["point_count"].max(),
                )
                sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
                sm._A = []  # Dummy array for the ScalarMappable
                cbar = fig.colorbar(
                    sm, ax=ax, orientation="vertical", shrink=0.7, aspect=20
                )
                cbar.set_label(legend_title)
        elif operation == "aggregate":
            # Count the number of 'adult' individuals within each polygon
            if aggregated_column not in self.dataframe.columns:
                raise Exception(
                    f"Column not present in dataframe. Looking for {aggregated_column} in a dataframe with columns {self.dataframe.columns}"
                )
            aggregate = (
                points_within_cat.groupby("index_right")[aggregated_column]
                .sum()
                .rename("count_column")
            )

            # Merge these counts back into the 'cat' GeoDataFrame
            cat_with_counts = self.map.join(aggregate, how="left")
            cat_with_counts.fillna(
                0, inplace=True
            )  # Replace NaN with 0 for polygons with no adults

            cat_with_counts.plot(
                column="count_column", ax=ax, legend=False, cmap="viridis"
            )  # Use a colormap of your choice
            if legend_title != "":
                # Create a color bar manually
                norm = matplotlib.colors.Normalize(
                    vmin=cat_with_counts["count_column"].min(),
                    vmax=cat_with_counts["count_column"].max(),
                )
                sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
                sm._A = []  # Dummy array for the ScalarMappable
                cbar = fig.colorbar(
                    sm, ax=ax, orientation="vertical", shrink=0.7, aspect=20
                )
                cbar.set_label(legend_title)
        else:
            raise Exception(
                "Invalid operations. Accpeted: None, point_count, count and aggregate"
            )
        plt.show()
        return
