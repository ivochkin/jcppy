#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details).
#
# For JSON-Schema spec, see http://tools.ietf.org/html/draft-fge-json-schema-validation-00

jcppyVersion = '0.0.1'

import sys
import os
import json
import argparse
import pprint
import codecs

env = {}

def debug(p):
    'Pretty print object. Useful for debugging'
    pprint.PrettyPrinter().pprint(p)


def indent(o):
    'Return an output functor with higher indentation level'
    return lambda x : o(x) if x == '\n' else o('  ' + x)


def title(word):
    'Uppercase first letter of `word\''
    return word[0].upper() + word[1:]


def snippet(env, name):
    with open(os.path.join(env['snippet_dir'], name)) as f:
        return f.read()


def storageType(s):
    '''
    Return storage type for object defined by schema `s\'.
    Storage type is a c++ type stored in class instance.
    '''
    gen = s['generator']
    if gen == 'object':
        return s['name']
    if gen == 'array':
        return 'std::vector<{}>'.format(storageType(s['items']))

    return {
        'boolean': 'bool'
        , 'string': 'std::string'
        , 'integer': 'int'
        , 'number': 'double'
        , 'date-time': 'jcppy::date_time'
        , 'utc-millisec': 'jcppy::uint64_t'
        , 'uuid': 'jcppy::uuid'
        , 'base64': 'std::vector<char>'
    }[gen]


def argumentType(s):
    '''
    Return argument type for object defined by schema `s\'.
    Argument type is a c++ type used for argument passing in setFoo(..)
    and return type in getFoo(..) methods.
    '''
    gen = s['generator']
    if gen == 'object':
        return 'const {}&'.format(s['name'])
    if gen == 'array':
        return 'const std::vector<{}>&'.format(storageType(s['items']))

    return {
        'boolean': 'bool'
        , 'string': 'const std::string&'
        , 'integer': 'int'
        , 'number': 'double'
        , 'date-time': 'const jcppy::date_time&'
        , 'utc-millisec': 'jcppy::uint64_t'
        , 'uuid': 'const jcppy::uuid&'
        , 'base64': 'const std::vector<char>&'
    }[gen]


def resolveCppTypes(s, firstPass=False):
    'Resolve argument types, storage types and generators for each type in schema'
    if s == {}:
        return

    if 'generator' in s:
        # executed only during the second pass
        s[u'sto_type'] = storageType(s)
        s[u'arg_type'] = argumentType(s)

    s[u'generator'] = s['format'] if s['type'] == 'string' and 'format' in s else s['type']

    if not firstPass:
        if s['generator'] == 'uuid':
            env['useBoostUuid'] = True
        if s['generator'] == 'date-time':
            env['useBoostDateTime'] = True
        if s['generator'] == 'utc-millisec':
            env['useBoostCstdint'] = True
        if s['generator'] == 'base64':
            env['useBase64'] = True

    for i in s.get('properties', {}).values():
        i = resolveCppTypes(i, firstPass)
    resolveCppTypes(s.get('items', {}), firstPass)
    return s


def enumerateObjects(prefix, schema):
    'Make a list of all objects in schema (including nested)'

    if not (schema['type'] == 'object' or schema['type'] == 'array'):
        return []

    if schema['type'] == 'object':
        newPrefix = schema['name'] if prefix == '' else prefix + '::' + schema['name']
        return [newPrefix] + [j for i in schema['properties'].values() for j in enumerateObjects(newPrefix, i)]

    if schema['type'] == 'array':
        return [j for j in enumerateObjects(prefix, schema['items'])]


def headerHasClear(name, schema, o):
    'Generate declarations of hasFoo() clearFoo() methods plus hasFoo_ member'

    o('\n')
    o('public:\n')
    o('  bool has{}() const{};\n'.format(title(name), env['noexcept']))
    o('  void clear{}(){};\n'.format(title(name), env['noexcept']))
    o('private:\n')
    o('  bool has{}_;\n'.format(title(name)))


def sourceHasClear(memName, className, schema, o):
    'Generate definition of hasFoo() clearFoo() methods'

    o('\n')
    o('bool {}::has{}() const{}\n'.format(title(className), title(memName), env['noexcept']))
    o('{\n')
    o('  return has{}_;\n'.format(title(memName)))
    o('}\n')

    o('\n')
    o('void {}::clear{}(){}\n'.format(title(className), title(memName), env['noexcept']))
    o('{\n')
    o('  has{}_ = false;\n'.format(title(memName)))
    o('}\n')


