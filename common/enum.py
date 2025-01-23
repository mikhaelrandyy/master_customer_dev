from enum import Enum

class CustomerDevTypeEnum(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    PERSON_GROUP = "PERSON_GROUP"

class JenisIdentitasTypeEnum(str, Enum):
    KTP = "KTP"
    KIA = "KIA"
    PASPOR = "PASPOR"

class NationalityEnum(str, Enum):
    WNI = "WNI"
    WNA = "WNA"

class ReligionTypeEnum(str, Enum):
    ISLAM = "ISLAM"
    KRISTEN = "KRISTEN"
    KATOLIK = "KATOLIK"
    HINDU = "HINDU"
    BUDDHA = "BUDDHA"
    KHONGHUCU = "KHONGHUCU"

class GenderTypeEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class MaritalStatusEnum(str, Enum):
    MARRIED = "MARRIED"
    SINGLE = "SINGLE"
    DIVORCED = "DIVORCED"

class TypePersonEnum(str, Enum):
    RUMAH = "RUMAH"
    PERUSAHAAN = "PERUSAHAAN"
    KANTOR = "KANTOR"
    GUDANG = "GUDANG"
    LAINNYA = "LAINNYA"




