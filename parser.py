import os
import xml.etree.ElementTree as ET
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from models import *
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FIXDictionaryParser:
    def __init__(self, resources_path: str = "resources/dict"):
        self.resources_path = resources_path
        self.data: Dict[FIXVersion, Dict[str, pd.DataFrame]] = {}
        self._load_all_versions()
    
    def _load_all_versions(self):
        """Load all available FIX versions"""
        for version in FIXVersion:
            self.data[version] = self._load_version(version.value)
            logger.info(f"Loaded {version.value}")
    
    def _load_version(self, version: str) -> Dict[str, pd.DataFrame]:
        """Load a specific FIX version into DataFrames"""
        version_path = os.path.join(self.resources_path, version, "Base")
        
        data = {
            'messages': pd.DataFrame(),
            'fields': pd.DataFrame(),
            'components': pd.DataFrame(),
            'enums': pd.DataFrame(),
            'categories': pd.DataFrame(),
            'sections': pd.DataFrame(),
            'datatypes': pd.DataFrame(),
            'abbreviations': pd.DataFrame(),
            'msgcontents': pd.DataFrame(),
            'msgform': pd.DataFrame()
        }
        
        try:
            # Load messages
            messages_file = os.path.join(version_path, "Messages.xml")
            if os.path.exists(messages_file):
                data['messages'] = self._parse_messages_to_df(messages_file)
            
            # Load fields
            fields_file = os.path.join(version_path, "Fields.xml")
            if os.path.exists(fields_file):
                data['fields'] = self._parse_fields_to_df(fields_file)
            
            # Load components
            components_file = os.path.join(version_path, "Components.xml")
            if os.path.exists(components_file):
                data['components'] = self._parse_components_to_df(components_file)
            
            # Load enums
            enums_file = os.path.join(version_path, "Enums.xml")
            if os.path.exists(enums_file):
                data['enums'] = self._parse_enums_to_df(enums_file)
            
            # Load categories
            categories_file = os.path.join(version_path, "Categories.xml")
            if os.path.exists(categories_file):
                data['categories'] = self._parse_categories_to_df(categories_file)
            
            # Load sections
            sections_file = os.path.join(version_path, "Sections.xml")
            if os.path.exists(sections_file):
                data['sections'] = self._parse_sections_to_df(sections_file)
            
            # Load datatypes
            datatypes_file = os.path.join(version_path, "Datatypes.xml")
            if os.path.exists(datatypes_file):
                data['datatypes'] = self._parse_datatypes_to_df(datatypes_file)
            
            # Load abbreviations
            abbreviations_file = os.path.join(version_path, "Abbreviations.xml")
            if os.path.exists(abbreviations_file):
                data['abbreviations'] = self._parse_abbreviations_to_df(abbreviations_file)
            
            # Load message contents
            msgcontents_file = os.path.join(version_path, "MsgContents.xml")
            if os.path.exists(msgcontents_file):
                data['msgcontents'] = self._parse_msgcontents_to_df(msgcontents_file)
            
            # Generate msgform by joining msgcontents with fields and components
            data['msgform'] = self._generate_msgform(data)
                
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
    
    def _parse_messages_to_df(self, file_path: str) -> pd.DataFrame:
        """Parse Messages.xml file to DataFrame"""
        data = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for msg_elem in root.findall('Message'):
                row = {
                    'component_id': self._get_int(msg_elem, 'ComponentID'),
                    'msg_type': self._get_text(msg_elem, 'MsgType'),
                    'name': self._get_text(msg_elem, 'Name'),
                    'category_id': self._get_text(msg_elem, 'CategoryID'),
                    'section_id': self._get_text(msg_elem, 'SectionID', 'Other'),
                    'abbr_name': self._get_text(msg_elem, 'AbbrName'),
                    'not_req_xml': self._get_bool(msg_elem, 'NotReqXML'),
                    'description': self._get_text(msg_elem, 'Description'),
                    'elaboration': self._get_text(msg_elem, 'Elaboration'),
                    'added': msg_elem.get('added'),
                    'updated': msg_elem.get('updated'),
                    'deprecated': msg_elem.get('deprecated'),
                    'addedEP': int(msg_elem.get('addedEP')) if msg_elem.get('addedEP') else None,
                    'updatedEP': int(msg_elem.get('updatedEP')) if msg_elem.get('updatedEP') else None,
                    'deprecatedEP': int(msg_elem.get('deprecatedEP')) if msg_elem.get('deprecatedEP') else None
                }
                data.append(row)
        except Exception as e:
            logger.error(f"Error parsing messages from {file_path}: {e}")
        
        return pd.DataFrame(data)
    
    def _parse_fields_to_df(self, file_path: str) -> pd.DataFrame:
        """Parse Fields.xml file to DataFrame"""
        data = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for field_elem in root.findall('Field'):
                row = {
                    'tag': self._get_int(field_elem, 'Tag'),
                    'name': self._get_text(field_elem, 'Name'),
                    'type': self._get_text(field_elem, 'Type'),
                    'abbr_name': self._get_text(field_elem, 'AbbrName'),
                    'not_req_xml': self._get_bool(field_elem, 'NotReqXML'),
                    'description': self._get_text(field_elem, 'Description'),
                    'elaboration': self._get_text(field_elem, 'Elaboration'),
                    'base_category': self._get_text(field_elem, 'BaseCategory'),
                    'base_category_abbr_name': self._get_text(field_elem, 'BaseCategoryAbbrName'),
                    'union_data_type': self._get_text(field_elem, 'UnionDataType'),
                    'added': field_elem.get('added'),
                    'updated': field_elem.get('updated'),
                    'deprecated': field_elem.get('deprecated'),
                    'addedEP': int(field_elem.get('addedEP')) if field_elem.get('addedEP') else None,
                    'updatedEP': int(field_elem.get('updatedEP')) if field_elem.get('updatedEP') else None,
                    'deprecatedEP': int(field_elem.get('deprecatedEP')) if field_elem.get('deprecatedEP') else None
                }
                data.append(row)
        except Exception as e:
            logger.error(f"Error parsing fields from {file_path}: {e}")
        
        return pd.DataFrame(data)
    
    def _parse_components_to_df(self, file_path: str) -> pd.DataFrame:
        """Parse Components.xml file to DataFrame"""
        data = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for comp_elem in root.findall('Component'):
                row = {
                    'component_id': self._get_int(comp_elem, 'ComponentID'),
                    'component_type': self._get_text(comp_elem, 'ComponentType', 'Block'),
                    'category_id': self._get_text(comp_elem, 'CategoryID'),
                    'name': self._get_text(comp_elem, 'Name'),
                    'abbr_name': self._get_text(comp_elem, 'AbbrName'),
                    'not_req_xml': self._get_bool(comp_elem, 'NotReqXML'),
                    'description': self._get_text(comp_elem, 'Description'),
                    'elaboration': self._get_text(comp_elem, 'Elaboration'),
                    'added': comp_elem.get('added'),
                    'updated': comp_elem.get('updated'),
                    'deprecated': comp_elem.get('deprecated'),
                    'addedEP': int(comp_elem.get('addedEP')) if comp_elem.get('addedEP') else None,
                    'updatedEP': int(comp_elem.get('updatedEP')) if comp_elem.get('updatedEP') else None,
                    'deprecatedEP': int(comp_elem.get('deprecatedEP')) if comp_elem.get('deprecatedEP') else None
                }
                data.append(row)
        except Exception as e:
            logger.error(f"Error parsing components from {file_path}: {e}")
        
        return pd.DataFrame(data)
    
    def _parse_enums_to_df(self, file_path: str) -> pd.DataFrame:
        """Parse Enums.xml file to DataFrame"""
        data = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for enum_elem in root.findall('Enum'):
                row = {
                    'tag': self._get_int(enum_elem, 'Tag'),
                    'value': self._get_text(enum_elem, 'Value'),
                    'symbolic_name': self._get_text(enum_elem, 'SymbolicName'),
                    'group': self._get_text(enum_elem, 'Group'),
                    'sort': self._get_int(enum_elem, 'Sort') if self._get_text(enum_elem, 'Sort') else None,
                    'description': self._get_text(enum_elem, 'Description'),
                    'elaboration': self._get_text(enum_elem, 'Elaboration'),
                    'added': enum_elem.get('added'),
                    'updated': enum_elem.get('updated'),
                    'deprecated': enum_elem.get('deprecated'),
                    'addedEP': int(enum_elem.get('addedEP')) if enum_elem.get('addedEP') else None,
                    'updatedEP': int(enum_elem.get('updatedEP')) if enum_elem.get('updatedEP') else None,
                    'deprecatedEP': int(enum_elem.get('deprecatedEP')) if enum_elem.get('deprecatedEP') else None
                }
                data.append(row)
        except Exception as e:
            logger.error(f"Error parsing enums from {file_path}: {e}")
        
        return pd.DataFrame(data)
    
    def _parse_categories_to_df(self, file_path: str) -> pd.DataFrame:
        """Parse Categories.xml file to DataFrame"""
        data = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for cat_elem in root.findall('Category'):
                row = {
                    'category_id': self._get_text(cat_elem, 'CategoryID'),
                    'fixml_filename': self._get_text(cat_elem, 'FIXMLFileName'),
                    'not_req_xml': self._get_bool(cat_elem, 'NotReqXML'),
                    'generate_impl_file': self._get_bool(cat_elem, 'GenerateImplFile'),
                    'component_type': self._get_text(cat_elem, 'ComponentType'),
                    'section_id': self._get_text(cat_elem, 'SectionID', 'Other'),
                    'volume': self._get_text(cat_elem, 'Volume'),
                    'include_file': self._get_text(cat_elem, 'IncludeFile'),
                    'description': self._get_text(cat_elem, 'Description'),
                    'added': cat_elem.get('added'),
                    'updated': cat_elem.get('updated'),
                    'deprecated': cat_elem.get('deprecated'),
                    'addedEP': int(cat_elem.get('addedEP')) if cat_elem.get('addedEP') else None,
                    'updatedEP': int(cat_elem.get('updatedEP')) if cat_elem.get('updatedEP') else None,
                    'deprecatedEP': int(cat_elem.get('deprecatedEP')) if cat_elem.get('deprecatedEP') else None
                }
                data.append(row)
        except Exception as e:
            logger.error(f"Error parsing categories from {file_path}: {e}")
        
        return pd.DataFrame(data)
    
    def _parse_sections_to_df(self, file_path: str) -> pd.DataFrame:
        """Parse Sections.xml file to DataFrame"""
        data = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for sec_elem in root.findall('Section'):
                row = {
                    'section_id': self._get_text(sec_elem, 'SectionID', 'Other'),
                    'name': self._get_text(sec_elem, 'Name'),
                    'display_order': self._get_int(sec_elem, 'DisplayOrder'),
                    'volume': self._get_text(sec_elem, 'Volume'),
                    'not_req_xml': self._get_bool(sec_elem, 'NotReqXML'),
                    'fixml_filename': self._get_text(sec_elem, 'FIXMLFileName'),
                    'description': self._get_text(sec_elem, 'Description'),
                    'added': sec_elem.get('added'),
                    'updated': sec_elem.get('updated'),
                    'deprecated': sec_elem.get('deprecated'),
                    'addedEP': int(sec_elem.get('addedEP')) if sec_elem.get('addedEP') else None,
                    'updatedEP': int(sec_elem.get('updatedEP')) if sec_elem.get('updatedEP') else None,
                    'deprecatedEP': int(sec_elem.get('deprecatedEP')) if sec_elem.get('deprecatedEP') else None
                }
                data.append(row)
        except Exception as e:
            logger.error(f"Error parsing sections from {file_path}: {e}")
        
        return pd.DataFrame(data)
    
    def _parse_datatypes_to_df(self, file_path: str) -> pd.DataFrame:
        """Parse Datatypes.xml file to DataFrame"""
        data = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for dt_elem in root.findall('Datatype'):
                # Parse examples
                examples = []
                for ex_elem in dt_elem.findall('Example'):
                    if ex_elem.text:
                        examples.append(ex_elem.text)
                
                row = {
                    'name': self._get_text(dt_elem, 'Name'),
                    'base_type': self._get_text(dt_elem, 'BaseType'),
                    'description': self._get_text(dt_elem, 'Description'),
                    'example': '|'.join(examples) if examples else None,  # Join examples with |
                    'added': dt_elem.get('added'),
                    'updated': dt_elem.get('updated'),
                    'deprecated': dt_elem.get('deprecated'),
                    'addedEP': int(dt_elem.get('addedEP')) if dt_elem.get('addedEP') else None,
                    'updatedEP': int(dt_elem.get('updatedEP')) if dt_elem.get('updatedEP') else None,
                    'deprecatedEP': int(dt_elem.get('deprecatedEP')) if dt_elem.get('deprecatedEP') else None
                }
                data.append(row)
        except Exception as e:
            logger.error(f"Error parsing datatypes from {file_path}: {e}")
        
        return pd.DataFrame(data)
    
    def _parse_abbreviations_to_df(self, file_path: str) -> pd.DataFrame:
        """Parse Abbreviations.xml file to DataFrame"""
        data = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for abbr_elem in root.findall('Abbreviation'):
                row = {
                    'term': self._get_text(abbr_elem, 'Term'),
                    'abbr_term': self._get_text(abbr_elem, 'AbbrTerm'),
                    'description': self._get_text(abbr_elem, 'Description'),
                    'added': abbr_elem.get('added'),
                    'updated': abbr_elem.get('updated'),
                    'deprecated': abbr_elem.get('deprecated'),
                    'addedEP': int(abbr_elem.get('addedEP')) if abbr_elem.get('addedEP') else None,
                    'updatedEP': int(abbr_elem.get('updatedEP')) if abbr_elem.get('updatedEP') else None,
                    'deprecatedEP': int(abbr_elem.get('deprecatedEP')) if abbr_elem.get('deprecatedEP') else None
                }
                data.append(row)
        except Exception as e:
            logger.error(f"Error parsing abbreviations from {file_path}: {e}")
        
        return pd.DataFrame(data)
    
    def _parse_msgcontents_to_df(self, file_path: str) -> pd.DataFrame:
        """Parse MsgContents.xml file to DataFrame"""
        data = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for mc_elem in root.findall('MsgContent'):
                row = {
                    'component_id': self._get_int(mc_elem, 'ComponentID'),
                    'tag_text': self._get_text(mc_elem, 'TagText'),
                    'indent': self._get_int(mc_elem, 'Indent'),
                    'position': self._get_float(mc_elem, 'Position'),
                    'reqd': self._get_bool(mc_elem, 'Reqd'),
                    'inlined': self._get_bool(mc_elem, 'Inlined') if self._get_text(mc_elem, 'Inlined') else None,
                    'description': self._get_text(mc_elem, 'Description'),
                    'added': mc_elem.get('added'),
                    'updated': mc_elem.get('updated'),
                    'deprecated': mc_elem.get('deprecated'),
                    'addedEP': int(mc_elem.get('addedEP')) if mc_elem.get('addedEP') else None,
                    'updatedEP': int(mc_elem.get('updatedEP')) if mc_elem.get('updatedEP') else None,
                    'deprecatedEP': int(mc_elem.get('deprecatedEP')) if mc_elem.get('deprecatedEP') else None
                }
                data.append(row)
        except Exception as e:
            logger.error(f"Error parsing msgcontents from {file_path}: {e}")
        
        return pd.DataFrame(data)
    
    def _generate_msgform(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Generate msgform by joining msgcontents with fields, components, and messages"""
        msgform_data = []
        
        try:
            msgcontents_df = data.get('msgcontents', pd.DataFrame())
            fields_df = data.get('fields', pd.DataFrame())
            components_df = data.get('components', pd.DataFrame())
            messages_df = data.get('messages', pd.DataFrame())
            
            if msgcontents_df.empty:
                return pd.DataFrame()
            
            for _, mc_row in msgcontents_df.iterrows():
                tag_text = mc_row.get('tag_text', '')
                component_id = mc_row.get('component_id', 0)
                
                # Left join with messages table to get msgType and message name
                msg_type = ''
                component_name = ''
                if not messages_df.empty:
                    message_matches = messages_df[messages_df['component_id'] == component_id]
                    if not message_matches.empty:
                        message_row = message_matches.iloc[0]
                        msg_type = message_row.get('msg_type', '')
                        component_name = message_row.get('name', '')
                
                # Left join with components table to get component name
                if not components_df.empty:
                    comp_matches = components_df[components_df['component_id'] == component_id]
                    if not comp_matches.empty:
                        comp_row = comp_matches.iloc[0]
                        component_name = comp_row.get('name', component_name)
                
                # Try to parse tag_text as integer (field reference)
                try:
                    tag_num = int(tag_text)
                    is_field = True
                except (ValueError, TypeError):
                    tag_num = None
                    is_field = False
                
                if is_field and tag_num is not None:
                    # Join with fields table
                    field_matches = fields_df[fields_df['tag'] == tag_num]
                    if not field_matches.empty:
                        field_row = field_matches.iloc[0]
                        msgform_row = {
                            'component_id': component_id,
                            'tag_text': tag_text,
                            'tag': tag_num,
                            'name': field_row.get('name', ''),
                            'abbr_name': field_row.get('abbr_name', ''),
                            'type': field_row.get('type', ''),
                            'reqd': mc_row.get('reqd', False),
                            'indent': mc_row.get('indent', 0),
                            'position': mc_row.get('position', 0.0),
                            'comments': field_row.get('description', ''),
                            'field_or_component': 'Field',
                            'inlined': mc_row.get('inlined'),
                            'added': field_row.get('added'),
                            'updated': field_row.get('updated'),
                            'deprecated': field_row.get('deprecated'),
                            'msgType': msg_type,
                            'componentName': component_name
                        }
                        msgform_data.append(msgform_row)
                else:
                    # Join with components table by name
                    component_matches = components_df[components_df['name'].str.lower() == tag_text.lower()]
                    if not component_matches.empty:
                        comp_row = component_matches.iloc[0]
                        msgform_row = {
                            'component_id': component_id,
                            'tag_text': tag_text,
                            'tag': None,
                            'name': comp_row.get('name', ''),
                            'abbr_name': comp_row.get('abbr_name', ''),
                            'type': comp_row.get('component_type', ''),
                            'reqd': mc_row.get('reqd', False),
                            'indent': mc_row.get('indent', 0),
                            'position': mc_row.get('position', 0.0),
                            'comments': comp_row.get('description', ''),
                            'field_or_component': 'Component',
                            'inlined': mc_row.get('inlined'),
                            'added': comp_row.get('added'),
                            'updated': comp_row.get('updated'),
                            'deprecated': comp_row.get('deprecated'),
                            'msgType': msg_type,
                            'componentName': component_name
                        }
                        msgform_data.append(msgform_row)
                    else:
                        # Create row for unmatched tag_text (could be a group or unknown reference)
                        msgform_row = {
                            'component_id': component_id,
                            'tag_text': tag_text,
                            'tag': None,
                            'name': tag_text,
                            'abbr_name': '',
                            'type': 'Unknown',
                            'reqd': mc_row.get('reqd', False),
                            'indent': mc_row.get('indent', 0),
                            'position': mc_row.get('position', 0.0),
                            'comments': mc_row.get('description', ''),
                            'field_or_component': 'Unknown',
                            'inlined': mc_row.get('inlined'),
                            'added': None,
                            'updated': None,
                            'deprecated': None,
                            'msgType': msg_type,
                            'componentName': component_name
                        }
                        msgform_data.append(msgform_row)
                        
        except Exception as e:
            logger.error(f"Error generating msgform: {e}")
        
        return pd.DataFrame(msgform_data)
    
    # Query methods with DataFrame operations
    def get_messages(self, version: FIXVersion, limit: int = 100, offset: int = 0, 
                    sort_by: str = 'name', sort_dir: str = 'asc', filters: Dict = None) -> pd.DataFrame:
        """Get messages with pagination, sorting, and filtering"""
        df = self.data.get(version, {}).get('messages', pd.DataFrame())
        
        if df.empty:
            return df
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if field in df.columns and value:
                    if isinstance(value, str):
                        df = df[df[field].str.contains(value, case=False, na=False)]
                    else:
                        df = df[df[field] == value]
        
        # Apply sorting
        if sort_by in df.columns:
            ascending = sort_dir.lower() == 'asc'
            df = df.sort_values(by=sort_by, ascending=ascending)
        
        # Apply pagination
        return df.iloc[offset:offset + limit]
    
    def get_fields(self, version: FIXVersion, limit: int = 100, offset: int = 0, 
                  sort_by: str = 'tag', sort_dir: str = 'asc', filters: Dict = None) -> pd.DataFrame:
        """Get fields with pagination, sorting, and filtering"""
        df = self.data.get(version, {}).get('fields', pd.DataFrame())
        
        if df.empty:
            return df
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if field in df.columns and value:
                    if isinstance(value, str):
                        df = df[df[field].str.contains(value, case=False, na=False)]
                    else:
                        df = df[df[field] == value]
        
        # Apply sorting
        if sort_by in df.columns:
            ascending = sort_dir.lower() == 'asc'
            df = df.sort_values(by=sort_by, ascending=ascending)
        
        # Apply pagination
        return df.iloc[offset:offset + limit]
    
    def get_components(self, version: FIXVersion, limit: int = 100, offset: int = 0, 
                      sort_by: str = 'name', sort_dir: str = 'asc', filters: Dict = None) -> pd.DataFrame:
        """Get components with pagination, sorting, and filtering"""
        df = self.data.get(version, {}).get('components', pd.DataFrame())
        
        if df.empty:
            return df
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if field in df.columns and value:
                    if isinstance(value, str):
                        df = df[df[field].str.contains(value, case=False, na=False)]
                    else:
                        df = df[df[field] == value]
        
        # Apply sorting
        if sort_by in df.columns:
            ascending = sort_dir.lower() == 'asc'
            df = df.sort_values(by=sort_by, ascending=ascending)
        
        # Apply pagination
        return df.iloc[offset:offset + limit]
    
    def get_enums(self, version: FIXVersion, limit: int = 100, offset: int = 0, 
                 sort_by: str = 'tag', sort_dir: str = 'asc', filters: Dict = None) -> pd.DataFrame:
        """Get enums with pagination, sorting, and filtering"""
        df = self.data.get(version, {}).get('enums', pd.DataFrame())
        
        if df.empty:
            return df
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if field in df.columns and value:
                    if isinstance(value, str):
                        df = df[df[field].str.contains(value, case=False, na=False)]
                    else:
                        df = df[df[field] == value]
        
        # Apply sorting
        if sort_by in df.columns:
            ascending = sort_dir.lower() == 'asc'
            df = df.sort_values(by=sort_by, ascending=ascending)
        
        # Apply pagination
        return df.iloc[offset:offset + limit]
    
    def get_msgform(self, version: FIXVersion, limit: int = 100, offset: int = 0, 
                   sort_by: str = 'position', sort_dir: str = 'asc', filters: Dict = None) -> pd.DataFrame:
        """Get msgform (message structure) with pagination, sorting, and filtering"""
        df = self.data.get(version, {}).get('msgform', pd.DataFrame())
        
        if df.empty:
            return df
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if field in df.columns and value:
                    if isinstance(value, str):
                        df = df[df[field].str.contains(value, case=False, na=False)]
                    else:
                        df = df[df[field] == value]
        
        # Apply sorting
        if sort_by in df.columns:
            ascending = sort_dir.lower() == 'asc'
            df = df.sort_values(by=sort_by, ascending=ascending)
        
        # Apply pagination
        return df.iloc[offset:offset + limit]
    
    def get_message_by_type(self, msg_type: str, version: FIXVersion) -> Optional[pd.Series]:
        """Get message by message type"""
        df = self.data.get(version, {}).get('messages', pd.DataFrame())
        if df.empty:
            return None
        
        matches = df[df['msg_type'] == msg_type]
        return matches.iloc[0] if not matches.empty else None
    
    def get_field_by_tag(self, tag: int, version: FIXVersion) -> Optional[pd.Series]:
        """Get field by tag number"""
        df = self.data.get(version, {}).get('fields', pd.DataFrame())
        if df.empty:
            return None
        
        matches = df[df['tag'] == tag]
        return matches.iloc[0] if not matches.empty else None
    
    def get_field_by_name(self, name: str, version: FIXVersion) -> Optional[pd.Series]:
        """Get field by name"""
        df = self.data.get(version, {}).get('fields', pd.DataFrame())
        if df.empty:
            return None
        
        matches = df[df['name'].str.lower() == name.lower()]
        return matches.iloc[0] if not matches.empty else None
    
    def get_component_by_name(self, name: str, version: FIXVersion) -> Optional[pd.Series]:
        """Get component by name"""
        df = self.data.get(version, {}).get('components', pd.DataFrame())
        if df.empty:
            return None
        
        matches = df[df['name'].str.lower() == name.lower()]
        return matches.iloc[0] if not matches.empty else None
    
    def get_enums_for_field(self, tag: int, version: FIXVersion) -> pd.DataFrame:
        """Get all enums for a specific field tag"""
        df = self.data.get(version, {}).get('enums', pd.DataFrame())
        if df.empty:
            return df
        
        return df[df['tag'] == tag]
    
    def get_msgform_for_component(self, component_id: int, version: FIXVersion) -> pd.DataFrame:
        """Get msgform (message structure) for a specific component/message"""
        df = self.data.get(version, {}).get('msgform', pd.DataFrame())
        if df.empty:
            return df
        
        # Filter by component_id and sort by position to maintain message structure order
        result = df[df['component_id'] == component_id].sort_values(by='position')
        return result
    
    def search(self, query: str, search_type: SearchType, version: FIXVersion, 
              match_abbr_only: bool = False, is_regex: bool = False, 
              limit: int = 100, offset: int = 0) -> List[SearchResult]:
        """Search across all entities with pagination"""
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
            df = self.data.get(version, {}).get('messages', pd.DataFrame())
            if not df.empty:
                for _, row in df.iterrows():
                    if self._matches_pattern(pattern, row.get('name', ''), 
                                           row.get('description', ''), 
                                           row.get('abbr_name', '') if match_abbr_only else None):
                        results.append(SearchResult(
                            type=SearchType.MESSAGE,
                            id=str(row.get('component_id', '')),
                            name=row.get('name', ''),
                            abbr_name=row.get('abbr_name', ''),
                            description=row.get('description', ''),
                            msg_type=row.get('msg_type', ''),
                            category=row.get('category_id', ''),
                            section=row.get('section_id', '')
                        ))
        
        # Search fields
        if search_type in [SearchType.FIELD, SearchType.ALL]:
            df = self.data.get(version, {}).get('fields', pd.DataFrame())
            if not df.empty:
                for _, row in df.iterrows():
                    if self._matches_pattern(pattern, row.get('name', ''), 
                                           row.get('description', ''),
                                           row.get('abbr_name', '') if match_abbr_only else None):
                        results.append(SearchResult(
                            type=SearchType.FIELD,
                            id=str(row.get('tag', '')),
                            name=row.get('name', ''),
                            abbr_name=row.get('abbr_name', ''),
                            description=row.get('description', ''),
                            tag=row.get('tag')
                        ))
        
        # Search components
        if search_type in [SearchType.COMPONENT, SearchType.ALL]:
            df = self.data.get(version, {}).get('components', pd.DataFrame())
            if not df.empty:
                for _, row in df.iterrows():
                    if self._matches_pattern(pattern, row.get('name', ''), 
                                           row.get('description', ''),
                                           row.get('abbr_name', '') if match_abbr_only else None):
                        results.append(SearchResult(
                            type=SearchType.COMPONENT,
                            id=str(row.get('component_id', '')),
                            name=row.get('name', ''),
                            abbr_name=row.get('abbr_name', ''),
                            description=row.get('description', ''),
                            category=row.get('category_id', '')
                        ))
        
        # Search enums (codes)
        if search_type in [SearchType.ENUM, SearchType.ALL]:
            enums_df = self.data.get(version, {}).get('enums', pd.DataFrame())
            fields_df = self.data.get(version, {}).get('fields', pd.DataFrame())
            
            if not enums_df.empty:
                for _, row in enums_df.iterrows():
                    if self._matches_pattern(pattern, row.get('symbolic_name', ''), 
                                           row.get('description', '')):
                        field_name = ""
                        if not fields_df.empty:
                            field_matches = fields_df[fields_df['tag'] == row.get('tag')]
                            if not field_matches.empty:
                                field_name = field_matches.iloc[0]['name']
                        
                        results.append(SearchResult(
                            type=SearchType.ENUM,
                            id=f"{row.get('tag', '')}_{row.get('value', '')}",
                            name=f"{field_name}({row.get('tag', '')}) = {row.get('value', '')}",
                            description=row.get('description', ''),
                            tag=row.get('tag')
                        ))
        
        # Apply pagination to results
        start_idx = offset
        end_idx = offset + limit
        return results[start_idx:end_idx]
    
    def _matches_pattern(self, pattern: re.Pattern, name: str, description: str, abbr_name: str = None) -> bool:
        """Check if pattern matches any of the searchable fields"""
        if pattern.search(name or ""):
            return True
        if pattern.search(description or ""):
            return True
        if abbr_name and pattern.search(abbr_name):
            return True
        return False
