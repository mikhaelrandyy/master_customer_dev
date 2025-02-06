from ulid import ULID
from sqlmodel import Field, Relationship
from common.enum import CustomerDevTypeEnum, JenisIdentitasTypeEnum, NationalityEnum, ReligionTypeEnum, GenderTypeEnum, MaritalStatusEnum, AddressTypeEnum
from datetime import date
from pydantic import EmailStr
from typing import TYPE_CHECKING

from models.base_model import BaseULIDModel, SQLModel

if TYPE_CHECKING:
    from models import Attachment, HistoryLog

class CustomerDevBase(SQLModel):
    type: CustomerDevTypeEnum | None = Field(nullable=True)
    code: str | None = Field(nullable=True, unique=True)
    first_name: str | None = Field(nullable=True, max_length=40) 
    last_name: str | None = Field(nullable=True, max_length=40) 
    known_as: str | None = Field(nullable=True, max_length=40) 

    business_id_type: JenisIdentitasTypeEnum | None = Field(nullable=False) 
    business_id: str | None = Field(nullable=True) 
    business_establishment_number: str | None = Field(nullable=True)
    business_id_kitas: str | None = Field(nullable=True)
    business_id_creation_date: date | None = Field(nullable=True)
    business_id_valid_until: date | None = Field(nullable=True)

    address: str | None = Field(nullable=True) 
    region: str | None = Field(nullable=True) 
    city: str | None = Field(nullable=True) 
    country: str | None = Field(nullable=True) 
    sub_district: str | None = Field(nullable=True)  
    district: str | None = Field(nullable=True)
    postal_code : str | None = Field(nullable=True, max_length=5) 

    nationality: NationalityEnum | None = Field(nullable=True)
    nationality_country: str | None = Field(nullable=True)
    date_of_birth: date | None = Field(nullable=True) 
    place_of_birth: str | None = Field(nullable=True) 

    religion: ReligionTypeEnum | None = Field(nullable=True) 
    gender: GenderTypeEnum | None = Field(nullable=True) 
    marital_status: MaritalStatusEnum | None = Field(nullable=True) 

    npwp_name: str | None = Field(nullable=True)
    npwp_address: str | None = Field(nullable=True)
    npwp: str | None = Field(nullable=False)
    nitku: str | None = Field(nullable=False)

    handphone_number: str | None = Field(nullable=True, max_length=15) 
    handphone_number_secondary: str | None = Field(nullable=True,  max_length=15)
    phone_number: str | None = Field(nullable=True) 
    email: EmailStr | None = Field(nullable=True) 

    mailing_address_type: AddressTypeEnum | None = Field(nullable=True)
    mailing_other_type: str | None = Field(nullable=True)
    mailing_address: str | None = Field(nullable=True)
    mailing_sub_district: str | None = Field(nullable=True)
    mailing_district: str | None = Field(nullable=True)
    mailing_city: str | None = Field(nullable=True)
    mailing_region: str | None = Field(nullable=True)
    mailing_country: str | None = Field(nullable=True)
    mailing_postal_code: str | None = Field(nullable=True)

    lastest_source_from: str | None = Field(nullable=True) #TERAHKIR DI UPDATE 

class CustomerDevFullBase(CustomerDevBase, BaseULIDModel):
    pass


class CustomerDev(CustomerDevFullBase, table=True):
    attachments: list["Attachment"] = Relationship(
        back_populates="customer_dev",
        sa_relationship_kwargs = {
            "lazy": "select"
        }
    )