def headerDefault(name, schema, o):
    'Generate declaration of defaultFoo() method if property have default value'

    if not 'default' in schema:
        return

    if schema['generator'] == 'boolean':
        defValue = 'true' if schema['default'] else 'false'
    else:
        defValue = schema['default']

    o('\n')
    o('public:\n')

    if schema['generator'] == 'string':
        o('  static constexpr const char* default{}(){} {{ return "{}"; }}\n'\
            .format(title(name), env['noexcept'], defValue))
        return

    o('  static constexpr {} default{}(){} {{ return {}; }}\n'\
        .format(schema['arg_type'], title(name), env['noexcept'], defValue))


def headerPrimitive(name, schema, o):
    'Generate declarations for primitive type'

    o('\n')
    o('public:\n')
    o('  {0} {1}() const;\n'.format(schema['arg_type'], name))
    o('  void set{0}({1} new{0}){2}\n'.format(title(name), schema['arg_type'], '' if env['noexcept'] else ';'))
    if env['noexcept']:
        o('      noexcept(std::is_nothrow_copy_constructible<{}>::value);\n'.format(schema['sto_type']))
    o('private:\n')
    o('  {0} {1}_;\n'.format(schema['sto_type'], name))

    headerHasClear(name, schema, o)

    headerDefault(name, schema, o)


def sourcePrimitive(memName, className, schema, o):
    'Generate definitions for primitive type'

    o('\n')
    o('{} {}::{}() const\n'.format(schema['arg_type'], className, memName))
    o('{\n')
    o('  if (!has{}_) {{\n'.format(title(memName)))
    o('    JCPPY_THROW(std::runtime_error("Member \\"{}\\" is not set"));\n'.format(memName))
    o('  }\n')
    o('  return {}_;\n'.format(memName))
    o('}\n')

    o('\n')
    o('void {0}::set{1}({2} new{1})\n'.format(className, title(memName), schema['arg_type']))
    if env['noexcept']:
        o('    noexcept(std::is_nothrow_copy_constructible<{}>::value)\n'.format(schema['sto_type']))
    o('{\n')
    o('  {0}_ = new{1};\n'.format(memName, title(memName)))
    o('  has{}_ = true;\n'.format(title(memName)))
    o('}\n')

    sourceHasClear(memName, className, schema, o)


def headerMovable(name, schema, o):
    'Generate declarations for movable type'

    argType = schema['arg_type']
    stoType = schema['sto_type']

    o('\n')
    o('public:\n')
    o('  {} {}() const{};\n'.format(argType, name, env['noexcept']))
    o('  void set{0}({1} new{0});\n'.format(title(name), argType))
    o('  void set{0}({1}&& new{0}){2};\n'.format(title(name), stoType, env['noexcept']))

    headerHasClear(name, schema, o)

    o('\n')
    o('public:\n')
    o('  {}* mutable{}(){};\n'.format(stoType, title(name), env['noexcept']))

    o('\n')
    o('private:\n')
    o('  {0} {1}_;\n'.format(stoType, name))

    headerDefault(name, schema, o)


def sourceMovable(memName, className, schema, o):
    'Generate definitions for movable type'

    argType = schema['arg_type']
    stoType = schema['sto_type']

    o('\n')
    o('{} {}::{}() const{}\n'.format(argType, className, memName, env['noexcept']))
    o('{\n')
    o('  if (!has{}_) {{\n'.format(title(memName)))
    o('    JCPPY_THROW(std::runtime_error("Member \\"{}\\" is not set"));\n'.format(memName))
    o('  }\n')
    o('  return {}_;\n'.format(memName))
    o('}\n')

    o('\n')
    o('void {0}::set{1}({2} new{1})\n'.format(className, title(memName), argType))
    o('{\n')
    o('  {0}_ = new{1};\n'.format(memName, title(memName)))
    o('  has{}_ = true;\n'.format(title(memName)))
    o('}\n')

    o('\n')
    o('void {0}::set{1}({2}&& new{1}){3}\n'.format(className, title(memName), stoType, env['noexcept']))
    o('{\n')
    o('  {0}_ = std::move(new{1});\n'.format(memName, title(memName)))
    o('  has{}_ = true;\n'.format(title(memName)))
    o('}\n')

    sourceHasClear(memName, className, schema, o)

    o('\n')
    o('{}* {}::mutable{}(){}\n'.format(stoType, title(className), title(memName), env['noexcept']))
    o('{\n')
    o('  has{}_ = true;\n'.format(title(memName)))
    o('  return &{}_;\n'.format(memName))
    o('}\n')


