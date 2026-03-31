import unittest
from unittest.mock import patch, Mock
from pypidinst.instrument import PIDInst, Instrument, Identifier, Owner, OwnerIdentifier, Manufacturer, ManufacturerIdentifier, Model, ModelIdentifier, RelatedIdentifier
import requests

class TestInstruments(unittest.TestCase):

    def test_valid_instance_with_identifier(self):
        identifier = Identifier(identifier_value="10.1000/retwebwb", identifier_type="DOI")
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ", 
        )
        instrument.set_identifier(identifier)
        self.assertIsInstance(instrument, Instrument, 'Something is wrong with class instantation')

    def test_valid_instance_without_identifier(self):
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ",
        )
        self.assertIsInstance(instrument, Instrument, 'Something is wrong with class instantation')

    def test_identifier_already_exists(self):
        identifier = Identifier(identifier_value="10.1000/retwebwb", identifier_type="DOI")
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ"
        )
        instrument.set_identifier(identifier)
        with self.assertRaises(ValueError) as exc:
            identifier = Identifier(identifier_value="10.1000/123ABC", identifier_type="DOI")
            instrument.set_identifier(identifier)
        self.assertEqual(str(exc.exception), "This Instrument record already has an identifier allocated")

    def test_non_identifier_object_set(self):
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        dummy_identifier = {'value':'ABC123'}
        with self.assertRaises(TypeError) as exc:
            instrument.set_identifier(dummy_identifier)
        self.assertEqual(str(exc.exception), "Identifier must be instance of Identifier class")

    def test_non_related_identifier_object_set(self):
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        dummy_identifier = {'value':'ABC123'}
        with self.assertRaises(TypeError) as exc:
            instrument.append_related_identifier(dummy_identifier)
        self.assertEqual(str(exc.exception), "related_identifier must be instance of RelatedIdentifier class")

    # SCHEMA VERSION TESTS
    def test_schema_version(self):
        identifier = Identifier(identifier_value="10.1000/retwebwb", identifier_type="DOI")
        instrument = Instrument(landing_page='https://www.landingpage.com', name="Instrument XYZ")
        instrument.set_identifier(identifier)
        self.assertEqual(instrument._schema_version, 1.0, 'The schema version is incorrect')

    # LANDING PAGE TESTS
    def test_non_string_landing_page_error(self):
        with self.assertRaises(TypeError) as exc:
            Instrument(landing_page=101, name="Instrument XYZ")
        self.assertEqual(str(exc.exception), "landing_page must be a string")

    def test_non_http_landing_page_error(self):
        with self.assertRaises(ValueError) as exc:
            Instrument(landing_page='www.landingpage.com', name="Instrument XYZ")
        self.assertEqual(str(exc.exception), "landing_page must be a valid http or https URL")

    # NAME TESTS
    def test_missing_name_error(self):
        """Test that name is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            Instrument(landing_page='https://www.landingpage.com')
        self.assertIn("missing 1 required positional argument: 'name'", str(exc.exception))

    def test_non_string_name_error(self):
        with self.assertRaises(TypeError) as exc:
            Instrument(landing_page="https://mylandingpage.com", name=333)
        self.assertEqual(str(exc.exception), "name must be a string")

    def test_invalid_empty_string_name_error(self):
        with self.assertRaises(ValueError) as exc:
            Instrument(landing_page="https://mylandingpage.com", name="")
        self.assertEqual(str(exc.exception), "name cannot be an empty string")

    def test_name_too_long_error(self):
        with self.assertRaises(ValueError) as exc:
            Instrument(landing_page="https://mylandingpage.com", name="A"*201)
        self.assertEqual(str(exc.exception), "name must be less than 200 chars")

    # INSTRUMENT OWNER TESTS
    def test_valid_owner_object_set_on_init(self):
        owners = []
        owner = Owner(owner_name="Jane Doe", owner_contact="jane.doe@email.com")
        owner_identifier = OwnerIdentifier(owner_identifier_value="0000-ABCD-1234-WXYZ", owner_identifier_type='ORCID') 
        owner.set_owner_identifier(owner_identifier)
        owners.append(owner)
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument', owners=owners)        

        self.assertIsInstance(instrument, Instrument, 'Something went wrong with class instantation')
        self.assertIsInstance(instrument.owners[0], Owner, 'Something went wrong with class instantation')

    def test_invalid_non_owner_object_set_on_init(self):
        owners = []
        owner = {'owner_name':"Jane Doe", 'owner_contact':"jane.doe@email.com"}
        owners.append(owner)

        with self.assertRaises(TypeError) as exc:
            Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument', owners=owners)    
        self.assertEqual(str(exc.exception), "owners must be a list of Owner objects")    

    def test_invalid_non_owner_object_set_post_init(self):
        owners = []
        owner = {'owner_name':"Jane Doe", 'owner_contact':"jane.doe@email.com"}
        owners.append(owner)
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        self.assertIsInstance(instrument, Instrument, 'Something went wrong with class instantation')

        with self.assertRaises(TypeError) as exc:
            instrument.owners = owners    
        self.assertEqual(str(exc.exception), "owners must be a list of Owner objects")    

    def test_valid_owner_object_append(self):
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        owner = Owner(owner_name="Jane Doe", owner_contact="jane.doe@email.com")
        owner_identifier = OwnerIdentifier(owner_identifier_value="0000-ABCD-1234-WXYZ", owner_identifier_type='ORCID') 
        owner.set_owner_identifier(owner_identifier)
        instrument.append_owner(owner)

        self.assertIsInstance(instrument, Instrument, 'Something went wrong with class instantation')
        self.assertIsInstance(instrument.owners[0], Owner, 'Something went wrong with class instantation')

    def test_non_owner_object_append(self):
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        dummy_owner = {'name':'Jane Doe'}
        with self.assertRaises(TypeError) as exc:
            instrument.append_owner(dummy_owner)
        self.assertEqual(str(exc.exception), "owner must be instance of Owner class")

    # INSTRUMENT MANUFACTURER TESTS
    def test_valid_manufacturer_object_set_on_init(self):
        manufacturers = []
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        manufacturer_identifier = ManufacturerIdentifier(manufacturer_identifier_value="https://www.acme.com", manufacturer_identifier_type='URL') 
        manufacturer.set_manufacturer_identifier(manufacturer_identifier)
        manufacturers.append(manufacturer)

        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument', manufacturers=manufacturers)        

        self.assertIsInstance(instrument, Instrument, 'Something went wrong with class instantation')
        self.assertIsInstance(instrument.manufacturers[0], Manufacturer, 'Something went wrong with class instantation')

    def test_invalid_non_manufacturer_object_set_on_init(self):
        manufacturers = []
        manufacturer = {'manufacturer_identifier_valu':"https://www.acme.com", 'manufacturer_identifier_type':'URL'}
        manufacturers.append(manufacturer)

        with self.assertRaises(TypeError) as exc:
            Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument', manufacturers=manufacturers)    
        self.assertEqual(str(exc.exception), "manufacturers must be a list of Manufacturer objects")    

    def test_invalid_non_manufacturer_object_set_post_init(self):
        manufacturers = []
        manufacturer = {'manufacturer_identifier_valu':"https://www.acme.com", 'manufacturer_identifier_type':'URL'}
        manufacturers.append(manufacturer)
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        self.assertIsInstance(instrument, Instrument, 'Something went wrong with class instantation')

        with self.assertRaises(TypeError) as exc:
            instrument.manufacturers = manufacturers    
        self.assertEqual(str(exc.exception), "manufacturers must be a list of Manufacturer objects") 

    def test_valid_manufacturer_object_append(self):
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        manufacturer_identifier = ManufacturerIdentifier(manufacturer_identifier_value="https://www.acme.com", manufacturer_identifier_type='URL') 
        manufacturer.set_manufacturer_identifier(manufacturer_identifier)
        instrument.append_manufacturer(manufacturer)

        self.assertIsInstance(instrument, Instrument, 'Something went wrong with class instantation')
        self.assertIsInstance(instrument.manufacturers[0], Manufacturer, 'Something went wrong with class instantation')

    def test_non_manufacturer_object_append(self):
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        dummy_manufacturer = {'name':'Manufacturer X'}
        with self.assertRaises(TypeError) as exc:
            instrument.append_manufacturer(dummy_manufacturer)
        self.assertEqual(str(exc.exception), "manufacturer must be instance of Manufacturer class")

    # INSTRUMENT RELATED IDENTIFIER TESTS
    def test_valid_related_identifier_object_set_on_init(self):
        related_identifiers = []
        related_identifier = RelatedIdentifier(related_identifier_value="https://www.pathtopaper.edu.au", related_identifier_type="URL", related_identifier_relation_type="IsDescribedBy", related_identifier_name="Documentation Paper")
        related_identifiers.append(related_identifier)
        instrument = Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument', related_identifiers=related_identifiers)        

        self.assertIsInstance(instrument, Instrument, 'Something went wrong with class instantation')
        self.assertIsInstance(instrument.related_identifiers[0], RelatedIdentifier, 'Something went wrong with class instantation')

    def test_invalid_non_related_identifier_object_set_on_init(self):
        related_identifiers = []
        related = {'related_identifier_value':"https://www.pathtopaper.edu.au", 'related_identifier_type':'URL'}
        related_identifiers.append(related)

        with self.assertRaises(TypeError) as exc:
            Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument', related_identifiers=related_identifiers)    
        self.assertEqual(str(exc.exception), "related_identifiers must be a list of RelatedIdentifier objects")   

    def test_invalid_non_related_identifier_object_set_post_init(self):
        related_identifiers = []
        related = {'related_identifier_value':"https://www.pathtopaper.edu.au", 'related_identifier_type':'URL'}
        related_identifiers.append(related)
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        self.assertIsInstance(instrument, Instrument, 'Something went wrong with class instantation')

        with self.assertRaises(TypeError) as exc:
            instrument.related_identifiers = related_identifiers    
        self.assertEqual(str(exc.exception), "related_identifiers must be a list of RelatedIdentifier objects") 

    def test_valid_related_identifier_object_append(self):
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        related_identifier_1 = RelatedIdentifier(related_identifier_value="https://www.pathtopaper.edu.au", related_identifier_type="URL", related_identifier_relation_type="IsDescribedBy", related_identifier_name="Documentation Paper")
        instrument.append_related_identifier(related_identifier_1)
        related_identifier_2 = RelatedIdentifier(related_identifier_value="https://www.pathtopaper.edu.au", related_identifier_type="URL", related_identifier_relation_type="IsDescribedBy", related_identifier_name="Documentation Paper")
        instrument.append_related_identifier(related_identifier_2)

        self.assertIsInstance(instrument, Instrument, 'Something went wrong with class instantation')
        self.assertIsInstance(instrument.related_identifiers[0], RelatedIdentifier, 'Something went wrong with class instantation')
        self.assertIsInstance(instrument.related_identifiers[1], RelatedIdentifier, 'Something went wrong with class instantation')

    def test_non_related_identifier_object_append(self):
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        dummy_related_identifier = {'name':'Paper X'}
        with self.assertRaises(TypeError) as exc:
            instrument.append_related_identifier(dummy_related_identifier)
        self.assertEqual(str(exc.exception), "related_identifier must be instance of RelatedIdentifier class")

    # INSTRUMENT MODEL TESTS
    def test_valid_model_object_set(self):
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        model = Model(model_name="Model OPQ")
        model_identifier = ModelIdentifier(model_identifier_value="ABC123", model_identifier_type='URL') 
        model.set_model_identifier(model_identifier)
        instrument.set_model(model)

        self.assertIsInstance(instrument, Instrument, 'Something went wrong with class instantation')
        self.assertIsInstance(instrument.model, Model, 'Something went wrong with class instantation')

    def test_non_model_object_set(self):
        instrument =  Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description='A description of this instrument')        
        dummy_model = {'name':'Manufacturer X'}
        with self.assertRaises(TypeError) as exc:
            instrument.set_model(dummy_model)
        self.assertEqual(str(exc.exception), "model must be instance of Model class")

    # DESCRIPTION TESTS
    def test_non_string_description_error(self):
        with self.assertRaises(TypeError) as exc:
            Instrument(landing_page="https://mylandingpage.com", name='Instrument XYZ', description=33)
        self.assertEqual(str(exc.exception), "description must be a string")

    # TEST DOI ALLOCATION
    def test_allocate_doi_identifier_exists(self):
        identifier = Identifier(identifier_value="10.1000/retwebwb", identifier_type="DOI")
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ" 
        )
        instrument.set_identifier(identifier)
        with self.assertRaises(ValueError) as exc:
            instrument.allocate_doi()
        self.assertEqual(str(exc.exception), "This Instrument record already has an identifier allocated")
   
    def test_allocate_doi_non_complete_info(self):
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ"
        )
        with self.assertRaises(ValueError) as exc:
            instrument.allocate_doi()
        self.assertEqual(str(exc.exception), "This record does not yet have sufficient content to allocate a DOI")
   
    def test_allocate_doi_complete_info(self):
        pass

    @patch('pypidinst.instrument.datacite_login')
    @patch('pypidinst.instrument.generate_datacite_payload')
    @patch('pypidinst.instrument.requests.post')
    def test_allocate_doi_http_error_401(self, mock_post, mock_payload, mock_login):
        """Test that HTTP 401 error is properly raised, not SystemExit (Bug #3 regression test)"""
        # Setup
        mock_login.return_value = 'Bearer fake_token'
        mock_payload.return_value = {'data': 'fake_payload'}
        
        # Simulate 401 Unauthorized error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response
        
        # Create valid instrument
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ"
        )
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        owner = Owner(owner_name="Jane Doe")
        instrument.append_owner(owner)
        
        # Should raise HTTPError, not SystemExit
        with self.assertRaises(requests.exceptions.HTTPError) as exc:
            instrument.allocate_doi()
        self.assertIn("401", str(exc.exception))

    @patch('pypidinst.instrument.datacite_login')
    @patch('pypidinst.instrument.generate_datacite_payload')
    @patch('pypidinst.instrument.requests.post')
    def test_allocate_doi_http_error_500(self, mock_post, mock_payload, mock_login):
        """Test that HTTP 500 error is properly raised, not SystemExit (Bug #3 regression test)"""
        # Setup
        mock_login.return_value = 'Bearer fake_token'
        mock_payload.return_value = {'data': 'fake_payload'}
        
        # Simulate 500 Server Error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_post.return_value = mock_response
        
        # Create valid instrument
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ"
        )
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        owner = Owner(owner_name="Jane Doe")
        instrument.append_owner(owner)
        
        # Should raise HTTPError, not SystemExit
        with self.assertRaises(requests.exceptions.HTTPError) as exc:
            instrument.allocate_doi()
        self.assertIn("500", str(exc.exception))

    @patch('pypidinst.instrument.datacite_login')
    @patch('pypidinst.instrument.generate_datacite_payload')
    @patch('pypidinst.instrument.requests.post')
    def test_allocate_doi_timeout(self, mock_post, mock_payload, mock_login):
        """Test that timeout error is properly raised when DataCite API times out"""
        # Setup
        mock_login.return_value = 'Bearer fake_token'
        mock_payload.return_value = {'data': 'fake_payload'}
        
        # Simulate timeout error
        mock_post.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        # Create valid instrument
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ"
        )
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        owner = Owner(owner_name="Jane Doe")
        instrument.append_owner(owner)
        
        # Should raise Timeout exception
        with self.assertRaises(requests.exceptions.Timeout) as exc:
            instrument.allocate_doi()
        self.assertIn("DataCite API request timed out", str(exc.exception))

    @patch('pypidinst.instrument.datacite_login')
    @patch('pypidinst.instrument.generate_datacite_payload')
    @patch('pypidinst.instrument.requests.post')
    def test_allocate_doi_success(self, mock_post, mock_payload, mock_login):
        """Test successful DOI allocation creates and sets an Identifier"""
        # Setup
        mock_login.return_value = 'Bearer fake_token'
        mock_payload.return_value = {'data': 'fake_payload'}
        
        # Simulate successful DataCite response with proper structure
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {
                'id': '10.80402/test-doi-123',
                'type': 'dois',
                'attributes': {'doi': '10.80402/test-doi-123'}
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Create valid instrument
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ"
        )
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        owner = Owner(owner_name="Jane Doe")
        instrument.append_owner(owner)
        
        # Allocate DOI
        instrument.allocate_doi()
        
        # Verify identifier was created and set correctly
        self.assertIsNotNone(instrument.identifier)
        self.assertIsInstance(instrument.identifier, Identifier)
        self.assertEqual(instrument.identifier.identifier_type, "DOI")
        self.assertEqual(instrument.identifier.identifier_value, "10.80402/test-doi-123")

    @patch('pypidinst.instrument.datacite_login')
    @patch('pypidinst.instrument.generate_datacite_payload')
    @patch('pypidinst.instrument.requests.post')
    def test_allocate_doi_invalid_response_not_dict(self, mock_post, mock_payload, mock_login):
        """Test that non-dict response from DataCite is rejected"""
        mock_login.return_value = 'Bearer fake_token'
        mock_payload.return_value = {'data': 'fake_payload'}
        
        # Simulate response that's not a dictionary
        mock_response = Mock()
        mock_response.json.return_value = "not a dict"
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        instrument = Instrument(landing_page='https://www.landingpage.com', name="Instrument XYZ")
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        owner = Owner(owner_name="Jane Doe")
        instrument.append_owner(owner)
        
        with self.assertRaises(ValueError) as exc:
            instrument.allocate_doi()
        self.assertIn("invalid response format", str(exc.exception))

    @patch('pypidinst.instrument.datacite_login')
    @patch('pypidinst.instrument.generate_datacite_payload')
    @patch('pypidinst.instrument.requests.post')
    def test_allocate_doi_missing_data_field(self, mock_post, mock_payload, mock_login):
        """Test that response missing 'data' field is rejected"""
        mock_login.return_value = 'Bearer fake_token'
        mock_payload.return_value = {'data': 'fake_payload'}
        
        # Simulate response missing 'data' field
        mock_response = Mock()
        mock_response.json.return_value = {"wrong_field": "value"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        instrument = Instrument(landing_page='https://www.landingpage.com', name="Instrument XYZ")
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        owner = Owner(owner_name="Jane Doe")
        instrument.append_owner(owner)
        
        with self.assertRaises(ValueError) as exc:
            instrument.allocate_doi()
        self.assertIn("missing required 'data' field", str(exc.exception))

    @patch('pypidinst.instrument.datacite_login')
    @patch('pypidinst.instrument.generate_datacite_payload')
    @patch('pypidinst.instrument.requests.post')
    def test_allocate_doi_missing_id_field(self, mock_post, mock_payload, mock_login):
        """Test that response missing 'id' field is rejected"""
        mock_login.return_value = 'Bearer fake_token'
        mock_payload.return_value = {'data': 'fake_payload'}
        
        # Simulate response with 'data' but missing 'id'
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"other_field": "value"}}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        instrument = Instrument(landing_page='https://www.landingpage.com', name="Instrument XYZ")
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        owner = Owner(owner_name="Jane Doe")
        instrument.append_owner(owner)
        
        with self.assertRaises(ValueError) as exc:
            instrument.allocate_doi()
        self.assertIn("missing required 'id' field", str(exc.exception))

    @patch('pypidinst.instrument.datacite_login')
    @patch('pypidinst.instrument.generate_datacite_payload')
    @patch('pypidinst.instrument.requests.post')
    def test_allocate_doi_empty_doi_value(self, mock_post, mock_payload, mock_login):
        """Test that empty DOI value is rejected"""
        mock_login.return_value = 'Bearer fake_token'
        mock_payload.return_value = {'data': 'fake_payload'}
        
        # Simulate response with empty DOI
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"id": ""}}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        instrument = Instrument(landing_page='https://www.landingpage.com', name="Instrument XYZ")
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        owner = Owner(owner_name="Jane Doe")
        instrument.append_owner(owner)
        
        with self.assertRaises(ValueError) as exc:
            instrument.allocate_doi()
        self.assertIn("empty DOI value", str(exc.exception))

    @patch('pypidinst.instrument.datacite_login')
    @patch('pypidinst.instrument.generate_datacite_payload')
    @patch('pypidinst.instrument.requests.post')
    def test_allocate_doi_invalid_doi_format(self, mock_post, mock_payload, mock_login):
        """Test that DOI not starting with '10.' is rejected"""
        mock_login.return_value = 'Bearer fake_token'
        mock_payload.return_value = {'data': 'fake_payload'}
        
        # Simulate response with invalid DOI format
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"id": "invalid-doi-format"}}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        instrument = Instrument(landing_page='https://www.landingpage.com', name="Instrument XYZ")
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        owner = Owner(owner_name="Jane Doe")
        instrument.append_owner(owner)
        
        with self.assertRaises(ValueError) as exc:
            instrument.allocate_doi()
        self.assertIn("invalid DOI format", str(exc.exception))
        self.assertIn("must start with '10.'", str(exc.exception))


