import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Union
from models import *
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FIXDictionaryParser:
    def __init__(self, resources_path: str = "resources/dict"):
        self.resources_path = resources_path
        self.data: Dict[FIXVersion, Dict[str, List]] = {}
        self._load_all_versions()
    
    def _load_all_versions(self):
        """Load all available FIX versions"""
        for version in FIXVersion:
            self.data[version] = self._load_version(version.value)
            logger.info(f"Loaded {version.value}")
    
    def _load_version(self, version: str) -> Dict[str, List]:
        """Load a specific FIX version"""
        version_path = os.path.join(self.resources_path, version, "Base")
        
        data = {
            'messages': [],
            'fields': [],
            'components': [],
            'enums': [],
            'categories': [],
            'sections': [],
            'datatypes': [],
            'abbreviations': [],
            'msgcontents': []
        }
        
        try:
            # Load messages
            messages_file = os.path.join(version_path, "Messages.xml")
            if os.path.exists(messages_file):
                data['messages'] = self._parse_messages(messages_file)
            
            # Load fields
            fields_file = os.path.join(version_path, "Fields.xml")
            if os.path.exists(fields_file):
                data['fields'] = self._parse_fields(fields_file)
            
            # Load components
            components_file = os.path.join(version_path, "Components.xml")
            if os.path.exists(components_file):
                data['components'] = self._parse_components(components_file)
            
            # Load enums
            enums_file = os.path.join(version_path, "Enums.xml")
            if os.path.exists(enums_file):
                data['enums'] = self._parse_enums(enums_file)
            
            # Load categories
            categories_file = os.path.join(version_path, "Categories.xml")
            if os.path.exists(categories_file):
                data['categories'] = self._parse_categories(categories_file)
            
            # Load sections
            sections_file = os.path.join(version_path, "Sections.xml")
            if os.path.exists(sections_file):
                data['sections'] = self._parse_sections(sections_file)
            
            # Load datatypes
            datatypes_file = os.path.join(version_path, "Datatypes.xml")
            if os.path.exists(datatypes_file):
                data['datatypes'] = self._parse_datatypes(datatypes_file)
            
            # Load abbreviations
            abbreviations_file = os.path.join(version_path, "Abbreviations.xml")
            if os.path.exists(abbreviations_file):
                data['abbreviations'] = self._parse_abbreviations(abbreviations_file)
            
            # Load message contents
            msgcontents_file = os.path.join(version_path, "MsgContents.xml")
            if os.path.exists(msgcontents_file):
                data['msgcontents'] = self._parse_msgcontents(msgcontents_file)
                
        except Exception as e:
            logger.error(f"Error loading version {version}: {e}")
        
        return data
    
    def _get_text(self, element: ET.Element, tag: str, default: str = "") -> str:
        """Get text content from XML element"""
        child = element.find(tag)
        return child.text if child is not None and child.text else default
    
    def _get_int(self, element: ET.Element, tag: str, default: int = 0) -> int:
        """Get integer content from XML element"""
        text = self._get_text(element, tag)
        try:
            return int(text) if text else default
        except ValueError:
            return default
    
    def _get_float(self, element: ET.Element, tag: str, default: float = 0.0) -> float:
        """Get float content from XML element"""
        text = self._get_text(element, tag)
        try:
            return float(text) if text else default
        except ValueError:
            return default
    
    def _get_bool(self, element: ET.Element, tag: str, default: bool = False) -> bool:
        """Get boolean content from XML element"""
        text = self._get_text(element, tag)
        if text == "1" or text.lower() == "true":
            return True
        elif text == "0" or text.lower() == "false":
            return False
        return default
    
    def _parse_messages(self, file_path: str) -> List[Message]:
        """Parse Messages.xml file"""
        messages = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for msg_elem in root.findall('Message'):
                message = Message(
                    component_id=self._get_int(msg_elem, 'ComponentID'),
                    msg_type=self._get_text(msg_elem, 'MsgType'),
                    name=self._get_text(msg_elem, 'Name'),
                    category_id=self._get_text(msg_elem, 'CategoryID'),
                    section_id=SectionID(self._get_text(msg_elem, 'SectionID', 'Other')),
                    abbr_name=self._get_text(msg_elem, 'AbbrName'),
                    not_req_xml=self._get_bool(msg_elem, 'NotReqXML'),
                    description=self._get_text(msg_elem, 'Description'),
                    elaboration=self._get_text(msg_elem, 'Elaboration'),
                    added=msg_elem.get('added'),
                    updated=msg_elem.get('updated'),
                    deprecated=msg_elem.get('deprecated'),
                    addedEP=int(msg_elem.get('addedEP')) if msg_elem.get('addedEP') else None,
                    updatedEP=int(msg_elem.get('updatedEP')) if msg_elem.get('updatedEP') else None,
                    deprecatedEP=int(msg_elem.get('deprecatedEP')) if msg_elem.get('deprecatedEP') else None
                )
                messages.append(message)
        except Exception as e:
            logger.error(f"Error parsing messages from {file_path}: {e}")
        
        return messages
    
    def _parse_fields(self, file_path: str) -> List[Field]:
        """Parse Fields.xml file"""
        fields = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for field_elem in root.findall('Field'):
                field = Field(
                    tag=self._get_int(field_elem, 'Tag'),
                    name=self._get_text(field_elem, 'Name'),
                    type=self._get_text(field_elem, 'Type'),
                    abbr_name=self._get_text(field_elem, 'AbbrName'),
                    not_req_xml=self._get_bool(field_elem, 'NotReqXML'),
                    description=self._get_text(field_elem, 'Description'),
                    elaboration=self._get_text(field_elem, 'Elaboration'),
                    base_category=self._get_text(field_elem, 'BaseCategory'),
                    base_category_abbr_name=self._get_text(field_elem, 'BaseCategoryAbbrName'),
                    union_data_type=self._get_text(field_elem, 'UnionDataType'),
                    added=field_elem.get('added'),
                    updated=field_elem.get('updated'),
                    deprecated=field_elem.get('deprecated'),
                    addedEP=int(field_elem.get('addedEP')) if field_elem.get('addedEP') else None,
                    updatedEP=int(field_elem.get('updatedEP')) if field_elem.get('updatedEP') else None,
                    deprecatedEP=int(field_elem.get('deprecatedEP')) if field_elem.get('deprecatedEP') else None
                )
                fields.append(field)
        except Exception as e:
            logger.error(f"Error parsing fields from {file_path}: {e}")
        
        return fields
    
    def _parse_components(self, file_path: str) -> List[Component]:
        """Parse Components.xml file"""
        components = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for comp_elem in root.findall('Component'):
                component = Component(
                    component_id=self._get_int(comp_elem, 'ComponentID'),
                    component_type=ComponentType(self._get_text(comp_elem, 'ComponentType', 'Block')),
                    category_id=self._get_text(comp_elem, 'CategoryID'),
                    name=self._get_text(comp_elem, 'Name'),
                    abbr_name=self._get_text(comp_elem, 'AbbrName'),
                    not_req_xml=self._get_bool(comp_elem, 'NotReqXML'),
                    description=self._get_text(comp_elem, 'Description'),
                    elaboration=self._get_text(comp_elem, 'Elaboration'),
                    added=comp_elem.get('added'),
                    updated=comp_elem.get('updated'),
                    deprecated=comp_elem.get('deprecated'),
                    addedEP=int(comp_elem.get('addedEP')) if comp_elem.get('addedEP') else None,
                    updatedEP=int(comp_elem.get('updatedEP')) if comp_elem.get('updatedEP') else None,
                    deprecatedEP=int(comp_elem.get('deprecatedEP')) if comp_elem.get('deprecatedEP') else None
                )
                components.append(component)
        except Exception as e:
            logger.error(f"Error parsing components from {file_path}: {e}")
        
        return components
    
    def _parse_enums(self, file_path: str) -> List[Enum]:
        """Parse Enums.xml file"""
        enums = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for enum_elem in root.findall('Enum'):
                enum = Enum(
                    tag=self._get_int(enum_elem, 'Tag'),
                    value=self._get_text(enum_elem, 'Value'),
                    symbolic_name=self._get_text(enum_elem, 'SymbolicName'),
                    group=self._get_text(enum_elem, 'Group'),
                    sort=self._get_int(enum_elem, 'Sort') if self._get_text(enum_elem, 'Sort') else None,
                    description=self._get_text(enum_elem, 'Description'),
                    elaboration=self._get_text(enum_elem, 'Elaboration'),
                    added=enum_elem.get('added'),
                    updated=enum_elem.get('updated'),
                    deprecated=enum_elem.get('deprecated'),
                    addedEP=int(enum_elem.get('addedEP')) if enum_elem.get('addedEP') else None,
                    updatedEP=int(enum_elem.get('updatedEP')) if enum_elem.get('updatedEP') else None,
                    deprecatedEP=int(enum_elem.get('deprecatedEP')) if enum_elem.get('deprecatedEP') else None
                )
                enums.append(enum)
        except Exception as e:
            logger.error(f"Error parsing enums from {file_path}: {e}")
        
        return enums
    
    def _parse_categories(self, file_path: str) -> List[Category]:
        """Parse Categories.xml file"""
        categories = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for cat_elem in root.findall('Category'):
                category = Category(
                    category_id=self._get_text(cat_elem, 'CategoryID'),
                    fixml_filename=self._get_text(cat_elem, 'FIXMLFileName'),
                    not_req_xml=self._get_bool(cat_elem, 'NotReqXML'),
                    generate_impl_file=self._get_bool(cat_elem, 'GenerateImplFile'),
                    component_type=self._get_text(cat_elem, 'ComponentType'),
                    section_id=SectionID(self._get_text(cat_elem, 'SectionID', 'Other')),
                    volume=self._get_text(cat_elem, 'Volume'),
                    include_file=self._get_text(cat_elem, 'IncludeFile'),
                    description=self._get_text(cat_elem, 'Description'),
                    added=cat_elem.get('added'),
                    updated=cat_elem.get('updated'),
                    deprecated=cat_elem.get('deprecated'),
                    addedEP=int(cat_elem.get('addedEP')) if cat_elem.get('addedEP') else None,
                    updatedEP=int(cat_elem.get('updatedEP')) if cat_elem.get('updatedEP') else None,
                    deprecatedEP=int(cat_elem.get('deprecatedEP')) if cat_elem.get('deprecatedEP') else None
                )
                categories.append(category)
        except Exception as e:
            logger.error(f"Error parsing categories from {file_path}: {e}")
        
        return categories
    
    def _parse_sections(self, file_path: str) -> List[Section]:
        """Parse Sections.xml file"""
        sections = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for sec_elem in root.findall('Section'):
                section = Section(
                    section_id=SectionID(self._get_text(sec_elem, 'SectionID', 'Other')),
                    name=self._get_text(sec_elem, 'Name'),
                    display_order=self._get_int(sec_elem, 'DisplayOrder'),
                    volume=self._get_text(sec_elem, 'Volume'),
                    not_req_xml=self._get_bool(sec_elem, 'NotReqXML'),
                    fixml_filename=self._get_text(sec_elem, 'FIXMLFileName'),
                    description=self._get_text(sec_elem, 'Description'),
                    added=sec_elem.get('added'),
                    updated=sec_elem.get('updated'),
                    deprecated=sec_elem.get('deprecated'),
                    addedEP=int(sec_elem.get('addedEP')) if sec_elem.get('addedEP') else None,
                    updatedEP=int(sec_elem.get('updatedEP')) if sec_elem.get('updatedEP') else None,
                    deprecatedEP=int(sec_elem.get('deprecatedEP')) if sec_elem.get('deprecatedEP') else None
                )
                sections.append(section)
        except Exception as e:
            logger.error(f"Error parsing sections from {file_path}: {e}")
        
        return sections
    
    def _parse_datatypes(self, file_path: str) -> List[Datatype]:
        """Parse Datatypes.xml file"""
        datatypes = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for dt_elem in root.findall('Datatype'):
                # Parse examples
                examples = []
                for ex_elem in dt_elem.findall('Example'):
                    if ex_elem.text:
                        examples.append(ex_elem.text)
                
                datatype = Datatype(
                    name=self._get_text(dt_elem, 'Name'),
                    base_type=self._get_text(dt_elem, 'BaseType'),
                    description=self._get_text(dt_elem, 'Description'),
                    example=examples if examples else None,
                    added=dt_elem.get('added'),
                    updated=dt_elem.get('updated'),
                    deprecated=dt_elem.get('deprecated'),
                    addedEP=int(dt_elem.get('addedEP')) if dt_elem.get('addedEP') else None,
                    updatedEP=int(dt_elem.get('updatedEP')) if dt_elem.get('updatedEP') else None,
                    deprecatedEP=int(dt_elem.get('deprecatedEP')) if dt_elem.get('deprecatedEP') else None
                )
                datatypes.append(datatype)
        except Exception as e:
            logger.error(f"Error parsing datatypes from {file_path}: {e}")
        
        return datatypes
    
    def _parse_abbreviations(self, file_path: str) -> List[Abbreviation]:
        """Parse Abbreviations.xml file"""
        abbreviations = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for abbr_elem in root.findall('Abbreviation'):
                abbreviation = Abbreviation(
                    term=self._get_text(abbr_elem, 'Term'),
                    abbr_term=self._get_text(abbr_elem, 'AbbrTerm'),
                    description=self._get_text(abbr_elem, 'Description'),
                    added=abbr_elem.get('added'),
                    updated=abbr_elem.get('updated'),
                    deprecated=abbr_elem.get('deprecated'),
                    addedEP=int(abbr_elem.get('addedEP')) if abbr_elem.get('addedEP') else None,
                    updatedEP=int(abbr_elem.get('updatedEP')) if abbr_elem.get('updatedEP') else None,
                    deprecatedEP=int(abbr_elem.get('deprecatedEP')) if abbr_elem.get('deprecatedEP') else None
                )
                abbreviations.append(abbreviation)
        except Exception as e:
            logger.error(f"Error parsing abbreviations from {file_path}: {e}")
        
        return abbreviations
    
    def _parse_msgcontents(self, file_path: str) -> List[MsgContent]:
        """Parse MsgContents.xml file"""
        msgcontents = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for mc_elem in root.findall('MsgContent'):
                msgcontent = MsgContent(
                    component_id=self._get_int(mc_elem, 'ComponentID'),
                    tag_text=self._get_text(mc_elem, 'TagText'),
                    indent=self._get_int(mc_elem, 'Indent'),
                    position=self._get_float(mc_elem, 'Position'),
                    reqd=self._get_bool(mc_elem, 'Reqd'),
                    inlined=self._get_bool(mc_elem, 'Inlined') if self._get_text(mc_elem, 'Inlined') else None,
                    description=self._get_text(mc_elem, 'Description'),
                    added=mc_elem.get('added'),
                    updated=mc_elem.get('updated'),
                    deprecated=mc_elem.get('deprecated'),
                    addedEP=int(mc_elem.get('addedEP')) if mc_elem.get('addedEP') else None,
                    updatedEP=int(mc_elem.get('updatedEP')) if mc_elem.get('updatedEP') else None,
                    deprecatedEP=int(mc_elem.get('deprecatedEP')) if mc_elem.get('deprecatedEP') else None
                )
                msgcontents.append(msgcontent)
        except Exception as e:
            logger.error(f"Error parsing msgcontents from {file_path}: {e}")
        
        return msgcontents
    
    # Query methods
    def get_messages(self, version: FIXVersion) -> List[Message]:
        """Get all messages for a version"""
        return self.data.get(version, {}).get('messages', [])
    
    def get_fields(self, version: FIXVersion) -> List[Field]:
        """Get all fields for a version"""
        return self.data.get(version, {}).get('fields', [])
    
    def get_components(self, version: FIXVersion) -> List[Component]:
        """Get all components for a version"""
        return self.data.get(version, {}).get('components', [])
    
    def get_enums(self, version: FIXVersion) -> List[Enum]:
        """Get all enums for a version"""
        return self.data.get(version, {}).get('enums', [])
    
    def get_message_by_type(self, msg_type: str, version: FIXVersion) -> Optional[Message]:
        """Get message by message type"""
        messages = self.get_messages(version)
        for message in messages:
            if message.msg_type == msg_type:
                return message
        return None
    
    def get_field_by_tag(self, tag: int, version: FIXVersion) -> Optional[Field]:
        """Get field by tag number"""
        fields = self.get_fields(version)
        for field in fields:
            if field.tag == tag:
                return field
        return None
    
    def get_field_by_name(self, name: str, version: FIXVersion) -> Optional[Field]:
        """Get field by name"""
        fields = self.get_fields(version)
        for field in fields:
            if field.name.lower() == name.lower():
                return field
        return None
    
    def get_component_by_name(self, name: str, version: FIXVersion) -> Optional[Component]:
        """Get component by name"""
        components = self.get_components(version)
        for component in components:
            if component.name.lower() == name.lower():
                return component
        return None
    
    def get_enums_for_field(self, tag: int, version: FIXVersion) -> List[Enum]:
        """Get all enums for a specific field tag"""
        enums = self.get_enums(version)
        return [enum for enum in enums if enum.tag == tag]
    
    def search(self, query: str, search_type: SearchType, version: FIXVersion, 
              match_abbr_only: bool = False, is_regex: bool = False) -> List[SearchResult]:
        """Search across all entities"""
        results = []
        
        # Prepare search pattern
        if is_regex:
            try:
                pattern = re.compile(query, re.IGNORECASE)
            except re.error:
                pattern = re.compile(re.escape(query), re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(query), re.IGNORECASE)
        
        # Search messages
        if search_type in [SearchType.MESSAGE, SearchType.ALL]:
            messages = self.get_messages(version)
            for message in messages:
                if self._matches_pattern(pattern, message.name, message.description, 
                                       message.abbr_name if match_abbr_only else None):
                    results.append(SearchResult(
                        type=SearchType.MESSAGE,
                        id=str(message.component_id),
                        name=message.name,
                        abbr_name=message.abbr_name,
                        description=message.description,
                        msg_type=message.msg_type,
                        category=message.category_id,
                        section=message.section_id
                    ))
        
        # Search fields
        if search_type in [SearchType.FIELD, SearchType.ALL]:
            fields = self.get_fields(version)
            for field in fields:
                if self._matches_pattern(pattern, field.name, field.description,
                                       field.abbr_name if match_abbr_only else None):
                    results.append(SearchResult(
                        type=SearchType.FIELD,
                        id=str(field.tag),
                        name=field.name,
                        abbr_name=field.abbr_name,
                        description=field.description,
                        tag=field.tag
                    ))
        
        # Search components
        if search_type in [SearchType.COMPONENT, SearchType.ALL]:
            components = self.get_components(version)
            for component in components:
                if self._matches_pattern(pattern, component.name, component.description,
                                       component.abbr_name if match_abbr_only else None):
                    results.append(SearchResult(
                        type=SearchType.COMPONENT,
                        id=str(component.component_id),
                        name=component.name,
                        abbr_name=component.abbr_name,
                        description=component.description,
                        category=component.category_id
                    ))
        
        # Search enums (codes)
        if search_type in [SearchType.ENUM, SearchType.ALL]:
            enums = self.get_enums(version)
            for enum in enums:
                if self._matches_pattern(pattern, enum.symbolic_name, enum.description):
                    field_name = ""
                    field = self.get_field_by_tag(enum.tag, version)
                    if field:
                        field_name = field.name
                    
                    results.append(SearchResult(
                        type=SearchType.ENUM,
                        id=f"{enum.tag}_{enum.value}",
                        name=f"{field_name}({enum.tag}) = {enum.value}",
                        description=enum.description,
                        tag=enum.tag
                    ))
        
        return results[:100]  # Limit results
    
    def _matches_pattern(self, pattern: re.Pattern, name: str, description: str, abbr_name: str = None) -> bool:
        """Check if pattern matches any of the searchable fields"""
        if pattern.search(name or ""):
            return True
        if pattern.search(description or ""):
            return True
        if abbr_name and pattern.search(abbr_name):
            return True
        return False
