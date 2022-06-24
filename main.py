import ShopwareConnection as sc
import BusinessCentralConnection as bcc
import json


# region Importing of the tax data
def import_all_tax_info():
    print("Tax import started!")
    sc.authorize_shopware()
    tax_information = bcc.get_tax().text
    tax_information = json.loads(tax_information)
    for tax in tax_information["value"]:
        payload, name = create_tax_payload(tax)
        sc.post_tax(payload)
        print(f"Tax {name} was imported.")
    print("Tax import done!")


def create_tax_payload(tax):
    tax_id = tax["SystemId"].replace('-', '').lower()
    rate = 0
    if tax["taxrate"].isnumeric():
        rate = int(tax["taxrate"])
    name = tax["Description"]
    payload = json.dumps({
        "type": "tax",
        "id": tax_id,
        "taxRate": rate,
        "name": name
    })
    return payload, name


# endregion

# region Importing of the category data
def import_all_category_info():
    print("Category import started!")
    sc.authorize_shopware()
    category_information = bcc.get_categories().text
    category_information = json.loads(category_information)
    for category in category_information["value"]:
        payload, name, category_id = create_category_payload_basic(category)
        sc.patch_category(category_id, payload)
        print(f"Category {name} was imported.")
        if category["Code"] != category["ParentCategoryCode"]:
            for cat in category_information["value"]:
                if cat["ParentCategoryCode"] == category["Code"]:
                    payload, cat_name, cat_id = create_category_payload_with_parent(cat, category_id)
                    sc.authorize_shopware()
                    sc.patch_category(cat_id, payload)
                    print(f"Category {cat_name} was updated with parent.")
    print("Category import done!")


def create_category_payload_basic(category):
    category_id = category["SystemId"].replace('-', '').lower()
    name = category["Description"]
    payload = json.dumps({
        "id": category_id,
        "type": "page",
        "name": name,
        "cmsPageId": "5f7de46694aa45869188f9e2bc065798"
    })
    return payload, name, category_id


def create_category_payload_with_parent(cat, category_id):
    cat_id = cat["SystemId"].replace('-', '').lower()
    cat_name = cat["Description"]
    payload = json.dumps({
        "id": cat_id,
        "type": "page",
        "name": cat_name,
        "parentId": category_id,
        "afterCategoryId": category_id,
        "cmsPageId": "5f7de46694aa45869188f9e2bc065798"
    })
    return payload, cat_name, cat_id


# endregion

# region Importing of the currency data
def import_all_currency_info():
    print("Currency import started!")
    sc.authorize_shopware()
    currency_information = bcc.get_currencies().text
    currency_information = json.loads(currency_information)
    for currency in currency_information["value"]:
        payload, name = create_currency_payload(currency)
        sc.post_currency(payload)
        print(f"Currency {name} was imported.")
    print("Currency import done!")


def create_currency_payload(currency):
    currency_id = currency["SystemId"].replace('-', '').lower()
    factor = float(currency["CurrencyFactor"])
    symbol = currency["Symbol"]
    iso = currency["ISOCode"]
    short_name = currency["Code"]
    name = currency["Description"]
    decimal_p = int(currency["AmountDecimalPlaces"])
    payload = json.dumps({
        "type": "currency",
        "id": currency_id,
        "factor": factor,
        "symbol": symbol,
        "isoCode": iso,
        "shortName": short_name,
        "name": name,
        "decimalPrecision": decimal_p,
        "itemRounding": {
            "decimals": 2,
            "interval": 0.05,
            "roundForNet": False
        },
        "totalRounding": {
            "decimals": 2,
            "interval": 0.05,
            "roundForNet": False
        }
    })
    return payload, name


# endregion

# region Importing of the attribute data
def import_all_attribute_info():
    print("Attribute import started!")
    sc.authorize_shopware()
    attribute_information = bcc.get_attributes_and_values().text
    attribute_information = json.loads(attribute_information)
    for attribute in attribute_information["value"]:
        payload, name, attribute_id = create_attribute_payload(attribute)
        sc.post_property_group(payload)
        print(f"Attibute {name} was imported.")
        for attribute_value in attribute["attributevalues"]:
            value_payload, value_name = create_attribute_option_payload(attribute_value, attribute_id)
            sc.post_property_group_option(value_payload)
            print(f"Attibute option {value_name} was imported.")
    print("Attribute import done!")


def create_attribute_payload(attribute):
    attribute_id = attribute["SystemId"].replace('-', '').lower()
    name = attribute["Name"]
    payload = json.dumps({
        "type": "property_group",
        "id": attribute_id,
        "name": name,
        "description": "string"
    })
    return payload, name, attribute_id


def create_attribute_option_payload(attribute_value, attribute_id):
    attribute_value_id = attribute_value["SystemId"].replace('-', '').lower()
    value_name = attribute_value["Value"]
    value_payload = json.dumps({
        "type": "property_group_option",
        "id": attribute_value_id,
        "groupId": attribute_id,
        "name": value_name
    })
    return value_payload, value_name


# endregion

