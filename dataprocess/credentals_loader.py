from google.oauth2 import service_account
from google.oauth2.service_account import Credentials


def load_credentials(ruta_credenciales: str) -> Credentials:
    """
    Carga un archivo de credenciales de Google Cloud y devuelve un objeto de credenciales.

    Args:
        ruta_credenciales (str): La ruta al archivo de credenciales de la cuenta de servicio de Google Cloud.

    Returns:
        Credentials: Un objeto de credenciales de Google Cloud.

    Ejemplo:
        credenciales = load_credentials('ruta/a/tu/archivo/credenciales.json')
    """
    # Carga las credenciales
    credenciales = service_account.Credentials.from_service_account_file(
        ruta_credenciales
    )

    return credenciales