def headerBase64(name, schema, o):
    'Generate declarations for base64 type'

    o('\n')
    o('public:\n')
    o('  const std::vector<char>& {}() const{};\n'.format(name, env['noexcept']))
    o('  void set{0}(const std::vector<char>& new{0});\n'.format(title(name)))
    o('  void set{0}(std::vector<char>&& new{0}){1};\n'.format(title(name), env['noexcept']))
    o('  std::vector<char>* mutable{}(){};\n'.format(title(name), env['noexcept']))
    headerHasClear(name, schema, o)
    o('private:\n')
    o('  std::vector<char> {}_;\n'.format(name))


def sourceBase64(memName, className, schema, o):
    'Generate definitions for base64 type'

    o('const std::vector<char>& {}::{}() const{}\n'.format(className, memName, env['noexcept']))
    o('{\n')
    o('  return {}_;\n'.format(memName))
    o('}\n')

    o('\n')
    o('void {0}::set{1}(const std::vector<char>& new{1})\n'.format(className, title(memName)))
    o('{\n')
    o('  {0}_ = new{1};\n'.format(memName, title(memName)))
    o('  has{}_ = true;\n'.format(title(memName)))
    o('}\n')

    o('\n')
    o('void {0}::set{1}(std::vector<char>&& new{1}){2}\n'.format(className, title(memName), env['noexcept']))
    o('{\n')
    o('  {0}_ = std::move(new{1});\n'.format(memName, title(memName)))
    o('  has{}_ = true;\n'.format(title(memName)))
    o('}\n')

    o('\n')
    o('std::vector<char>* {}::mutable{}(){}\n'.format(className, title(memName), env['noexcept']))
    o('{\n')
    o('  has{}_ = true;\n'.format(title(memName)))
    o('  return &{}_;\n'.format(memName))
    o('}\n')

    sourceHasClear(memName, className, schema, o)


def headerObject(_, schema, o):
    'Generate declarations for root type'

    oo = indent(o)

    o('\n')
    if 'title' in schema.keys():
        o(u'/// @brief {}\n'.format(schema['title'].replace('\n', '\n/// ')))

    if 'description' in schema.keys():
        o(u'/// @detail {}\n'.format(schema['description'].replace('\n', '\n/// ')))

    o('class {}\n'.format(schema['name']))
    o('{\n')
    oo('friend class JcppyHelper;\n')
    o('public:\n')
    oo('{}(){};\n'.format(schema['name'], env['noexcept']))
    oo('explicit {}(std::istream&);\n'.format(schema['name']))
    oo('explicit {}(const std::string&);\n'.format(schema['name']))

    o('\n')
    o('public:\n')
    oo('// Group of methods for json serialization\n')
    oo('std::string json() const;\n')
    oo('void writeJson(std::ostream&) const;\n')
    oo('void writeJson(void*) const;\n')
    oo('void fromJson(const std::string&);\n')
    oo('void readJson(std::istream&);\n')
    o('private:\n')
    oo('void readDocument(void*);\n')

    o('\n')
    o('public:\n')
    oo('// General methods\n')
    oo('void clear();\n')
    oo('void ensureInitialized() const;\n')
    oo('///@returns true if any property was set to default\n')
    oo('bool populateDefaults();\n')

    for name, schema in schema['properties'].items():
        if not schema['generator'] in headerGenerators:
            continue
            raise Exception('unsupported type "{}"'.format(schema['generator']))
        o('\n')
        o('//' + '-' * 77 + '\n')
        o('// Methods and fields related to field "{}"\n'.format(name))
        o('//   Type     : {}\n'.format(schema['type']))
        o('//   Format   : {}\n'.format(schema.get('format', None)))
        o('//' + '-' * 77 + '\n')

        headerGenerators[schema['generator']](name, schema, o)

    o('};\n')


def headerNestedObject(name, schema, o):
    'Generate declarations for any object type excluding root object'

    o('\n')
    o('public:')
    headerObject(None, schema, indent(o))

    headerMovable(name, schema, o)


