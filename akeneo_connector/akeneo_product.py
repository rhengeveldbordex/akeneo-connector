from typing import TypedDict, Optional

from akeneo_connector.akeneo_connector import AkeneoConnector

class Value(TypedDict):
     locale: Optional[str]
     scope: Optional[str]
     data: str

class AkeneoProduct:
    """
    A class to represent an Akeneo product.

    Attributes:
        uuid (str): The UUID of the product.
        identifier (str): The identifier of the product.
        enabled (bool): The enabled status of the product.
        family (str): The family of the product.
        categories (list): The categories of the product.
        groups (list): The groups of the product.
        parent (str): The parent of the product.
        values (dict): The values of the product.
        updated_values (dict): The updated values of the product.
        created (str): The created date of the product.
        updated (str): The updated date of the product.
        associations (dict): The associations of the product.
        quantified_associations (dict): The quantified associations of the product.
        metadata (dict): The metadata of the product.
        connector (AkeneoConnector): The Akeneo connector to use.

    """

    # Constants
    PRODUCT_URL = 'https://bordex.cloud.akeneo.com/api/rest/{version}/products/{identifier}'

    def __init__(self, data: dict = {}, connector: AkeneoConnector = AkeneoConnector()):
        # Initialize the AkeneoProduct classs
        self.set(data)

        self.connector = connector

    def set(self, data: dict):
        """
        Sets the data of the product.

        Args:
            data (dict): The data of the product.
        """
        self.uuid = data.get('uuid')
        self.identifier = data.get('identifier')
        self.enabled = data.get('enabled')
        self.family = data.get('family')
        self.categories = data.get('categories')
        self.groups = data.get('groups')
        self.parent = data.get('parent')
        self.values = data.get('values')
        self.updated_values = {}
        self.created = data.get('created')
        self.updated = data.get('updated')
        self.associations = data.get('associations')
        self.quantified_associations = data.get('quantified_associations')
        self.metadata = data.get('metadata')
    
    def payload(self):
        """Returns a dictionary representation of the product.

        Returns:
            dict: A dictionary representation of the product.
        """
        return {
            'uuid': self.uuid,
            'identifier': self.identifier,
            'values': self.updated_values,
        }
    
    def get_scopes(self, attribute: str) -> list[str]:
        """
        Gets the scopes for the given attribute.

        Args:
            attribute (str): The attribute to get the scopes for.

        Returns:
            list: The scopes of the attribute.
        """
        scopes = []
        for value in self.values.get(attribute, []):
            scope = value.get('scope')
            if scope not in scopes:
                scopes.append(scope)
        return scopes
    
    def get_locales(self, attribute: str) -> list[str]:
        """
        Gets the locales for the given attribute.

        Args:
            attribute (str): The attribute to get the locales for.

        Returns:
            list: The locales of the attribute.
        """
        locales = []
        for value in self.values.get(attribute, []):
            locale = value.get('locale')
            if locale not in locales:
                locales.append(locale)
        return locales
    
    def get_values(self, attribute: str) -> list[Value]:
        """
        Gets the values for the given attribute.

        Args:
            attribute (str): The attribute to get the values for.

        Returns:
            list: The values of the attribute.
        """
        return self.values.get(attribute, [])
    
    def get_value(self, attribute: str, locale: str | None = None, scope: str | None = None) -> Value:
        """
        Gets the value for the given attribute.

        Args:
            attribute (str): The attribute to get the value for.
            locale (str): The locale of the value.
            scope (str): The scope of the value.

        Returns:
            str: The value of the attribute.
        """
        # Failsafe
        if attribute not in self.values:
            return None

        # Try to find the value with locale and scope
        for value in self.values[attribute]:
            if value.get('locale') == locale and value.get('scope') == scope:
                return value.get('data')

        # Return the first value if locale and scope are not found
        return self.values[attribute][0].get('data')
    

    def set_value(self, attribute: str, locale: str | None = None, scope: str | None = None, data: str | None = None):
        """
        Sets a value for the given attribute.

        Args:
            attribute (str): The attribute to set the value for.
            locale (str): The locale of the value.
            scope (str): The scope of the value.
            data (str): The data of the value.

        Returns:
            None
        """
        # Failsafes
        if data is None:
            return
        
        if attribute not in self.values:
            self.values[attribute] = []

        if attribute not in self.updated_values:
            self.updated_values[attribute] = self.values[attribute]

        # Try to find the index of the value existing with locale and scope
        index = None
        for i, value in enumerate(self.updated_values[attribute]):
            if value.get('locale') == locale and value.get('scope') == scope:
                index = i
                break

        # Update the value if it exists
        if index is not None:
            self.updated_values[attribute][index]['data'] = data
        else:
            self.updated_values[attribute].append({
                'locale': locale,
                'scope': scope,
                'data': data
            })

    def get(self, identifier: str | None = None):
        """
        Retrieves the product data.

        Args:
            identifier (str): The identifier of the product.

        Returns:
            AkeneoProduct: The product with data. None if not found. 
        """
        # Use the identifier if provided
        if identifier is None:
            identifier = self.identifier

        # Failsafe
        if identifier is None:
            return None
        
        # Build the URL
        url = self.connector.product_url.format(identifier=identifier)

        # Get the product
        data = self.connector.get(url)

        # Return the product if found
        if data is not None:
            # Set the data
            self.set(data)

            # Return the product
            return self
        
        return None

    def update(self):
        """
        Updates the product.

        Returns:
            bool: True if successful, False otherwise.
        """
        # Build the URL
        url = self.connector.product_url.format(identifier=self.identifier)

        # Update the product
        self.connector.update(url, self.payload())

        return True

    