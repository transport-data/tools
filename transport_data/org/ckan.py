from transport_data.util.ckan import Client

#: Development instance of TDC CKAN. Accessible as of 2024-11-27.
DEV = Client("https://ckan.tdc.dev.datopian.com")

#: Production instance of TDC CKAN. Accessible as of 2024-11-27.
PROD = Client("https://ckan.transport-data.org")

#: Staging instance of TDC CKAN. Not accessible as of 2024-11-27; SSL certificate error.
STAGING = Client("https://ckan.tdc.staging.datopian.com")