def writeJsonAny(name, schema, o):
    oo = indent(o)

    if schema['generator'] == 'object':
        o('{}.writeJson(writer);\n'.format(name))
        return

    if schema['generator'] == 'array':
        o('writer->StartArray();\n')
        o('for (const auto& i : {}) {{\n'.format(name))
        writeJsonAny('i'.format(name), schema['items'], oo)
        o('}\n')
        o('writer->EndArray();\n')
        return

    if schema['generator'] == 'boolean':
        o('writer->Bool({});\n'.format(name))
        return

    if schema['generator'] == 'string':
        oo('writer->String({0}.c_str(), {0}.length());\n'.format(name))
        return

    if schema['generator'] == 'base64':
        o('{\n')
        oo('auto tmp = ::base64({});\n'.format(name));
        oo('writer->String(tmp.c_str(), tmp.length());\n')
        o('}\n')
        return

    if schema['generator'] == 'date-time':
        o('{\n')
        oo('auto tmp = boost::posix_time::to_iso_extended_string({});\n'.format(name));
        oo('writer->String(tmp.c_str(), tmp.length());\n')
        o('}\n')
        return

    if schema['generator'] == 'number':
        o('writer->Double({});\n'.format(name))
        return

    if schema['generator'] == 'integer':
        o('writer->Int({});\n'.format(name))
        return

    if schema['generator'] == 'utc-millisec':
        o('writer->Int64({});\n'.format(name))
        return

    if schema['generator'] == 'uuid':
        o('{\n')
        oo('auto tmp = boost::uuids::to_string({});\n'.format(name));
        oo('writer->String(tmp.c_str(), tmp.length());\n')
        o('}\n')
        return

    raise Exception('unknown generator "' + schema['generator'] + '"')


def writeJsonObject(name, schema, o):
    oo = indent(o)

    o('Writer* writer = static_cast<Writer*>(writerr);\n')
    o('\n')
    o('writer->StartObject();\n')
    for name, s in schema['properties'].items():
        o('\n')
        o('if (has{}_) {{\n'.format(title(name)))
        oo('writer->String(\"{}\");\n'.format(name))
        writeJsonAny('{}_'.format(name), s, oo)
        o('}\n')
    o('\n')
    o('writer->EndObject();\n')


def readJsonAny(obj, name, schema, o):
    oo = indent(o)

    jsonType = {
        'object': 'Object'
        , 'array' : 'Array'
        , 'boolean' : 'Bool'
        , 'string' : 'String'
        , 'base64' : 'String'
        , 'date-time' : 'String'
        , 'number' : 'Double'
        , 'integer' : 'Int'
        , 'utc-millisec' : 'Int64'
        , 'uuid' : 'String'
    }

    o('if (!{}.Is{}()) {{\n'.format(obj, jsonType[schema['generator']]))
    oo('JCPPY_THROW(std::runtime_error("Json type mismatch for member \\"{}\\""));\n'.format(name))
    o('}\n')


    if schema['generator'] == 'object':
        o('{} tmp;\n'.format(schema['sto_type'], name))
        o('JcppyHelper::readDocument(tmp, &{});\n'.format(obj))
        o('{} = std::move(tmp);\n'.format(name))
        return

    if schema['generator'] == 'array':
        o('{}.resize({}.Size());\n'.format(name, obj))
        o('for (std::size_t i = 0; i < {}.Size(); ++i) {{\n'.format(obj))
        readJsonAny('{}[i]'.format(obj), '{}[i]'.format(name), schema['items'], oo)
        o('}\n')
        return

    if schema['generator'] in ['number', 'integer', 'utc-millisec', 'boolean']:
        o('{} = {}.Get{}();\n'.format(name, obj, jsonType[schema['generator']]))
        return

    if schema['generator'] == 'string':
        o('{0}.assign({1}.GetString(), {1}.GetStringLength());\n'.format(name, obj))
        return

    if schema['generator'] == 'base64':
        o('{0} = ::fromBase64({1}.GetString(), {1}.GetStringLength());\n'.format(name, obj))
        return

    if schema['generator'] == 'date-time':
        o('std::string tmp({0}.GetString(), {0}.GetStringLength());\n'.format(obj))
        o('{} = boost::posix_time::time_from_string(std::move(tmp));\n'.format(name))
        return

    if schema['generator'] == 'uuid':
        o('boost::uuids::string_generator gen;\n')
        o('{0} = gen({1}.GetString(), {1}.GetString() + {1}.GetStringLength());\n'.format(name, obj))
        return

    raise Exception('unknown generator "' + schema['generator'] + '"')