class TestIdentifiers(unittest.TestCase):

    def test_valid_identifier_doi(self):
        identifier = Identifier(identifier_value="10.1000/ABC123", identifier_type="DOI")
        self.assertIsInstance(identifier, Identifier, 'Something went wrong with Identifier class instantation')

    def test_valid_identifier_handle(self):
        identifier = Identifier(identifier_value="2381/12345", identifier_type="Handle")
        self.assertIsInstance(identifier, Identifier, 'Something went wrong with Identifier class instantation')

    def test_missing_identifier_type(self):
        """Test that identifier_type is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            Identifier(identifier_value="2381/12345")
        self.assertIn("missing 1 required positional argument: 'identifier_type'", str(exc.exception))

    def test_invalid_identifier_type_type(self):
        with self.assertRaises(TypeError) as exc:
            Identifier(identifier_value="2381/12345", identifier_type=321)
        self.assertEqual(str(exc.exception), "Identifier Type must be a string")

    def test_invalid_identifier_type(self):
        with self.assertRaises(ValueError) as exc:
            Identifier(identifier_value="2381/12345", identifier_type="DUMMY")
        self.assertEqual(str(exc.exception), "Identifier Type not recognised")

    def test_missing_identifier_value(self):
        """Test that identifier_value is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            Identifier(identifier_type="DOI")
        self.assertIn("missing 1 required positional argument: 'identifier_value'", str(exc.exception))

    def test_invalid_identifier_value_type(self):
        with self.assertRaises(TypeError) as exc:
            Identifier(identifier_value=123, identifier_type="DOI")
        self.assertEqual(str(exc.exception), "Identifier Value must be a string")

    def test_invalid_identifier_value_empty(self):
        with self.assertRaises(ValueError) as exc:
            Identifier(identifier_value='', identifier_type="DOI")
        self.assertEqual(str(exc.exception), "Identifier Value cannot be an empty string")

    def test_identifier_value_too_long_error(self):
        with self.assertRaises(ValueError) as exc:
            Identifier(identifier_value="A"*200, identifier_type='DOI')
        self.assertEqual(str(exc.exception), "Identifier Value must be less than 200 chars")


