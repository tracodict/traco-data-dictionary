# Rest service for data dictionary based on FIX variants

## XML based dictionary

#file:schema  contains XML schema for FIX protocol's data.

#file:FIX.4.4 contains FIX version 4.4 protocol data conforming with above schema.

#file:FIX.5.0SP2 contains FIX version 5.0 SP2 protocol data conforming with above schema.

## Python based Vercel Deployment

The service should be implemented using Python and be able to be deployed to Vercel.

### Dictionary Load

The service provide an API to load multiple versions' FIX data dictionary from #file:dict and by default load the dictionaries during startup.

### API doc

Swagger UI is built in.

## Fiximate alike service

The service provide query HTTP APIs to mimic FIximate funtionalities:

FIXimatesm User Guide

FIXimate is an interactive Web browser based reference for the FIX Specification. FIXimate has been generated from the FIX Orchestra Repository. This section provides a user guide for the various features and capabilities of FIXimate.

Screen setup
The screen is split into three areas as follows:

The left-hand side provides general links and the possibility to select content to be displayed on the right-hand side.
The upper pane on the right-hand side provides search results as well as message and component layouts.
The lower pane on the right-hand side provides detailed information related to a single field.
The size of the upper and lower pane on the right-hand side can be manually adjusted, depending on the content one wishes to see without having to use scrolling.
The upper set of links on the left-hand side offers this user guide, a disclaimer, release notes, the download of FIXimate for offline usage, and allows to switch to the display of FIX legacy versions. The latter shows the scope of the FIX Repository at the time of the release of previous FIX versions all the way back to FIX 4.0. It offers a link to switch back to FIX Latest in the same area of the screen.

Selecting content for display
The second section on the left-hand side of the screen offers a number of search boxes to select data for display on the upper or lower pane on the right hand-side as follows:

Find all: entry of an arbitrary string (case-insensitive) or regular expression (see details below) to search for messages, components, fields, code sets, and codes with that string in their name and/or description (synopsis only, not the elaboration).