# region Importing of the product data
def import_all_product_info():
    print("Product import started!")
    sc.authorize_shopware()
    product_information = bcc.get_webshoplines().text
    product_information = json.loads(product_information)
    saleschannelid = (json.loads(bcc.get_saleschannelid().text))["value"]
    for products in product_information["value"]:
        payload, name, product_id = create_product_payload(products, saleschannelid)
        sc.authorize_shopware()
        sc.post_product(payload)
        print(f"Product {name} imported.")
        if len(products["webshoplinevariantitems"]) > 0:
            for variant in products["webshoplinevariantitems"]:
                payload, var_name = create_product_variant_payload(variant, saleschannelid, products, product_id)
                sc.post_product(payload)
                print(f"Product variant {var_name} imported.")
    print("Product import done!")


def create_product_payload(products, saleschannelid):
    product_id = products["SystemId"].replace('-', '').lower()
    name = products["Description"]
    description = products["Description2"]
    product_no = products["No"]
    currency_id = products["currencyId"].replace('-', '').replace('{', '').replace('}', '').lower()
    gross_price = float(products["UnitGrossPrice"])
    net_price = float(products["UnitPrice"])
    stock = int(products["Inventory"])
    length = float(products["Length"])
    height = float(products["Height"])
    width = float(products["Width"])
    weight = float(products["Weight"])

    # tax
    tax_id = "ebf01d515324eb11bb4b000d3a2b9ce5"
    if len(products["itemFields"]) > 0:
        if len(products["itemFields"][0]["vatPostingGroup"]) > 0:
            tax_id = products["itemFields"][0]["vatPostingGroup"][0]["SystemId"].replace('-', '').lower()

    # properties/attributes
    attributes = products["itemattributes"]
    attribute_list = []
    for attribute in attributes:
        if attribute["AttributeValueid"] != "00000000-0000-0000-0000-000000000000":
            attribute_list.append({"id": attribute["AttributeValueid"].replace('-', '').lower()})

    # categories
    categories = products["itemCategories"]
    category_list = []
    for category in categories:
        if category["Categoryid"] != "00000000-0000-0000-0000-000000000000":
            category_list.append({"id": category["Categoryid"].replace('-', '').lower()})

    # custom fields
    a01, b01, b02, b03, b04 = "", "", "", "", ""
    for custom in products["customFields"]:
        if custom["TextType"] == "A01.01":
            a01 = custom["TextValue"]
        if custom["TextType"] == "B01.01":
            b01 = custom["TextValue"]
        if custom["TextType"] == "B02.01":
            b02 = custom["TextValue"]
        if custom["TextType"] == "B03.01":
            b03 = custom["TextValue"]
        if custom["TextType"] == "B04.01":
            b04 = custom["TextValue"]

    payload = json.dumps({
        "id": product_id,
        "visibilities": [{
            "salesChannelId": saleschannelid,
            "visibility": 1}],
        "name": name,
        "productNumber": product_no,
        "description": description,
        "stock": stock,
        "price": [
            {
                "currencyId": currency_id,
                "gross": gross_price,
                "net": net_price,
                "linked": False
            }
        ],
        "taxId": tax_id,
        "weight": weight,
        "width": width,
        "height": height,
        "length": length,
        "categories": category_list,
        "properties": attribute_list,
        "customFields": {
            "wosoNavit_A01.01.text": a01,
            "wosoNavit_B01.01.text": b01,
            "wosoNavit_B02.01.text": b02,
            "wosoNavit_B03.01.text": b03,
            "wosoNavit_B04.01.text": b04
        }
    })
    return payload, name, product_id


def create_product_variant_payload(variant, saleschannelid, products, product_id):
    variant_product_id = variant["SystemId"].replace('-', '').lower()
    name = variant["Description"]
    description = variant["Description2"]
    product_no = variant["No"]
    currency_id = variant["currencyId"].replace('-', '').replace('{', '').replace('}', '').lower()
    gross_price = float(variant["UnitGrossPrice"])
    net_price = float(variant["UnitPrice"])
    stock = int(variant["Inventory"])
    length = float(variant["Length"])
    height = float(variant["Height"])
    width = float(variant["Width"])
    weight = float(variant["Weight"])

    # properties/attributes
    attributes = products["itemattributes"]
    attribute_list = []
    for attribute in attributes:
        if attribute["AttributeValueid"] != "00000000-0000-0000-0000-000000000000":
            attribute_list.append({"id": attribute["AttributeValueid"].replace('-', '').lower()})

    # media
    media_list = []
    if len(products["media"]) > 0:
        for media in products["media"]:
            media_id = media["SystemId"].replace('-', '').lower()
            media_url = media["MediaLink"]
            media_title = media["MediaType"]
            media_content = json.dumps({
                "id": media_id,
                "title": media_title,
                "url": media_url
            })
            sc.post_media(media_content)
            media_list.append({"mediaId": media["SystemId"].replace('-', '').lower()})

    payload = json.dumps({
        "id": variant_product_id,
        "parentId": product_id,
        "visibilities": [{
            "salesChannelId": saleschannelid,
            "visibility": 1}],
        "name": name,
        "productNumber": product_no,
        "description": description,
        "stock": stock,
        "price": [
            {
                "currencyId": currency_id,
                "gross": gross_price,
                "net": net_price,
                "linked": False
            }
        ],
        "weight": weight,
        "width": width,
        "height": height,
        "length": length,
        "properties": attribute_list
    })
    return payload, name


# endregion

def main():
    print("Import started!")
    print("Importing data from BusinessCentral to Shopware")
    import_all_tax_info()
    import_all_category_info()
    import_all_currency_info()
    import_all_attribute_info()
    import_all_product_info()
    print("Import done!")


if __name__ == "__main__":
    main()