class TestOwners(unittest.TestCase):

    def test_valid_owner(self):
        owner = Owner(owner_name="Jane Doe", owner_contact="jane.doe@email.com")
        owner_identifier = OwnerIdentifier(owner_identifier_value="0000-ABCD-1234-WXYZ", owner_identifier_type='ORCID') 
        owner.set_owner_identifier(owner_identifier)
        self.assertIsInstance(owner, Owner, 'Something went wrong with owner class instantation')

    def test_valid_owner_no_identifier(self):
        owner = Owner(owner_name="Jane Doe", owner_contact="jane.doe@email.com")
        self.assertIsInstance(owner, Owner, 'Something went wrong with owner class instantation')

    def test_invalid_empty_owner_name(self):
        with self.assertRaises(ValueError) as exc:
            Owner(owner_name="", owner_contact="jane.doe@email.com")
        self.assertEqual(str(exc.exception), "Owner name cannot be an empty string")

    def test_invalid_set_owner_identifier(self):
        owner = Owner(owner_name="Jane Doe", owner_contact="jane.doe@email.com")
        owner_identifier = {'name':'DUMMY'}
        with self.assertRaises(TypeError) as exc:
            owner.set_owner_identifier(owner_identifier)
        self.assertEqual(str(exc.exception), "Owner Identifier must be instance of OwnerIdentifier class")