If the checkbox "Match abbreviated name only" is activated, the search pattern will be used to find abbreviations and these will be displayed together with the corresponding message, component or field name. Code sets and codes do not have an abbreviated name.
Message type: entry of a value of MsgType(35) for a single FIX message.
Component: selection of a name for a single FIX component
Field tag: entry of a tag number for a single FIX field
Field name: selection of a name for a single FIX field
Code set: selection of a name for a single FIX code set
Using regular expressions to search the repository
Regular expressions are extremely powerful and may be used inside the "Find all:" search box. Especially the characters ^ (element must start with this string), $ (element must end with this string), and . (element can have any character at this position) are very useful and shown as a hint beneath the search box. Character ranges (e.g. "[0-9]" or "[A-Z]") and repetitions (e.g. "{3}") are also supported. Special characters like brackets (e.g. "(") need to be escaped with a backslash character ("\"). Please see here for further detail.

Note that FIXimate does not support case sensitivity in regular expressions.

Examples:

Nested.PartyID$ finds components Nested2PartyID, Nested3PartyID, and Nested4PartyID but not fields like Nested2PartyIDSource due to the "$" at the end of the pattern.
"^Nested.*" finds all components and fields starting with "Nested", e.g. "NestedPartyID(524), and "Nested.*" also finds NoNestedXXX fields, e.g. NoNestedPartyIDs(539).
^R$ or "^r$" (activate checkbox for abbreviated names) finds all party role fields, e.g. PartyRole(452), as their abbreviated name is simply "R".
"^[1-4]" finds all elements that start with a character between "1" and "4". This will result in a list of code names (aka field values) that begin with a number. Names of messages, components, fields, and code sets do not begin with a number in FIX.
"\([0-9]{4}\)" finds all elements that contain 4 consecutive digits enclosed in round brackets. This will result in field descriptions and code names that reference FIX fields with 4-digit tag numbers.
The third section on the left-hand side offers a number of predefined lists for display on the upper pane on the right hand-side as follows:

Message Summary: list of FIX messages sorted by either category (e.g. Market Data), name or message type (MsgType(35) value). The following details are provided for each message:
MsgType(35) value
Message name
Abbreviated name (e.g. for FIXML)
Repository identifier (unique across all messages)
Category
Description (synopsis only, no elaboration)
Pedigree
Components: list of FIX components sorted by either category (e.g. Market Data) or name (repeating groups are explicitly identified in the list). The following details are provided for each component:
Component name
Abbreviated name (e.g. for FIXML)
Repository identifier (unique across all components, repeating or not)
Category
Repeating group indicator (Y/N)
Description (synopsis only, no elaboration)
Pedigree
Fields: list of FIX fields sorted by either tag number, field name or datatype. Additionally, a link is provided to list of user-defined fields on the FIX website. The following details are provided for each field:
Tag number (identical to the repository identifier)
Field name
Abbreviated name (e.g. for FIXML)
Datatype
Union datatype (e.g. Reserved100Plus)
Description
Pedigree
Code Sets: list of FIX code sets sorted by name. The following details are provided for each code set:
Code set name
Repository identifier (unique across all codesets)
Base datatype of the codes
Description (synopsis only, no elaboration)
Pedigree
Datatypes: list of FIX and FIXML datatypes. The following details are provided for each datatype:
Datatype name
Base datatype
XML builtin (Y/N) – only for FIXML
XML base type – only for FIXML
XML pattern – only for FIXML
Minimum value (inclusive) – only for FIXML
Description
Pedigree
The elements in these lists can then be selected to see more detailed information. Message and component details are displayed in the upper pane of the right-hand side, thereby replacing the previous list. Fields and code set details are displayed in the lower pane of the right-hand side without removing the list from the upper pane.

The fourth and last section on the left-hand side offers a detailed list of FIX messages structured by business area and category. Each of the areas and categories can be expanded or collapsed to show the desired subset of FIX messages. The user may then click on any of the messages to trigger its display in the upper pane of the right-hand side.

Display of search results
Search results from the Find all box are displayed in the upper pane of the right-hand side of the screen. The results are sorted by name grouped as follows:

Message names: list of messages names.
Component names: list of component names.
Field names: list of field names together with their tag number.
Field descriptions: list of field names together with their tag number and the first 80 characters of the first line of the field description (synopsis in the FIX Orchestra Repository).
Code set names: list of code set names
Codes: list of code sets together with the matching code value and name.
Display of messages
Messages are displayed in the upper pane of the right-hand side of the screen. The message name can be clicked to open the message details in a separate tab for better visibility. The nested components of a message are collapsed upon display and can be individually expanded or collapsed by clicking on Component or the name of the component. It is also possible to collapse or expand all components at once.

When expanding a component, the screen area to the left of the first column changes to a grey color to show what belongs to this component. If the component is a repeating group, an additional visualization is provided in form of a bracket. This is useful when analyzing deeply nested components with multiple repeating groups.

Additionally, upon expansion of a component, the lower pane is used to display the overall usage of this component in FIX messages and/or components. Any of the displayed message or component names can be selected to have the upper pane display it instead of the message shown before.

The following information is provided:

Name: full name, e.g. NewOrderSingle, abbreviated name, e.g. <Order>, and message type (MsgType(35)) are provided.
Description: synopsis and elaboration (can be toggled with more and less, only the synopsis is displayed initially).
Pedigree: FIX version or Extension Pack the message was added, last updated, and deprecated (if applicable).
Message elements: an element can be a component or an individual field and the following information is provided per element:
Tag number: the number can be clicked to display the details of the field in the lower pane.
Field name: the name can be clicked to display the details of the field in the lower pane.
Abbreviated name: the abbreviated name is used for the FIXML encoding.
Required: indicates whether this field or component is always required.
Comments: field or component usage description, i.e. a specific description for the given context going beyond what is defined for the field in general (click on the field to display this in the lower pane).
Pedigree: FIX version or Extension Pack the field or component was added to, last updated in, and deprecated from (if applicable) the message.
Display of components
Components are displayed in the upper pane of the right-hand side of the screen. The component name can be clicked to open the component details in a separate tab for better visibility. The information provided for the component and the handling of nested components are identical to what is available for messages (see above). Additionally, information about the usage of the given component is provided at the end of the upper pane.

Display of fields
Fields are displayed in the lower pane of the right-hand side of the screen. The tag number or field name can be clicked to open the field details in a separate tab for better visibility. The usage of a given field in messages and components is displayed at the end of the lower pane. Any of these message or component names can be selected to have the upper pane display the details.

Instead of resizing upper and lower pane to increase the space for the display of a field with a large code set, it is possible to click on the field name to open a separate browser tab that only shows the field details.

The following information is provided for a field:

Tag number: unique number to identify the field.
Field name: unique name of the field.
Abbreviated name: the abbreviated name is used for the FIXML encoding and is not unique.
Datatype: base datatype of the field.
Union Datatype: additional datatype if the field has a code set as datatype but supports user-defined values, e.g. datatype Reserved100Plus allows user-defined values of 100 and above.
Description: synopsis and elaboration (set in italic font), followed by the name of the code set (if applicable). The codes may be grouped and detailed information is provided as follows:
Value: code (a.k.a. enumeration value) using the base datatype
Name (synopsis): Short description of the value
Elaboration: additional description for the value (set in italic font)
Pedigree: FIX version or Extension Pack the codeset value was added, last updated, and deprecated (if applicable).
Symbolic name: single term that can be used by software to identify the name
Pedigree: FIX version or Extension Pack the field was added to, last updated in, and deprecated from (if applicable) the FIX Repository.
Display of code sets
Code sets are displayed similar to fields in the lower pane of the right-hand side of the screen. The usage of a given code set in fields is displayed at the end of the lower pane. Any of these field names can be selected to have the lower pane display the details, thereby replacing the code set shown there before.

The following information is provided for a code set:

Code set name: the name can be clicked to display the details of the code set in a separate browser tab.
Datatype: base datatype of the code set.
Union Datatype: additional datatype if the field has a code set as datatype but supports user-defined values, e.g. datatype Reserved100Plus allows user-defined values of 100 and above.
Description: synopsis and elaboration (set in italic font), followed by the name of the code set (if applicable). The codes may be grouped and detailed information is identical to what is provided for a field using a code set (see field description above).
URLs for direct access
FIXimate can be invoked from the FIX website by using the dropdown menu Tools. This opens up FIXimate in your browser as it is a simple URL (https://fiximate.fixtrading.org/). However, it is also possible to use a URL with additional elements in two ways.

Open a full version of FIXimate with the result of a predefined search
Open FIXimate as a single frame to show an individual message, component, field or code set.
The first usage requires to append a single parameter to the base URL to provide an identifier or name of a message, component, field or code set. It is also possible to append an arbitrary search term as if one had manually entered it into the Find all search box. The result is FIXimate running in a browser with all three panes, the search item being shown on the left-hand side and the search result in the upper pane of the right-hand side.

Here are some examples:

Message by MsgType(35): https://fiximate.fixtrading.org?msgtype=D
Component by name: https://fiximate.fixtrading.org?comp=Instrument
Field by tag number: https://fiximate.fixtrading.org?tag=11
Field by name: https://fiximate.fixtrading.org?field=ClOrdId
Code set by name:https://fiximate.fixtrading.org?codeset=AdvSideCodeSet
Search: https://fiximate.fixtrading.org?find=Limit
The second usage is to extend the URL with direct access to the message, component, field or code set. This is useful as part of documentation or specifications to reference the standard FIX definition.

This approach does not apply to an arbitrary search and requires knowing the unique identifier as defined in the FIX Orchestra Repository. The result is a single pane with the details of the selected message, component, field or code set.

Here are some examples:

Message by identifier: https://fiximate.fixtrading.org/en/FIX.Latest/msg14.html
Component by identifier: https://fiximate.fixtrading.org/en/FIX.Latest/cmp1003.html
Field by tag number: https://fiximate.fixtrading.org/en/FIX.Latest/tag11.html
Code set by identifier: https://fiximate.fixtrading.org/en/FIX.Latest/cds4.html