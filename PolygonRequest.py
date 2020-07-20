import requests

def PolygonRequest(address):
    '''
        Returns the polygon coordinates of the chosen building.

        Parameters:
            address(str):The address of the building.

        Returns:
            polygon(list):The coordinates of the building.
    '''

    # Split the address
    req = requests.get(f"https://loc.geopunt.be/v4/Location?q={address}").json()

    city = req["LocationResult"][0]["Municipality"]
    street = req["LocationResult"][0]["Thoroughfarename"]
    nb = req["LocationResult"][0]["Housenumber"]
    pc = req["LocationResult"][0]["Zipcode"]

    req = requests.get(
        f"https://api.basisregisters.dev-vlaanderen.be/v1/adresmatch?gemeentenaam={city}&straatnaam={street}&huisnummer={nb}&postcode={pc}").json()

    objectId = req["adresMatches"][0]["adresseerbareObjecten"][0]["objectId"]

    req = requests.get(f"https://api.basisregisters.dev-vlaanderen.be/v1/gebouweenheden/{objectId}").json()
    objectId = req["gebouw"]["objectId"]

    req = requests.get(f"https://api.basisregisters.dev-vlaanderen.be/v1/gebouwen/{objectId}").json()
    polygon = [req["geometriePolygoon"]["polygon"]]

    return polygon