class TestOwnerIdentifiers(unittest.TestCase):

    def test_missing_owner_identifier_value(self):
        """Test that owner_identifier_value is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            OwnerIdentifier(owner_identifier_type='ORCID') 
        self.assertIn("missing 1 required positional argument", str(exc.exception))

    def test_missing_owner_identifier_type(self):
        """Test that owner_identifier_type is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            OwnerIdentifier(owner_identifier_value='0000-1111-2222-3333') 
        self.assertIn("missing 1 required positional argument", str(exc.exception))

    def test_invalid_owner_identifier_type(self):
        with self.assertRaises(ValueError) as exc:
            OwnerIdentifier(owner_identifier_value="0000-ABCD-1234-WXYZ", owner_identifier_type='DUMMY') 
        self.assertEqual(str(exc.exception), "Owner Identifier Type not recognised")


class TestManufacturers(unittest.TestCase):

    def test_valid_manufacturer(self):
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        manufacturer_identifier = ManufacturerIdentifier(manufacturer_identifier_value="https://www.acme.com", manufacturer_identifier_type='URL') 
        manufacturer.set_manufacturer_identifier(manufacturer_identifier)
        self.assertIsInstance(manufacturer, Manufacturer, 'Something went wrong with manufacturer class instantation')

    def test_valid_manufacturer_no_identifier(self):
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        self.assertIsInstance(manufacturer, Manufacturer, 'Something went wrong with manufacturer class instantation')

    def test_invalid_manufacturer_empty_name(self):
        with self.assertRaises(ValueError) as exc:
            Manufacturer(manufacturer_name="")
        self.assertEqual(str(exc.exception), "manufacturer_name cannot be an empty string")

    def test_invalid_set_manufacturer_identifier(self):
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        manufacturer_identifier = {'value':'DUMMY'}
        with self.assertRaises(TypeError) as exc:
            manufacturer.set_manufacturer_identifier(manufacturer_identifier)
        self.assertEqual(str(exc.exception), "Manufacturer Identifier must be instance of ManufacturerIdentifier class")


