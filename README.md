# PyPIDInst

A Python 3 library for working with the [PIDInst 1.0 Schema](https://doi.org/10.15497/RDA00070) for documentation and registration of research instruments. This library provides a simple interface for creating instrument metadata records compliant with the PIDInst standard and minting DOIs via DataCite.

## Features

- **PIDInst Schema Compliance**: Create metadata records following the PIDInst 1.0 standard
- **Validation**: Built-in validation for required fields and data formats
- **DOI Minting**: Direct integration with DataCite API for DOI allocation
- **Type Safety**: Strong typing and validation for all metadata fields
- **Security**: URL validation, timeout handling, and comprehensive error checking

## Installation

```bash
pip install git+https://github.com/gerrydevine/pypidinst.git
```

## Requirements

- Python 3.x
- `requests` library
- `python-dotenv` library (for credential management)

## Quick Start

```python
from pypidinst.instrument import Instrument, Owner, Manufacturer

# Create a new instrument
instrument = Instrument(
    name="High-Resolution Mass Spectrometer",
    landing_page="https://example.com/instruments/hrms-001"
)

# Add owner information
owner = Owner(
    owner_name="Dr. Jane Smith",
    owner_contact="jane.smith@example.com"
)
instrument.append_owner(owner)

# Add manufacturer information
manufacturer = Manufacturer(
    manufacturer_name="Scientific Instruments Inc.",
    manufacturer_identifier="https://ror.org/example123"
)
instrument.append_manufacturer(manufacturer)

# Check if ready for DOI allocation
if instrument.is_valid_for_doi():
    print("Instrument is ready for DOI minting!")
```

## Core Concepts

### PIDInst and Instrument Classes

- **`PIDInst`**: Base class representing the core PIDInst schema metadata
- **`Instrument`**: Extends PIDInst with DOI allocation capabilities

### Required Fields for DOI Minting

To mint a DOI, an instrument must have:
- A valid landing page (http/https URL)
- A name
- At least one owner
- At least one manufacturer
- No existing identifier

### Metadata Components

The library provides classes for all PIDInst metadata elements:
- `Identifier`: Persistent identifiers (DOI, ARK, URN, etc.)
- `Owner`: Contact information for instrument owners
- `Manufacturer`: Instrument manufacturer details
- `Model`: Instrument model information
- `RelatedIdentifier`: Links to related resources

## Basic Examples

### Creating an Instrument with Full Metadata

```python
from pypidinst.instrument import (
    Instrument, Identifier, Owner, OwnerIdentifier,
    Manufacturer, ManufacturerIdentifier, Model, ModelIdentifier,
    RelatedIdentifier
)

# Create instrument
instrument = Instrument(
    name="Electron Microscope EM-2000",
    landing_page="https://research.example.edu/instruments/em2000",
    description="High-resolution transmission electron microscope for materials science"
)

# Add owner with identifier
owner = Owner(
    owner_name="Materials Science Lab",
    owner_contact="materials.lab@example.edu"
)
owner_id = OwnerIdentifier(
    owner_identifier_value="https://ror.org/012345678",
    owner_identifier_type="ROR"
)
owner.set_owner_identifier(owner_id)
instrument.append_owner(owner)

# Add manufacturer with identifier
manufacturer = Manufacturer(
    manufacturer_name="ElectronTech Corp"
)
mfr_id = ManufacturerIdentifier(
    manufacturer_identifier_value="https://ror.org/987654321",
    manufacturer_identifier_type="ROR"
)
manufacturer.set_manufacturer_identifier(mfr_id)
instrument.append_manufacturer(manufacturer)

# Add model information
model = Model(model_name="EM-2000 Series")
model_id = ModelIdentifier(
    model_identifier_value="https://electrontech.com/models/em2000",
    model_identifier_type="URL"
)
model.set_model_identifier(model_id)
instrument.set_model(model)

# Add related identifiers (e.g., publications, documentation)
related = RelatedIdentifier(
    related_identifier_value="10.1234/related.publication",
    related_identifier_type="DOI",
    relation_type="IsDescribedBy"
)
instrument.append_related_identifier(related)

# Validate before proceeding
if instrument.is_valid_pidinst():
    print("✓ Instrument metadata is valid")
```

### Working with Identifiers

```python
from pypidinst.instrument import Instrument, Identifier

# Create instrument
instrument = Instrument(
    name="Spectrometer X-100",
    landing_page="https://example.com/instruments/x100"
)

# Set an existing identifier (e.g., if instrument already has a DOI)
identifier = Identifier(
    identifier_value="10.5061/example.instrument.1",
    identifier_type="DOI"
)
instrument.set_identifier(identifier)

# Check identifier
if instrument.get_identifier():
    print(f"Instrument ID: {instrument.get_identifier().identifier_value}")
```

### Validation

```python
# Check if instrument has complete PIDInst metadata
if instrument.is_valid_pidinst():
    print("Valid PIDInst record")

# Check if instrument is ready for DOI minting
if instrument.is_valid_for_doi():
    print("Ready to mint DOI")
else:
    print("Missing required fields for DOI minting")
```

## Advanced Examples: Minting DOIs with DataCite

### Prerequisites for DOI Minting

1. **DataCite Account**: You need a DataCite account with DOI minting privileges
2. **Configuration**: Update `pypidinst/config.py`:
   ```python
   DATACITE_URL = 'https://api.datacite.org/dois'  # or test: https://api.test.datacite.org/dois
   DOI_PREFIX = '10.YOUR_PREFIX'  # Your DataCite DOI prefix
   ```
3. **Credentials**: Create a `.env` file in your project root:
   ```env
   DATACITE_USERNAME=your_datacite_repository_id
   DATACITE_PASSWORD=your_datacite_password
   ```

### Example 1: Basic DOI Minting

```python
from pypidinst.instrument import Instrument, Owner, Manufacturer

# Create instrument with required metadata
instrument = Instrument(
    name="Atomic Force Microscope AFM-500",
    landing_page="https://lab.example.edu/instruments/afm500",
    description="High-precision atomic force microscope for nanoscale imaging"
)

# Add owner
owner = Owner(
    owner_name="Nanotechnology Research Center",
    owner_contact="nanotech@example.edu"
)
instrument.append_owner(owner)

# Add manufacturer
manufacturer = Manufacturer(
    manufacturer_name="NanoInstruments Ltd"
)
instrument.append_manufacturer(manufacturer)

# Validate before minting
if not instrument.is_valid_for_doi():
    raise ValueError("Instrument is not ready for DOI allocation")

# Mint DOI
try:
    instrument.allocate_doi()
    doi = instrument.get_identifier()
    print(f"✓ DOI minted successfully: {doi.identifier_value}")
    print(f"  Landing page: {instrument.landing_page}")
except ValueError as e:
    print(f"✗ DOI minting failed: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
```

### Example 2: Complete Workflow with Full Metadata

```python
from pypidinst.instrument import (
    Instrument, Owner, OwnerIdentifier,
    Manufacturer, ManufacturerIdentifier,
    Model, ModelIdentifier,
    RelatedIdentifier
)

# Create instrument with comprehensive metadata
instrument = Instrument(
    name="Liquid Chromatography-Mass Spectrometry System",
    landing_page="https://chemistry.example.edu/instruments/lcms-2024",
    description="Advanced LC-MS system for proteomics and metabolomics research"
)

# Add multiple owners
owner1 = Owner(
    owner_name="Prof. Alice Johnson",
    owner_contact="alice.johnson@example.edu"
)
owner1_id = OwnerIdentifier(
    owner_identifier_value="0000-0001-2345-6789",
    owner_identifier_type="ORCID"
)
owner1.set_owner_identifier(owner1_id)
instrument.append_owner(owner1)

owner2 = Owner(
    owner_name="Chemistry Department",
    owner_contact="chem.dept@example.edu"
)
instrument.append_owner(owner2)

# Add manufacturer with ROR identifier
manufacturer = Manufacturer(
    manufacturer_name="Analytical Systems International"
)
mfr_id = ManufacturerIdentifier(
    manufacturer_identifier_value="https://ror.org/03yrm5c26",
    manufacturer_identifier_type="ROR"
)
manufacturer.set_manufacturer_identifier(mfr_id)
instrument.append_manufacturer(manufacturer)

# Add model information
model = Model(
    model_name="LC-MS Pro 3000",
    description="Triple quadrupole mass spectrometer with UHPLC"
)
model_id = ModelIdentifier(
    model_identifier_value="https://analyticalsystems.com/products/lcms-pro-3000",
    model_identifier_type="URL"
)
model.set_model_identifier(model_id)
instrument.set_model(model)

# Add related identifiers
# Link to user manual
manual = RelatedIdentifier(
    related_identifier_value="10.5281/zenodo.1234567",
    related_identifier_type="DOI",
    relation_type="IsDocumentedBy"
)
instrument.append_related_identifier(manual)

# Link to calibration data
calibration = RelatedIdentifier(
    related_identifier_value="https://data.example.edu/calibration/lcms-2024",
    related_identifier_type="URL",
    relation_type="IsSupplementedBy"
)
instrument.append_related_identifier(calibration)

# Validate metadata
print("Validating instrument metadata...")
if not instrument.is_valid_pidinst():
    print("✗ Warning: Instrument metadata may be incomplete")

if not instrument.is_valid_for_doi():
    print("✗ Error: Instrument is not ready for DOI minting")
    print("  Required: name, landing_page, at least one owner and manufacturer")
    exit(1)

print("✓ Validation passed")

# Mint DOI
print("\nMinting DOI via DataCite...")
try:
    instrument.allocate_doi()
    doi = instrument.get_identifier()
    
    print("\n✓ Success! DOI has been minted:")
    print(f"  DOI: {doi.identifier_value}")
    print(f"  Type: {doi.identifier_type}")
    print(f"  Landing Page: {instrument.landing_page}")
    print(f"\n  View at: https://doi.org/{doi.identifier_value}")
    
except ValueError as e:
    print(f"\n✗ DOI minting failed: {e}")
    print("  Check your DataCite credentials and configuration")
except ConnectionError as e:
    print(f"\n✗ Network error: {e}")
    print("  Check your internet connection and DataCite API availability")
except Exception as e:
    print(f"\n✗ Unexpected error: {e}")
```

## Identifier Types

### Supported Instrument Identifier Types
- `DOI` - Digital Object Identifier
- `ARK` - Archival Resource Key
- `URN` - Uniform Resource Name
- `RRID` - Research Resource Identifier
- `URL` - Uniform Resource Locator

### Supported Owner/Manufacturer Identifier Types
- `ORCID` - Open Researcher and Contributor ID
- `ROR` - Research Organization Registry
- `GRID` - Global Research Identifier Database
- `ISNI` - International Standard Name Identifier

### Supported Model Identifier Types
- `URL` - Uniform Resource Locator

### Related Identifier Relation Types
- `IsDescribedBy` - The resource is described by the related resource
- `IsNewVersionOf` - The resource is a new version of the related resource
- `IsPreviousVersionOf` - The resource is a previous version of the related resource
- `IsPartOf` - The resource is a part of the related resource
- `HasPart` - The resource has the related resource as a part
- `IsReferencedBy` - The resource is referenced by the related resource
- `References` - The resource references the related resource
- `IsDocumentedBy` - The resource is documented by the related resource
- `Documents` - The resource documents the related resource
- `IsCompiledBy` - The resource is compiled by the related resource
- `Compiles` - The resource compiles the related resource
- `IsVariantFormOf` - The resource is a variant form of the related resource
- `IsOriginalFormOf` - The resource is the original form of the related resource
- `IsIdenticalTo` - The resource is identical to the related resource
- `IsAlternateIdentifier` - The resource is an alternate identifier for the related resource
- `IsSupplementedBy` - The resource is supplemented by the related resource
- `IsSupplementTo` - The resource is a supplement to the related resource

## Error Handling

The library raises specific exceptions for various error conditions:

```python
try:
    instrument = Instrument(
        name="Test Instrument",
        landing_page="invalid-url"  # Will raise ValueError
    )
except ValueError as e:
    print(f"Validation error: {e}")
except TypeError as e:
    print(f"Type error: {e}")
```

Common exceptions:
- `ValueError`: Invalid field values (e.g., invalid URLs, empty required fields)
- `TypeError`: Incorrect data types
- `ConnectionError`: Network issues when contacting DataCite API

## Security Features

- **URL Validation**: Landing pages are validated to prevent SSRF attacks (blocks localhost, private IPs)
- **HTTP Timeouts**: All API requests have 30-second timeouts
- **Response Validation**: DataCite responses are thoroughly validated before processing
- **Input Validation**: All metadata fields are validated for type and format

## Testing

Run the test suite:

```bash
python pypidinst/tests.py
```

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting pull requests.

## License

See LICENSE.txt for details.

## References

- [PIDInst Schema v1.0](https://doi.org/10.15497/RDA00070)
- [DataCite API Documentation](https://support.datacite.org/docs/api)
- [DataCite Metadata Schema](https://schema.datacite.org/)

## Support

For issues and questions, please use the GitHub issue tracker.
