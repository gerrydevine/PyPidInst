import os
import datetime
from dotenv import load_dotenv
from base64 import b64encode
from config import DOI_PREFIX

load_dotenv()


def datacite_login():
    ''' Login to DATACITE
    - Returns a Basic Auth Token 

    '''
    datacite_username = os.environ.get('DATACITE_USERNAME')
    datacite_password = os.environ.get('DATACITE_PASSWORD')
    datacite_token = b64encode(f"{datacite_username.upper()}:{datacite_password}".encode('utf-8')).decode("ascii")

    return f"Basic {datacite_token}"


def generate_datacite_payload(pidinst_metadata):
    ''' Map PIDInst metadata to a Datacite-friendly payload '''

    # Create new skeleton object to store instrument payload
    payload = {}
    payload["data"] = {}
    payload["data"]["type"] = 'dois'
    
    # Create empty Attributes dictionary then populate
    attrs = {}

    # SET DOI PREFIX
    attrs["prefix"] = DOI_PREFIX

    # SET PUBLISHER (DEFAULTING TO UNSW)
    attrs["publisher"] = {
        "name": "UNSW Sydney",
        "publisherIdentifier":"https://ror.org/03r8z3t63",
        "publisherIdentifierScheme":"ROR",
        "schemeUri": "https://ror.org/"
    },
    
    # SET PUBLICATION YEAR
    attrs["publicationYear"] = datetime.date.today().year

    # SET RESOURCE TYPE
    attrs["types"] = {"resourceTypeGeneral": "Instrument"}

    # SET INSTRUMENT NAME/TITLE
    attrs["titles"] = [
        {
            "title": pidinst_metadata.name
        }
    ]

    # SET URL/LANDING PAGE
    attrs["url"] = pidinst_metadata.landing_page

    # SET INSTRUMENT DESCRIPTION
    attrs['descriptions'] = []
    if pidinst_metadata.description:
        attrs["descriptions"].append(
            {
                "lang": "en-US",
                "description": pidinst_metadata.description,
                "descriptionType": "Abstract"
            }
        )

    # POPULATE DATACITE CREATORS
    creators = []
    for owner in pidinst_metadata.owners:
        c = {}
        c["name"] = owner.owner_name
        c["nameType"] = "Personal"

        # Get ORCID, if existing
        if hasattr(owner, 'owner_identifier'):
            if owner.owner_identifier.owner_identifier_type == 'ORCID':
                c['nameIdentifiers'] = [
                    	{
							"nameIdentifier": f"https://orcid.org/{owner.owner_identifier.owner_identifier_value}",
							"nameIdentifierScheme": "ORCID",
							"schemeUri": "https://orcid.org"
						}
                ]

        # Add Affiliation
        c["affiliation"] = [
            {
              "affiliationIdentifier": "https://ror.org/03r8z3t63",
              "affiliationIdentifierScheme": "ROR",
              "name": "UNSW Sydney",
              "schemeUri": "https://ror.org/"
            }
        ]

        creators.append(c)

    attrs["creators"] = creators


    payload["data"]["attributes"] = attrs

    return payload