class TestManufacturerIdentifiers(unittest.TestCase):
    
    def test_missing_manufacturer_identifier_value(self):
        """Test that manufacturer_identifier_value is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            ManufacturerIdentifier(manufacturer_identifier_type='URL') 
        self.assertIn("missing 1 required positional argument", str(exc.exception))

    def test_missing_manufacturer_identifier_type(self):
        """Test that manufacturer_identifier_type is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            ManufacturerIdentifier(manufacturer_identifier_value='0000-1111-2222-3333') 
        self.assertIn("missing 1 required positional argument", str(exc.exception))

    def test_invalid_manufacturer_identifier_type(self):
        with self.assertRaises(ValueError) as exc:
            ManufacturerIdentifier(manufacturer_identifier_value="0000-ABCD-1234-WXYZ", manufacturer_identifier_type='DUMMY') 
        self.assertEqual(str(exc.exception), "Manufacturer Identifier Type not recognised")


class TestModels(unittest.TestCase):

    def test_valid_model_with_identifier(self):
        model = Model(model_name="Acme Inc")
        model_identifier = ModelIdentifier(model_identifier_value="ABC123", model_identifier_type='URL') 
        model.set_model_identifier(model_identifier)
        self.assertIsInstance(model, Model, 'Something went wrong with model class instantation')

    def test_valid_model_without_identifier(self):
        model = Model(model_name="Acme Inc")
        self.assertIsInstance(model, Model, 'Something went wrong with model class instantation')

    def test_invalid_model_empty_name(self):
        with self.assertRaises(ValueError) as exc:
            Model(model_name="")
        self.assertEqual(str(exc.exception), "model_name cannot be an empty string")

    def test_invalid_model_identifier_exists(self):
        model = Model(model_name="Acme Inc")
        model_identifier_1 = ModelIdentifier(model_identifier_value="ABC123", model_identifier_type='URL') 
        model.set_model_identifier(model_identifier_1)
        with self.assertRaises(ValueError) as exc:
            model_identifier_2 = ModelIdentifier(model_identifier_value="DEF456", model_identifier_type='URL') 
            model.set_model_identifier(model_identifier_2)
        self.assertEqual(str(exc.exception), "This model record already has a model identifier allocated")


