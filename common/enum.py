from enum import Enum

class CustomerDevEnum(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    PERSON_GROUP = "person group"

class JenisIdentitasEnum(str, Enum):
    KTP = "ktp"
    NIB = "nib"
    KIA = "kia"
    PASPOR = "paspor"

class ReligionEnum(str, Enum):
    ISLAM = "islam"
    KRISTEN = "kristen"
    KATHOLIK ="katholik"
    HINDU = "hindu"
    BUDDHA = "buddha"
    KONGHUCU = "khonghucu"
    UNKNOWN = "-"

class GenderEnum(str, Enum):
    MALE = "laki - laki"
    FEMALE = "perempuan"

class MaritalStatusEnum(str, Enum):
    BELUM_KAWIN = "belum kawin"
    KAWIN = "kawin"
    CERAI_HIDUP = "cerai hidup"
    CERAI_MATI = "cerai mati"
    UNKNOWN = "-"

class AddressEnum(str, Enum):
    HOME = "rumah"
    OFFICE = "kantor"
    COMPANY = "perusahaan"
    WAREHOUSE = "gudang"
    OTHER = "lainnya"
    UNKNOWN = "-"




