""" PIDINST Instrument 
Research Instrument module following the PIDINST schema  

"""

import requests
import uuid
from vocabs import INSTRUMENT_IDENTIFIER_TYPES, OWNER_IDENTIFIER_TYPES, MANUFACTURER_IDENTIFIER_TYPES, RELATED_IDENTIFIER_TYPES, RELATED_IDENTIFIER_RELATION_TYPES 
from config import DATACITE_URL
from datacite_utils import datacite_login, generate_datacite_payload


class PIDInst():
    """
    Research Instrument class following the PIDInst Schema (Version 1.0). 
    See https://doi.org/10.15497/RDA00070

    Args:
        Name (mandatory): Common name of the Instrument Instance   
        landing_page: URL of instrument landing page (must begin 'http' or 'https')

    """

    # Current PIDInst schema version
    _schema_version = 1.0

    def __init__(self, landing_page:str = None, name:str = None, description:str = None, model:object = None, owners:list = None, manufacturers:list = None, related_identifiers:list = None):
        # self.local_id = str(uuid.uuid4())
        self.identifier = None
        self.landing_page = landing_page
        self.name = name
        self.owners = [] if owners is None else owners
        self.manufacturers = [] if manufacturers is None else manufacturers
        self.description = description
        self.model = model
        self.related_identifiers = [] if related_identifiers is None else related_identifiers

    def __str__(self):
        return f'PIDInst Instrument {self.name}'

    def __repr__(self):
        return f"PIDInst Instrument('{self.name}')"

    @property
    def landing_page(self):
        return self._landing_page
    
    @landing_page.setter
    def landing_page(self, value):
        if value is not None:
            if not isinstance(value, str):
                raise TypeError("landing_page must be a string")
            if not value.startswith('http'):
                raise ValueError("landing_page must start with either http or https")
        self._landing_page = value

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if value is None:
            raise ValueError("name cannot be None")
        if not isinstance(value, str):
            raise TypeError("name must be a string")
        if value == '':
            raise ValueError("name cannot be an empty string")
        if len(value) >= 200:
            raise ValueError("name must be less than 200 chars")
        self._name = value

    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        if value is not None:
            if not isinstance(value, str):
                raise TypeError("description must be a string")
        self._description = value

    @property
    def owners(self):
        return self._owners
    
    @owners.setter
    def owners(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise TypeError("owners must be a list of Owner objects")
            if not all(isinstance(entry, Owner) for entry in value):
                raise TypeError("owners must be a list of Owner objects")
        self._owners = value

    @property
    def manufacturers(self):
        return self._manufacturers
    
    @manufacturers.setter
    def manufacturers(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise TypeError("manufacturers must be a list of Manufacturer objects")
            if not all(isinstance(entry, Manufacturer) for entry in value):
                raise TypeError("manufacturers must be a list of Manufacturer objects")
        self._manufacturers = value

    @property
    def related_identifiers(self):
        return self._related_identifiers
    
    @related_identifiers.setter
    def related_identifiers(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise TypeError("related_identifiers must be a list of Related Identifier objects")
            if not all(isinstance(entry, RelatedIdentifier) for entry in value):
                raise TypeError("related_identifiers must be a list of RelatedIdentifier objects")
        self._related_identifiers = value

    def set_identifier(self, identifier):
        if self.identifier:
            raise ValueError("This Instrument record already has an identifier allocated")
          
        if not isinstance(identifier, Identifier):
            raise TypeError("Identifier must be instance of Identifier class")
        self.identifier = identifier

    def append_owner(self, owner):          
        if not isinstance(owner, Owner):
            raise TypeError("owner must be instance of Owner class")
        self.owners.append(owner)

    def append_manufacturer(self, manufacturer):          
        if not isinstance(manufacturer, Manufacturer):
            raise TypeError("manufacturer must be instance of Manufacturer class")
        self.manufacturers.append(manufacturer)

    def append_related_identifier(self, related_identifier):          
        if not isinstance(related_identifier, RelatedIdentifier):
            raise TypeError("related_identifier must be instance of RelatedIdentifier class")
        self.related_identifiers.append(related_identifier)

    def set_model(self, model):          
        if not isinstance(model, Model):
            raise TypeError("model must be instance of Model class")
        self.model = model

    def is_valid_for_doi(self):
        ''' Returns whether or not record is valid for doi allocation via Datacite '''

        if self._schema_version and self.landing_page and self.name and len(self.manufacturers) and len(self.owners) > 0 and self.identifier is None:
            return True
        
        return False

    def is_valid_pidinst(self):
        ''' Returns whether or not record is valid PIDInst (all mandatory fields present) '''

        if self._schema_version and self.landing_page and self.name and self.manufacturers and self.identifier and self.owners:
            return True
        
        return False


class Instrument(PIDInst):
    """
    Research Instrument

    Args:
        Name (mandatory): Common name of the Instrument Instance   
        landing_page: URL of instrument landing page (must begin 'http' or 'https')

    """

    def __init__(self, landing_page:str = None, name:str = None, description:str = None, model:object = None, owners:list=None, manufacturers:list=None, related_identifiers:list=None):
        super().__init__(landing_page, name, description, model, owners, manufacturers, related_identifiers)
        self.local_id = str(uuid.uuid4())

    def allocate_doi(self):
        ''' Allocate a new DOI identifier to this Instrument ''' 

        # Check if an identifier already exists and exit if so
        if self.identifier:
            raise ValueError("This Instrument record already has an identifier allocated")
        
        if not self.is_valid_for_doi():
            raise ValueError("This record does not yet have sufficient content to allocate a DOI")
        
        # Set up Datacite POST parameters 
        datacite_token = datacite_login()
        url = DATACITE_URL
        datacite_payload = generate_datacite_payload(self)

        headers = {
            "accept": "application/vnd.api+json",
            "content-type": "application/json",
            'authorization': datacite_token
        }

        try:
            resp = requests.post(url, json=datacite_payload, headers=headers) 
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        identifier = Identifier(identifier_value=resp.json()['data']['id'], identifier_type="DOI")
        self.set_identifier(identifier)


class Identifier():
    """ Persistent Identifier """

    def __init__(self, identifier_value:str = None, identifier_type:str = None):
        self.identifier_value = identifier_value
        self.identifier_type = identifier_type

    def __str__(self):
        return f'Identifier {self.identifier_value}'

    def __repr__(self):
        return f"Identifier ('{self.identifier_value}', '{self.identifier_type}')"
    
    @property
    def identifier_value(self):
        return self._identifier_value
    
    @identifier_value.setter
    def identifier_value(self, value):
        if value is None:
            raise ValueError("Identifier Value cannot be None")
        if not isinstance(value, str):
            raise TypeError("Identifier Value must be a string")
        if value == '':
            raise ValueError("Identifier Value cannot be an empty string")
        if len(value) >= 200:
            raise ValueError("Identifier Value must be less than 200 chars")
        self._identifier_value = value
    
    @property
    def identifier_type(self):
        return self._identifier_type
    
    @identifier_type.setter
    def identifier_type(self, value):
        if value is None:
            raise ValueError("Identifier Type cannot be None")
        if not isinstance(value, str):
            raise TypeError("Identifier Type must be a string")
        if value not in INSTRUMENT_IDENTIFIER_TYPES:
            raise ValueError("Identifier Type not recognised")
        self._identifier_type = value


class OwnerIdentifier():
    """ PIDInst Owner Identifier """

    def __init__(self, owner_identifier_value:str = None, owner_identifier_type:str = None):
        self.owner_identifier_value = owner_identifier_value
        self.owner_identifier_type = owner_identifier_type

    def __str__(self):
        return f'Owner Identifier {self.owner_identifier_value}'

    def __repr__(self):
        return f"Owner Identifier ('{self.owner_identifier_value}', '{self.owner_identifier_type}')"
    
    @property
    def owner_identifier_value(self):
        return self._owner_identifier_value
    
    @owner_identifier_value.setter
    def owner_identifier_value(self, value):
        if value is None:
            raise ValueError("Owner Identifier Value cannot be None")
        if not isinstance(value, str):
            raise TypeError("Owner Identifier Value must be a string")
        self._owner_identifier_value = value
    
    @property
    def owner_identifier_type(self):
        return self._owner_identifier_type
    
    @owner_identifier_type.setter
    def owner_identifier_type(self, value):
        if value is None:
            raise ValueError("Owner Identifier Type cannot be None")
        if not isinstance(value, str):
            raise TypeError("Owner Identifier Type must be a string")
        if value not in OWNER_IDENTIFIER_TYPES:
            raise ValueError("Owner Identifier Type not recognised")
        self._owner_identifier_type = value


class Owner():
    """ Owner Class """

    def __init__(self, owner_name:str = None, owner_contact:str = None):
        self.owner_identifier = None
        self.owner_name = owner_name
        self.owner_contact = owner_contact

    def __str__(self):
        return f'Owner {self.owner_name}'

    def __repr__(self):
        return f"Owner ('{self.owner_name}')"
    
    @property
    def owner_name(self):
        return self._owner_name
    
    @owner_name.setter
    def owner_name(self, value):
        if value is None:
            raise ValueError("owner_name cannot be None")
        if not isinstance(value, str):
            raise TypeError("owner_name must be a string")
        if value == '':
            raise ValueError("Owner name cannot be an empty string")
        if len(value) >= 200:
            raise ValueError("Owner name must be less than 200 chars")
        self._owner_name = value
    
    @property
    def owner_contact(self):
        return self._owner_contact
    
    @owner_contact.setter
    def owner_contact(self, value):
        if value is not None:
            if not isinstance(value, str):
                raise TypeError("owner_contact must be a string")
        self._owner_contact = value

    def set_owner_identifier(self, owner_identifier):
      if self.owner_identifier:
          raise ValueError("This owner record already has an owner identifier allocated")
          
      if not isinstance(owner_identifier, OwnerIdentifier):
          raise TypeError("Owner Identifier must be instance of OwnerIdentifier class")
      self.owner_identifier = owner_identifier
    

class ManufacturerIdentifier():
    """ PIDInst Manufacturer Identifier """

    def __init__(self, manufacturer_identifier_value:str = None, manufacturer_identifier_type:str = None):
        self.manufacturer_identifier_value = manufacturer_identifier_value
        self.manufacturer_identifier_type = manufacturer_identifier_type

    def __str__(self):
        return f'Manufacturer Identifier {self.manufacturer_identifier_value}'

    def __repr__(self):
        return f"Manufacturer Identifier ('{self.manufacturer_identifier_value}', '{self.manufacturer_identifier_type}')"
    
    @property
    def manufacturer_identifier_value(self):
        return self._manufacturer_identifier_value
    
    @manufacturer_identifier_value.setter
    def manufacturer_identifier_value(self, value):
        if value is None:
            raise ValueError("Manufacturer Identifier Value cannot be None")
        if not isinstance(value, str):
            raise TypeError("Manufacturer Identifier Value must be a string")
        self._manufacturer_identifier_value = value
    
    @property
    def manufacturer_identifier_type(self):
        return self._manufacturer_identifier_type
    
    @manufacturer_identifier_type.setter
    def manufacturer_identifier_type(self, value):
        if value is None:
            raise ValueError("Manufacturer Identifier Type cannot be None")
        if not isinstance(value, str):
            raise TypeError("Manufacturer Identifier Type must be a string")
        if value not in MANUFACTURER_IDENTIFIER_TYPES:
            raise ValueError("Manufacturer Identifier Type not recognised")
        self._manufacturer_identifier_type = value


class Manufacturer():
    """ Manufacturer Class """

    def __init__(self, manufacturer_name:str = None):
        self.manufacturer_identifier = None
        self.manufacturer_name = manufacturer_name

    def __str__(self):
        return f'Manufacturer {self.manufacturer_name}'

    def __repr__(self):
        return f"Manufacturer ('{self.manufacturer_name}')"
    
    @property
    def manufacturer_name(self):
        return self._manufacturer_name
    
    @manufacturer_name.setter
    def manufacturer_name(self, value):
        if value is None:
            raise ValueError("manufacturer_name cannot be None")
        if not isinstance(value, str):
            raise TypeError("manufacturer_name must be a string")
        if value == '':
            raise ValueError("manufacturer_name cannot be an empty string")
        if len(value) >= 200:
            raise ValueError("manufacturer_name must be less than 200 chars")
        self._manufacturer_name = value

    def set_manufacturer_identifier(self, manufacturer_identifier):
      if self.manufacturer_identifier:
          raise ValueError("This manufacturer record already has an manufacturer identifier allocated")
          
      if not isinstance(manufacturer_identifier, ManufacturerIdentifier):
          raise TypeError("Manufacturer Identifier must be instance of ManufacturerIdentifier class")
      self.manufacturer_identifier = manufacturer_identifier


class ModelIdentifier():
    """ Instrument Model Identifier """

    def __init__(self, model_identifier_value:str = None, model_identifier_type:str = None):
        self.model_identifier_value = model_identifier_value
        self.model_identifier_type = model_identifier_type

    def __str__(self):
        return f'Model Identifier {self.model_identifier_value}'

    def __repr__(self):
        return f"Model Identifier ('{self.model_identifier_value}', '{self.model_identifier_type}')"
    
    @property
    def model_identifier_value(self):
        return self._model_identifier_value
    
    @model_identifier_value.setter
    def model_identifier_value(self, value):
        if value is None:
            raise ValueError("Model Identifier Value cannot be None")
        if not isinstance(value, str):
            raise TypeError("Model Identifier Value must be a string")
        self._model_identifier_value = value
    
    @property
    def model_identifier_type(self):
        return self._model_identifier_type
    
    @model_identifier_type.setter
    def model_identifier_type(self, value):
        if value is None:
            raise ValueError("Model Identifier Type cannot be None")
        if not isinstance(value, str):
            raise TypeError("Model Identifier Type must be a string")
        self._manufacturer_identifier_type = value


class Model():
    """ Instrument Model Class """

    def __init__(self, model_name:str = None):
        self.model_identifier = None
        self.model_name = model_name

    def __str__(self):
        return f'Model {self.model_name}'

    def __repr__(self):
        return f"Model ('{self.model_name}')"
    
    @property
    def model_name(self):
        return self._model_name
    
    @model_name.setter
    def model_name(self, value):
        if value is None:
            raise ValueError("model_name cannot be None")
        if not isinstance(value, str):
            raise TypeError("model_name must be a string")
        if value == '':
            raise ValueError("model_name cannot be an empty string")
        if len(value) >= 200:
            raise ValueError("model_name must be less than 200 chars")
        self._model_name = value

    def set_model_identifier(self, model_identifier):
      if self.model_identifier:
          raise ValueError("This model record already has an model identifier allocated")
          
      if not isinstance(model_identifier, ModelIdentifier):
          raise TypeError("Model Identifier must be instance of ModelIdentifier class")
      self.model_identifier = model_identifier


class RelatedIdentifier():
    """ Related Identifier Class """

    def __init__(self, related_identifier_value:str = None, related_identifier_type:str = None, related_identifier_relation_type:str = None, related_identifier_name:str = None):
        self.related_identifier_value = related_identifier_value
        self.related_identifier_type = related_identifier_type
        self.related_identifier_relation_type = related_identifier_relation_type
        self.related_identifier_name = related_identifier_name

    def __str__(self):
        return f'Related Identifier {self.related_identifier_value}'

    def __repr__(self):
        return f"Related Identifier ('{self.related_identifier_value}')"
    
    @property
    def related_identifier_value(self):
        return self._related_identifier_value
    
    @related_identifier_value.setter
    def related_identifier_value(self, value):
        if value is None:
            raise ValueError("related_identifier_value cannot be None")
        if not isinstance(value, str):
            raise TypeError("related_identifier_value must be a string")
        if value == '':
            raise ValueError("related_identifier_value cannot be an empty string")
        if len(value) >= 200:
            raise ValueError("related_identifier_value must be less than 200 chars")
        self._related_identifier_value = value
    
    @property
    def related_identifier_type(self):
        return self._related_identifier_type
    
    @related_identifier_type.setter
    def related_identifier_type(self, value):
        if value is None:
            raise ValueError("related_identifier_type cannot be None")
        if not isinstance(value, str):
            raise TypeError("related_identifier_type must be a string")
        if value not in RELATED_IDENTIFIER_TYPES:
            raise ValueError("Related Identifier Type not recognised")
        self._related_identifier_type = value
    
    @property
    def related_identifier_relation_type(self):
        return self._related_identifier_relation_type
    
    @related_identifier_relation_type.setter
    def related_identifier_relation_type(self, value):
        if value is None:
            raise ValueError("related_identifier_relation_type cannot be None")
        if not isinstance(value, str):
            raise TypeError("related_identifier_relation_type must be a string")
        if value not in RELATED_IDENTIFIER_RELATION_TYPES:
            raise ValueError("Related Identifier Relation Type not recognised")
        self._related_identifier_relation_type = value

        
    @property
    def related_identifier_name(self):
        return self._related_identifier_name
    
    @related_identifier_name.setter
    def related_identifier_name(self, value):
        if value is not None:
            if not isinstance(value, str):
                raise TypeError("related_identifier_name must be a string")
            if value == '':
                raise ValueError("related_identifier_name cannot be an empty string")

        self._related_identifier_name = value

    