class TestModelIdentifiers(unittest.TestCase):
    
    def test_missing_model_identifier_value(self):
        """Test that model_identifier_value is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            ModelIdentifier(model_identifier_type='URL') 
        self.assertIn("missing 1 required positional argument", str(exc.exception))

    def test_missing_model_identifier_type(self):
        """Test that model_identifier_type is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            ModelIdentifier(model_identifier_value='XYZ123') 
        self.assertIn("missing 1 required positional argument", str(exc.exception))

    def test_invalid_model_identifier_value(self):
        with self.assertRaises(TypeError) as exc:
            ModelIdentifier(model_identifier_value=123, model_identifier_type='a model identfier type') 
        self.assertEqual(str(exc.exception), "Model Identifier Value must be a string")

    def test_invalid_model_identifier_type(self):
        with self.assertRaises(TypeError) as exc:
            ModelIdentifier(model_identifier_value='XYZ123', model_identifier_type=123) 
        self.assertEqual(str(exc.exception), "Model Identifier Type must be a string")

    def test_model_identifier_type_storage(self):
        """Test that model_identifier_type is correctly stored and retrieved (Bug #1 regression test)"""
        model_identifier = ModelIdentifier(model_identifier_value='ABC123', model_identifier_type='URL')
        self.assertEqual(model_identifier.model_identifier_type, 'URL', 
                        'Model identifier type not correctly stored or retrieved')
        self.assertEqual(model_identifier.model_identifier_value, 'ABC123',
                        'Model identifier value not correctly stored or retrieved')

    def test_invalid_model_identifier_type_not_in_vocab(self):
        """Test that invalid model_identifier_type raises ValueError"""
        with self.assertRaises(ValueError) as exc:
            ModelIdentifier(model_identifier_value='ABC123', model_identifier_type='INVALID_TYPE')
        self.assertEqual(str(exc.exception), "Model Identifier Type not recognised")


