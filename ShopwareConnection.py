import requests
import json


def authorize_shopware():
    url = f"{CredentialsShopware.url}/oauth/token"

    payload = json.dumps({
        "grant_type": "client_credentials",
        "client_id": CredentialsShopware.client_id,
        "client_secret": CredentialsShopware.client_secret
    })
    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    res = json.loads(response.text)
    CredentialsShopware.bearer = "Bearer " + res["access_token"]


def make_request(kind, postfix_url, payload=None):
    url = CredentialsShopware.url + postfix_url
    headers = {
        'Content-Type': 'application/json',
        'Authorization': CredentialsShopware.bearer}
    return requests.request(kind, url, headers=headers, data=payload, verify=False)


def post_product(details):
    return make_request("POST", "/product", details)


def post_property_group(details):
    return make_request("POST", "/property-group", details)


def post_property_group_option(details):
    return make_request("POST", "/property-group-option", details)


def post_category(details):
    return make_request("POST", "/category", details)


def patch_category(ent_id, details):
    return make_request("PATCH", f"/category/{ent_id}", details)


def post_tax(details):
    return make_request("POST", "/tax", details)


def post_currency(details):
    return make_request("POST", "/currency", details)


def post_media(details):
    return make_request("POST", "/media", details)


class CredentialsShopware:
    url = ""
    client_id = ""
    client_secret = ""
    bearer = ""
