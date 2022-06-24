import requests

from requests.auth import HTTPBasicAuth


def make_request(kind, postfix_url, payload=None):
    url = CredentialsBusiness.url + postfix_url
    return requests.request(kind, url, data=payload,
                            auth=HTTPBasicAuth(CredentialsBusiness.username, CredentialsBusiness.password),
                            verify=False)


def get_tax():
    return make_request("GET", f"/companies({CredentialsBusiness.company_id})/vatPostingGroup")


def get_categories():
    return make_request("GET",
                        f"/companies({CredentialsBusiness.company_id})/categories")


def get_currencies():
    return make_request("GET", f"/companies({CredentialsBusiness.company_id})/currency")


def get_attributes_and_values():
    return make_request("GET",
                        f"/companies({CredentialsBusiness.company_id})/attributes?$expand=attributevalues")


def get_webshoplines():
    return make_request("GET",
                        f"/companies({CredentialsBusiness.company_id1})/webshop({CredentialsBusiness.webshop_id1})/webshoplines?$expand=customFields,media,itemattributes,itemCategories,itemFields($expand=vatPostingGroup),webshoplinevariantitems($expand=customFields,media,itemattributes,itemCategories,itemFields($expand=vatPostingGroup))&$top=6")


def get_saleschannelid():
    return make_request("GET",
                        f"/companies({CredentialsBusiness.company_id})/webshop({CredentialsBusiness.webshop_id})/saleschannelid")


class CredentialsBusiness:
    url = ""
    username = ""
    password = ""
    company_id = ""
    webshop_id = ""
    company_id1 = ""
    webshop_id1 = ""