class TestRelatedIdentifiers(unittest.TestCase):

    def test_valid_related_identifier(self):
        related_identifier = RelatedIdentifier(related_identifier_value="https://www.pathtopaper.edu.au", related_identifier_type="URL", related_identifier_relation_type="IsDescribedBy", related_identifier_name="Documentation Paper")
        self.assertIsInstance(related_identifier, RelatedIdentifier, 'Something went wrong with related identifier class instantation')

    def test_valid_related_identifier_no_name(self):
        related_identifier = RelatedIdentifier(related_identifier_value="https://www.pathtopaper.edu.au", related_identifier_type="URL", related_identifier_relation_type="IsDescribedBy")
        self.assertIsInstance(related_identifier, RelatedIdentifier, 'Something went wrong with related identifier class instantation')

    def test_missing_value(self):
        """Test that related_identifier_value is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            RelatedIdentifier(related_identifier_type="URL", related_identifier_relation_type="IsDescribedBy")
        self.assertIn("missing 1 required positional argument", str(exc.exception))

    def test_invalid_empty_value(self):
        with self.assertRaises(ValueError) as exc:
            RelatedIdentifier(related_identifier_value="", related_identifier_type="URL", related_identifier_relation_type="IsDescribedBy", related_identifier_name="Documentation Paper")
        self.assertEqual(str(exc.exception), "related_identifier_value cannot be an empty string")

    def test_missing_identifier_type(self):
        """Test that related_identifier_type is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            RelatedIdentifier(related_identifier_value="https://www.pathtopaper.edu.au", related_identifier_relation_type="IsDescribedBy")
        self.assertIn("missing 1 required positional argument", str(exc.exception))

    def test_invalid_identifier_type(self):
        with self.assertRaises(ValueError) as exc:
            RelatedIdentifier(related_identifier_value="https://www.pathtopaper.edu.au", related_identifier_type="ABC", related_identifier_relation_type="IsDescribedBy")
        self.assertEqual(str(exc.exception), "Related Identifier Type not recognised")

    def test_missing_relation_type(self):
        """Test that related_identifier_relation_type is a required parameter"""
        with self.assertRaises(TypeError) as exc:
            RelatedIdentifier(related_identifier_value="https://www.pathtopaper.edu.au", related_identifier_type="URL")
        self.assertIn("missing 1 required positional argument", str(exc.exception))

    def test_invalid_relation_type(self):
        with self.assertRaises(ValueError) as exc:
            RelatedIdentifier(related_identifier_value="https://www.pathtopaper.edu.au", related_identifier_type="URL", related_identifier_relation_type="ABCDEF")
        self.assertEqual(str(exc.exception), "Related Identifier Relation Type not recognised")


