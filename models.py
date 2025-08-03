from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, RootModel
from enum import Enum

# Enums defined separately to avoid Pydantic conflicts
class SectionID(str, Enum):
    SESSION = "Session"
    PRETRADE = "PreTrade"
    TRADE = "Trade"
    POSTTRADE = "PostTrade"
    INFRASTRUCTURE = "Infrastructure"
    OTHER = "Other"

class ComponentType(str, Enum):
    BLOCK = "Block"
    BLOCK_REPEATING = "BlockRepeating"
    IMPLICIT_BLOCK = "ImplicitBlock"
    IMPLICIT_BLOCK_REPEATING = "ImplicitBlockRepeating"
    OPTIMISED_BLOCK_REPEATING = "OptimisedBlockRepeating"
    OPTIMISED_IMPLICIT_BLOCK_REPEATING = "OptimisedImplicitBlockRepeating"
    XML_DATA_BLOCK = "XMLDataBlock"
    MESSAGE = "Message"

class FIXVersion(str, Enum):
    FIX_4_4 = "FIX.4.4"
    FIX_5_0_SP2 = "FIX.5.0SP2"
    FIX_Z = "FIX.Z"

class SearchType(str, Enum):
    MESSAGE = "message"
    COMPONENT = "component" 
    FIELD = "field"
    ENUM = "enum"
    CODESET = "codeset"
    ALL = "all"

# Base models
class BaseEntity(BaseModel):
    added: Optional[str] = None
    updated: Optional[str] = None
    deprecated: Optional[str] = None
    addedEP: Optional[int] = None
    updatedEP: Optional[int] = None
    deprecatedEP: Optional[int] = None

class Field(BaseEntity):
    tag: int
    name: str
    type: str
    abbr_name: Optional[str] = None
    not_req_xml: bool
    description: str
    elaboration: Optional[str] = None
    base_category: Optional[str] = None
    base_category_abbr_name: Optional[str] = None
    union_data_type: Optional[str] = None

class Enum(BaseEntity):
    tag: int
    value: str
    symbolic_name: str
    group: Optional[str] = None
    sort: Optional[int] = None
    description: str
    elaboration: Optional[str] = None

class Component(BaseEntity):
    component_id: int
    component_type: ComponentType
    category_id: str
    name: str
    abbr_name: Optional[str] = None
    not_req_xml: bool
    description: str
    elaboration: Optional[str] = None

class Message(BaseEntity):
    component_id: int
    msg_type: str
    name: str
    category_id: str
    section_id: SectionID
    abbr_name: Optional[str] = None
    not_req_xml: bool
    description: str
    elaboration: Optional[str] = None

class Category(BaseEntity):
    category_id: str
    fixml_filename: str
    not_req_xml: bool
    generate_impl_file: bool
    component_type: str
    section_id: Optional[SectionID] = None
    volume: Optional[str] = None
    include_file: Optional[str] = None
    description: Optional[str] = None

class Section(BaseEntity):
    section_id: SectionID
    name: str
    display_order: int
    volume: str
    not_req_xml: bool
    fixml_filename: Optional[str] = None
    description: Optional[str] = None

class Datatype(BaseEntity):
    name: str
    base_type: Optional[str] = None
    description: str
    example: Optional[List[str]] = None

class Abbreviation(BaseEntity):
    term: str
    abbr_term: str
    description: str

class MsgContent(BaseEntity):
    component_id: int
    tag_text: str
    indent: int
    position: float
    reqd: bool
    inlined: Optional[bool] = None
    description: Optional[str] = None

# Search and response models

class SearchRequest(BaseModel):
    query: str
    search_type: SearchType = SearchType.ALL
    version: FIXVersion = FIXVersion.FIX_5_0_SP2
    match_abbr_only: bool = False
    is_regex: bool = False

class SearchResult(BaseModel):
    type: SearchType
    id: str
    name: str
    abbr_name: Optional[str] = None
    description: str
    tag: Optional[int] = None
    msg_type: Optional[str] = None
    category: Optional[str] = None
    section: Optional[SectionID] = None

class SearchResponse(BaseModel):
    query: str
    version: FIXVersion
    results: List[SearchResult]
    total_count: int

# Detailed response models
class FieldDetail(Field):
    enums: List[Enum] = []
    usage_in_messages: List[str] = []
    usage_in_components: List[str] = []

class MessageDetail(Message):
    contents: List[MsgContent] = []
    fields: List[Field] = []
    components: List[Component] = []

class ComponentDetail(Component):
    contents: List[MsgContent] = []
    fields: List[Field] = []
    nested_components: List[Component] = []
    usage_in_messages: List[str] = []
    usage_in_components: List[str] = []

# Summary models for listing endpoints
class MessageSummary(BaseModel):
    msg_type: str
    name: str
    abbr_name: Optional[str] = None
    component_id: int
    category_id: str
    description: str
    pedigree: str

class ComponentSummary(BaseModel):
    component_id: int
    name: str
    abbr_name: Optional[str] = None
    category_id: str
    component_type: ComponentType
    is_repeating_group: bool
    description: str
    pedigree: str

class FieldSummary(BaseModel):
    tag: int
    name: str
    abbr_name: Optional[str] = None
    datatype: str
    union_datatype: Optional[str] = None
    description: str
    pedigree: str

class CodeSetSummary(BaseModel):
    tag: int
    name: str
    base_datatype: str
    description: str
    pedigree: str

class DatatypeSummary(BaseModel):
    name: str
    base_datatype: Optional[str] = None
    xml_builtin: bool
    xml_base_type: Optional[str] = None
    xml_pattern: Optional[str] = None
    min_value: Optional[int] = None
    description: str
    pedigree: str

# API Error model
class APIError(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

# AG Grid SSRM Models
class ColumnVO(BaseModel):
    """Column Value Object for AG Grid SSRM"""
    id: str
    displayName: Optional[str] = None
    field: Optional[str] = None
    aggFunc: Optional[str] = None

class SortModelItem(BaseModel):
    """Sort model item for AG Grid SSRM"""
    colId: str
    sort: str  # 'asc' or 'desc'

class FilterModel(RootModel[Dict[str, Any]]):
    """Filter model for AG Grid SSRM"""
    root: Dict[str, Any]

class AdvancedFilterModel(RootModel[Dict[str, Any]]):
    """Advanced filter model for AG Grid SSRM"""
    root: Dict[str, Any]

class IServerSideGetRowsRequest(BaseModel):
    """AG Grid Server-Side Row Model request interface"""
    startRow: Optional[int] = None
    endRow: Optional[int] = None
    rowGroupCols: List[ColumnVO] = []
    valueCols: List[ColumnVO] = []
    pivotCols: List[ColumnVO] = []
    pivotMode: bool = False
    groupKeys: List[str] = []
    filterModel: Optional[Union[Dict[str, Any], FilterModel, AdvancedFilterModel]] = None
    sortModel: List[SortModelItem] = []

class LoadSuccessParams(BaseModel):
    """Response parameters for successful SSRM load"""
    rowData: List[Dict[str, Any]]
    rowCount: Optional[int] = None  # Total count for infinite scrolling
    storeInfo: Optional[Dict[str, Any]] = None
