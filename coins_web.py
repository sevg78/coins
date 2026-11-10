"""
Модуль для получения данных по памятным и инвестиционным монетам с сайта cbr.ru
"""
import requests
from bs4 import BeautifulSoup


enumseries = {'name': 'EnumSeries', 'tag': 'SE', 'tag_r': 'Name', 'tag_e': 'EName', 'id': 'Id'}
enumnominals = {'name': 'EnumNominals', 'tag': 'EN', 'tag_r': 'Nominal_Rus', 'tag_e': 'Nominal_Eng', 'id': 'NominalID'}
enummetals = {'name': 'EnumMetals', 'tag': 'EM', 'tag_r': 'Metall_Rus', 'tag_e': 'Metall_Eng', 'id': 'MetallID'}

def getmonetdetailinfo(kn, l_eng='false'):
    """
    Детальная информация по монете 
    Параметры:
        kn - строка, каталожный номер
        l_eng - язык справки, false - русский, true - англ
    """
    res = {}
    url = 'http://www.cbr.ru/CoinsBaseWS/CoinsBaseWS.asmx'
    headers={'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': 'http://web.cbr.ru/GetMonetDetailInfo'}
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <GetMonetDetailInfo xmlns="http://web.cbr.ru/">
                            <CatNumber>{kn}</CatNumber>
                            <Eng>{l_eng}</Eng>
                        </GetMonetDetailInfo>
                    </soap:Body>
                </soap:Envelope>"""
    response = requests.post(url, data=xml, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')
        head = soup.find('xs:sequence')
        for tag in head.findAll('xs:element'):
            if soup.find(tag['name']):
                res[tag['name'].lower()] = soup.find(tag['name']).text.strip()
            else:
                res[tag['name'].lower()] = None
    return res

def req(data, l_eng=False):  
    """
    Справочник номиналов data = enumnominals
    Справочник металлов data = enummetals
    Справочник серий data = enumseries
    """
    rus = {}
    eng = {}
    url = 'http://www.cbr.ru/CoinsBaseWS/CoinsBaseWS.asmx'
    headers={'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': f"http://web.cbr.ru/{data['name']}"}
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                               xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
                    <soap:Body>
                        <{data['name']} xmlns="http://web.cbr.ru/" />
                    </soap:Body>
                </soap:Envelope>"""
    response = requests.post(url, data=xml, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')
        for tag in soup.findAll(data['tag']):
            rus[tag(data['id'])[0].text] = tag(data['tag_r'])[0].text.strip()
            eng[tag(data['id'])[0].text] = tag(data['tag_e'])[0].text.strip()
    if l_eng: 
        return eng
    return rus

def searchcoin(year='0', nominal='-1', metal_id='0', serie_id='0', searchphrase='', is_investment='0'):
    """
    Поиск монет с фильтрацией
    Параметры:
        searchphrase - подстрока, осуществляется поиск по названию или каталожному номеру монет, может быть пустой
        year - год, если все года, то "0"
        nominal - код номинала из справочника номиналов, если не используется, то "-1"
        metal_id - код металла из справочника металлов, если не используется, то "0"
        serie_id - код серии из справочника серий, если не используется, то "0"
        is_investment - признак инвестиционной монеты может быть "1" или "0"
    """
    res = []
    tmp = {}
    url = 'http://www.cbr.ru/CoinsBaseWS/CoinsBaseWS.asmx'
    headers={'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': 'http://web.cbr.ru/SearchMonet'}
    xml_req = f"""<?xml version="1.0" encoding="utf-8"?>
                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                                   xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                                   xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                        <soap:Body>
                            <SearchMonet xmlns="http://web.cbr.ru/">
                                <SearchPhrase>{searchphrase}</SearchPhrase>
                                <year>{year}</year>
                                <nominal>{nominal}</nominal>
                                <metal_id>{metal_id}</metal_id>
                                <serie_id>{serie_id}</serie_id>
                                <is_investment>{is_investment}</is_investment>
                            </SearchMonet>
                        </soap:Body>
                    </soap:Envelope>"""
    response = requests.post(url, data=xml_req, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')
        for tag in soup.findAll('CL'):
            tmp['CatNumber'] = tag('CatNumber')[0].text
            tmp['DT'] = tag('DT')[0].text[:10]
            tmp['cname'] = tag('cname')[0].text.strip()
            tmp['nominal'] = tag('nominal')[0].text
            tmp['metal'] = tag('metal')[0].text
            if tag('sname'):
                tmp['sname'] = tag('sname')[0].text.strip()
            else:
                tmp['sname'] = ''
            res.append(tmp)
            tmp = {}
    return res