class TestValidations(unittest.TestCase):

    def test_valid_pidinst(self):
        # Initialise Instrument
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ", 
        )
        # Identifier
        identifier = Identifier(identifier_value="10.1000/retwebwb", identifier_type="DOI")
        instrument.set_identifier(identifier)
        # Manufacturer
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        manufacturer_identifier = ManufacturerIdentifier(manufacturer_identifier_value="https://www.acme.com", manufacturer_identifier_type='URL') 
        manufacturer.set_manufacturer_identifier(manufacturer_identifier)
        instrument.append_manufacturer(manufacturer)
        # Owner
        owner = Owner(owner_name="Jane Doe", owner_contact="jane.doe@email.com")
        owner_identifier = OwnerIdentifier(owner_identifier_value="0000-ABCD-1234-WXYZ", owner_identifier_type='ORCID') 
        owner.set_owner_identifier(owner_identifier)
        instrument.append_owner(owner)

        self.assertTrue(instrument.is_valid_pidinst, 'Something went wrong with PIDInst validation')

    def test_invalid_pidinst_1(self):
        # Initialise Instrument
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ", 
        )
        # Manufacturer
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        manufacturer_identifier = ManufacturerIdentifier(manufacturer_identifier_value="https://www.acme.com", manufacturer_identifier_type='URL') 
        manufacturer.set_manufacturer_identifier(manufacturer_identifier)
        instrument.append_manufacturer(manufacturer)
        # Owner
        owner = Owner(owner_name="Jane Doe", owner_contact="jane.doe@email.com")
        owner_identifier = OwnerIdentifier(owner_identifier_value="0000-ABCD-1234-WXYZ", owner_identifier_type='ORCID') 
        owner.set_owner_identifier(owner_identifier)
        instrument.append_owner(owner)

        self.assertFalse(instrument.is_valid_pidinst(), 'Something went wrong with PIDInst validation')

    def test_invalid_pidinst_2(self):
        # Initialise Instrument
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ", 
        )
        # Identifier
        identifier = Identifier(identifier_value="10.1000/retwebwb", identifier_type="DOI")
        instrument.set_identifier(identifier)
        # Manufacturer
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        manufacturer_identifier = ManufacturerIdentifier(manufacturer_identifier_value="https://www.acme.com", manufacturer_identifier_type='URL') 
        manufacturer.set_manufacturer_identifier(manufacturer_identifier)
        instrument.append_manufacturer(manufacturer)

        self.assertFalse(instrument.is_valid_pidinst(), 'Something went wrong with PIDInst validation')

    def test_valid_for_doi_all_requirements_met(self):
        """Test that is_valid_for_doi returns True when all requirements are met (Bug #2 regression test)"""
        # Initialise Instrument with all required fields for DOI
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ", 
        )
        # Manufacturer
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        # Owner
        owner = Owner(owner_name="Jane Doe", owner_contact="jane.doe@email.com")
        instrument.append_owner(owner)

        self.assertTrue(instrument.is_valid_for_doi(), 'Valid instrument should be ready for DOI allocation')

    def test_invalid_for_doi_no_manufacturers(self):
        """Test that is_valid_for_doi returns False when manufacturers list is empty (Bug #2 regression test)"""
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ", 
        )
        # Owner but no manufacturer
        owner = Owner(owner_name="Jane Doe", owner_contact="jane.doe@email.com")
        instrument.append_owner(owner)

        self.assertFalse(instrument.is_valid_for_doi(), 'Instrument without manufacturers should not be valid for DOI')

    def test_invalid_for_doi_no_owners(self):
        """Test that is_valid_for_doi returns False when owners list is empty (Bug #2 regression test)"""
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ", 
        )
        # Manufacturer but no owner
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)

        self.assertFalse(instrument.is_valid_for_doi(), 'Instrument without owners should not be valid for DOI')

    def test_invalid_for_doi_no_landing_page(self):
        """Test that is_valid_for_doi returns False when landing_page is None"""
        instrument = Instrument(
            name="Instrument XYZ", 
        )
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        owner = Owner(owner_name="Jane Doe", owner_contact="jane.doe@email.com")
        instrument.append_owner(owner)

        self.assertFalse(instrument.is_valid_for_doi(), 'Instrument without landing_page should not be valid for DOI')

    def test_invalid_for_doi_identifier_exists(self):
        """Test that is_valid_for_doi returns False when identifier already exists"""
        instrument = Instrument(
            landing_page='https://www.landingpage.com', 
            name="Instrument XYZ", 
        )
        manufacturer = Manufacturer(manufacturer_name="Acme Inc")
        instrument.append_manufacturer(manufacturer)
        owner = Owner(owner_name="Jane Doe", owner_contact="jane.doe@email.com")
        instrument.append_owner(owner)
        # Set an identifier
        identifier = Identifier(identifier_value="10.1000/existing", identifier_type="DOI")
        instrument.set_identifier(identifier)

        self.assertFalse(instrument.is_valid_for_doi(), 'Instrument with existing identifier should not be valid for DOI')

    def test_landing_page_localhost_blocked(self):
        """Test that landing_page blocks localhost URLs to prevent SSRF"""
        with self.assertRaises(ValueError) as context:
            PIDInst(landing_page="http://localhost:8080/instrument", name="Test")
        self.assertIn("valid", str(context.exception))

    def test_landing_page_internal_ip_blocked(self):
        """Test that landing_page blocks internal IP addresses"""
        with self.assertRaises(ValueError) as context:
            PIDInst(landing_page="http://192.168.1.1/instrument", name="Test")
        self.assertIn("valid", str(context.exception))

    def test_landing_page_loopback_blocked(self):
        """Test that landing_page blocks loopback IP"""
        with self.assertRaises(ValueError) as context:
            PIDInst(landing_page="http://127.0.0.1/instrument", name="Test")
        self.assertIn("valid", str(context.exception))

    def test_landing_page_invalid_scheme(self):
        """Test that landing_page rejects non-http/https schemes"""
        with self.assertRaises(ValueError) as context:
            PIDInst(landing_page="ftp://example.com/instrument", name="Test")
        self.assertIn("valid", str(context.exception))

    def test_landing_page_malformed_url(self):
        """Test that landing_page rejects malformed URLs"""
        with self.assertRaises(ValueError) as context:
            PIDInst(landing_page="http:malicious.com", name="Test")
        self.assertIn("valid", str(context.exception))

    def test_landing_page_valid_url(self):
        """Test that landing_page accepts valid URLs"""
        instrument = PIDInst(landing_page="https://example.com/instrument", name="Test")
        self.assertEqual(instrument.landing_page, "https://example.com/instrument")

    def test_landing_page_none_allowed(self):
        """Test that landing_page can be None"""
        instrument = PIDInst(name="Test")
        self.assertIsNone(instrument.landing_page)


if __name__ == '__main__':
    unittest.main()