def readJsonObject(name, schema, o):
    oo = indent(o)
    ooo = indent(oo)

    o('auto doc = static_cast<Document*>(document);\n')
    o('if (!doc->IsObject()) {\n')
    oo('JCPPY_THROW(std::runtime_error("json document must be object"));\n')
    o('}\n')
    o('\n')
    o('for (auto i = doc->MemberBegin(); i != doc->MemberEnd(); ++i) {\n')
    oo('assert(i->name.IsString());\n')
    oo('auto iname = boost::string_ref(i->name.GetString(), i->name.GetStringLength());\n')
    oo('auto& ivalue = i->value;\n')
    for name, s in schema['properties'].items():
        o('\n')
        oo('if (iname == \"{}\") {{\n'.format(name))
        readJsonAny('ivalue', '{}_'.format(name), s, ooo)
        ooo('has{}_ = true;\n'.format(title(name)))
        ooo('continue;\n')
        oo('}\n')
    o('}\n')
    o('ensureInitialized();\n')


def sourceObject(_, __, schema, o):
    'Generate definitions for root type'

    className = schema['name']
    oo = indent(o)
    ooo = indent(oo)
    oooo = indent(ooo)

    # @todo add indent support here
    o('\n')
    o('{0}::{0}(){1}\n'.format(className, env['noexcept']))
    oo(': ')
    o('\n  , '.join(['has{}_(false)'.format(title(i)) for i in schema['properties'].keys()]))
    o('\n')
    o('{\n')
    o('}\n')

    o('\n')
    o('{0}::{0}(std::istream& is)\n'.format(schema['name']))
    oo(': {}()\n'.format(schema['name']))
    o('{\n')
    oo('readJson(is);\n')
    o('}\n')

    o('\n')
    o('{0}::{0}(const std::string& json)\n'.format(schema['name']))
    oo(': {}()\n'.format(schema['name']))
    o('{\n')
    oo('fromJson(json);\n')
    o('}\n')

    o('\n')
    o('std::string {}::json() const\n'.format(className))
    o('{\n')
    oo('std::stringstream s;\n')
    oo('writeJson(s);\n')
    oo('return s.str();\n')
    o('}\n')

    o('\n')
    o('void {}::writeJson(std::ostream& out) const\n'.format(className))
    o('{\n')
    oo('::OStreamWrapper sw(out);\n')
    oo('Writer writer(sw);\n')
    oo('writeJson(&writer);\n')
    o('}\n')

    o('\n')
    o('void {}::writeJson(void* writerr) const\n'.format(className))
    o('{\n')
    oo('ensureInitialized();\n')
    writeJsonObject(None, schema, oo)
    o('}\n')

    o('\n')
    o('void {}::fromJson(const std::string& jsonObject)\n'.format(className))
    o('{\n')
    oo('std::stringstream s(jsonObject);\n')
    oo('s >> std::noskipws;\n')
    oo('readJson(s);\n')
    o('}\n')

    o('\n')
    o('void {}::readJson(std::istream& is)\n'.format(className))
    o('{\n')
    oo('Document doc;\n')
    oo('::IStreamWrapper s(is);\n')
    oo('doc.ParseStream<0>(s);\n')
    oo('if (doc.HasParseError()) {\n')
    ooo('JCPPY_THROW(std::runtime_error(doc.GetParseError()));\n')
    oo('}\n')
    oo('readDocument(&doc);\n')
    o('}\n')

    o('\n')
    o('void {}::readDocument(void* document)\n'.format(className))
    o('{\n')
    oo('clear();\n')
    oo('\n')
    readJsonObject(None, schema, oo)
    o('}\n')

    o('\n')
    o('void {}::ensureInitialized() const\n'.format(className))
    o('{')
    for i in schema.get('required', []):
        oo('\n')
        oo('if (!has{}_) {{\n'.format(title(i)))
        ooo('JCPPY_THROW(std::runtime_error("Member \\"{}\\" is not initialized"));\n'.format(i))
        oo('}\n')
    o('}\n')

    o('\n')
    o('bool {}::populateDefaults()\n'.format(className))
    o('{\n')
    oo('bool res = false;\n')
    for name, s in schema['properties'].items():
        if not (s['type'] == 'object' or 'default' in s):
            continue
        oo('\n')
        oo('if (!has{}_) {{\n'.format(title(name)))
        if 'default' in s:
            ooo('set{0}(default{0}());\n'.format(title(name)))
            ooo('res = true;\n')
        elif s['type'] == 'object':
            ooo('if ({}_.populateDefaults()) {{\n'.format(name))
            oooo('has{}_ = true;\n'.format(title(name)))
            oooo('res = true;\n')
            ooo('}\n');
        oo('}\n')
    oo('return res;\n')
    o('}\n')

    o('\n')
    o('void {}::clear()\n'.format(className))
    o('{\n')
    for name, s in schema['properties'].items():
        oo('has{}_ = false;\n'.format(title(name)))
        if s['generator'] in ['array', 'object']:
            oo('{}_.clear();\n'.format(name))
    o('}\n')

    for name, s in schema['properties'].items():
        if not s['type'] in headerGenerators:
            raise Exception('unsupported type "{}"'.format(s['type']))
        sourceGenerators[s['generator']](name, className, s, o)


