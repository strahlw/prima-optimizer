#################################################################################
# PRIMO - The P&A Project Optimizer was produced under the Methane Emissions
# Reduction Program (MERP) and National Energy Technology Laboratory's (NETL)
# National Emissions Reduction Initiative (NEMRI).
#
# NOTICE. This Software was developed under funding from the U.S. Government
# and the U.S. Government consequently retains certain rights. As such, the
# U.S. Government has been granted for itself and others acting on its behalf
# a paid-up, nonexclusive, irrevocable, worldwide license in the Software to
# reproduce, distribute copies to the public, prepare derivative works, and
# perform publicly and display publicly, and to permit others to do so.
#################################################################################


# Installed libs
import fastapi
from fastapi.testclient import TestClient

# User-defined libs
from main import app

client = TestClient(app)


def test_health_check():
    """
    Check for health_check function
    """
    response = client.get("/ping")
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.text == '"PRIMO API is running!"'


def test_home_page():
    """
    Check for home_page function
    """
    response = client.get("/")
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to the PRIMO API!"}
    # Adding a dummy parameter. Should be ignored
    response = client.get("/?param='test'")
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to the PRIMO API!"}
    # Use wrong request type
    response = client.post("/")
    assert response.status_code == fastapi.status.HTTP_405_METHOD_NOT_ALLOWED


def test_uptime():
    """
    Checks for the uptime function
    """
    response = client.get("/uptime")
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json()["Status"] == "OK"
    uptime = response.json()["Uptime"]

    response = client.get("/uptime")
    assert response.status_code == fastapi.status.HTTP_200_OK
    new_uptime = response.json()["Uptime"]

    # New uptime should be longer (even as string object)
    assert new_uptime > uptime