def sourceNestedObject(memName, className, schema, o):
    'Generate definitions for any object type excluding root object'

    sourceObject(None, None, schema, o)
    sourceMovable(memName, className, schema, o)


def headerArray(name, schema, o):
    'Generate declarations for array type'

    if schema['items']['type'] == 'object':
        o('\n')
        o('public:')
        headerObject(None, schema['items'], indent(o))

    o('\n')
    headerMovable(name, schema, o)


def sourceArray(memName, className, schema, o):
    'Generate definitions for array type'

    if schema['items']['type'] == 'object':
        sourceObject(None, None, schema['items'], o)

    o('\n')
    sourceMovable(memName, className, schema, o)


headerGenerators = {
    'boolean': headerPrimitive,
    'string': headerMovable,
    'integer': headerPrimitive,
    'number': headerPrimitive,
    'date-time': headerPrimitive,
    'utc-millisec': headerPrimitive,
    'uuid': headerPrimitive,
    'base64': headerBase64,
    'object': headerNestedObject,
    'array': headerArray
}

sourceGenerators = {
    'boolean': sourcePrimitive,
    'string': sourceMovable,
    'integer': sourcePrimitive,
    'number': sourcePrimitive,
    'date-time': sourcePrimitive,
    'utc-millisec': sourcePrimitive,
    'uuid': sourcePrimitive,
    'base64': sourceBase64,
    'object': sourceNestedObject,
    'array': sourceArray
}


def header(env, schema, o):
    if schema['type'] != 'object':
        raise Exception('jcppy can generate cpp classes only for objects')

    o('/// @file Generated by jcppy\n')
    o('/// @warning Do not edit!\n')
    o('\n')
    o('#pragma once\n')
    o('#include <string>\n')
    o('#include <vector>\n')
    o('#include <type_traits>\n')

    hasDateTime, hasUuid, hasCstdint = env['useBoostDateTime'], env['useBoostUuid'], env['useBoostCstdint']

    if hasUuid:
        o('#include <boost/uuid/uuid.hpp>\n')
        o('#include <boost/uuid/uuid_io.hpp>\n')

    if hasDateTime:
        o('#include <boost/date_time/posix_time/posix_time_types.hpp>\n')

    if hasCstdint:
        o('#include <boost/cstdint.hpp>\n')

    if hasUuid or hasDateTime or hasCstdint:
        o('\n')
        o('namespace jcppy {\n')
        o('\n')
        if hasUuid:
            o('typedef boost::uuids::uuid uuid;\n')
        if hasDateTime:
            o('typedef boost::posix_time::ptime date_time;\n')
        if hasCstdint:
            o('typedef boost::uint64_t uint64_t;\n')
        o('\n')
        o('} // namespace jcppy\n')

    o('\n')
    o('\n'.join(['namespace {} {{'.format(i) for i in env['namespace'].split('::')]) + '\n')

    o('\n')
    o('class JcppyHelper;\n')

    headerObject(None, schema, o)

    o('\n')
    o('}' * len(env['namespace'].split('::')) + ' // namespace {}\n'.format(env['namespace']))


def source(env, schema, o):
    o('/// @file Generated by jcppy ({})\n'.format(env['version']))
    o('/// @warning Do not edit!\n')
    o('#include <stdexcept>\n')
    o('#include <sstream>\n')

    if env['useBoostUuid']:
        o('#include <boost/uuid/uuid_io.hpp>\n')
        o('#include <boost/uuid/uuid_generators.hpp>\n')

    if env['useBoostDateTime']:
        o('#include <boost/date_time/posix_time/posix_time.hpp>\n')

    if env['useBoostThrowException']:
        o('#include <boost/throw_exception.hpp>\n')

    o('#include <boost/utility/string_ref.hpp>\n')

    o('#include <rapidjson/writer.h>\n')
    o('#include <rapidjson/document.h>\n')

    o('#include "{}"\n'.format(env['header']))

    o('\n')
    o('namespace {\n')

    o('\n')
    o(snippet(env, 'ostream_wrapper.inl'))

    o('\n')
    o(snippet(env, 'istream_wrapper.inl'))

    if env['useBase64']:
        o('\n')
        o(snippet(env, 'base64.inl'))
        o('\n')
        o(snippet(env, 'from_base64.inl'))

    o('\n')
    o('} // anonymous namespace\n')

    o('\n')
    o('\n'.join(['namespace {} {{'.format(i) for i in env['namespace'].split('::')]) + '\n')
    o('\n')
    o(snippet(env, 'jcppy_helper.inl'))
    o('\n')
    o('}' * len(env['namespace'].split('::')) + ' // namespace {}\n'.format(env['namespace']))

    o('\n')
    o('typedef rapidjson::Writer<::OStreamWrapper> Writer;\n')
    o('typedef rapidjson::Document Document;\n')
    for i in enumerateObjects('', schema):
        o('typedef {}::{} {};\n'.format(env['namespace'], i, i.split('::')[-1]))

    o('\n')
    if env['useBoostThrowException']:
        o('#define JCPPY_THROW(x) BOOST_THROW_EXCEPTION(x)\n')
    else:
        o('#define JCPPY_THROW(x) throw x\n')

    sourceObject(None, None, schema, o)


def main():
    global env
    parser = argparse.ArgumentParser(
        description='Generate c++ classes from the given json-schema'
        , prog='jcppy'
        , formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('files', metavar='file', type=unicode, nargs='+', help='json-schema files to process')
    parser.add_argument('-n', '--namespace', metavar='<namespace>', type=unicode, default='gen', help='namespace to place generated classes in. May be of format "foo::bar"')
    parser.add_argument('-o', '--output-dir', metavar='<directory>', type=unicode, default=argparse.SUPPRESS, help='directory to store generated files to')
    parser.add_argument('-s', '--snippet-dir', metavar='<directory>', type=unicode, default=os.path.realpath(os.path.join(os.path.dirname(__file__), '../share/jcppy/snippet')), help='directory with code snippets used by %(prog)s.')
    parser.add_argument('--noexcept', help='generate noexcept specifiers', default=False, action='store_true')
    parser.add_argument('--boost-throw-exception', help='use BOOST_THROW_EXCEPTION macro instead of throw()', default=True, action='store_true')
    parser.add_argument('--verbose', help='print debug messages', default=False, action='store_true')
    parser.add_argument('-v', '--version', help='print version', action='version', version='%(prog)s {}'.format(jcppyVersion))

    args = parser.parse_args()
    for i in args.files:
        headerFile = os.path.basename(i[:i.rfind('.')]) + '.h'
        sourceFile = os.path.basename(i[:i.rfind('.')]) + '.cpp'
        if not args.output_dir is None:
            headerFile = os.path.join(args.output_dir, headerFile)
            sourceFile = os.path.join(args.output_dir, sourceFile)
        env = {
            'version': jcppyVersion,
            'namespace' : args.namespace,
            'header' : headerFile,
            'source' : sourceFile,
            'verbose' : args.verbose,
            'useBoostUuid' : False,
            'useBoostDateTime' : False,
            'useBoostCstdint' : False,
            'useBase64': False,
            'useBoostThrowException' : args.boost_throw_exception,
            'noexcept': ' noexcept' if args.noexcept else '',
            'snippet_dir': args.snippet_dir
        }
        with open(i) as schemaF, codecs.open(headerFile, 'w', 'utf-8') as hF, codecs.open(sourceFile, 'w', 'utf-8') as sF:
            schema = resolveCppTypes(json.loads(schemaF.read()), firstPass=True)
            schema = resolveCppTypes(schema, firstPass=False)
            if env['verbose']:
                debug(schema)
            header(env, schema, hF.write)
            source(env, schema, sF.write)
    return 0

if __name__ == '__main__':
    sys.exit(main())
