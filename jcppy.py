#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2015 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details).
#
# For JSON-Schema spec, see
# http://tools.ietf.org/html/draft-fge-json-schema-validation-00
'''
Jcppy - C++ generator for JSON Schema written in python.
'''

JCPPY_VERSION = '0.0.1'

import sys
import os
import json
import argparse
import pprint
import codecs


def debug(obj):
    'Pretty print object. Useful for debugging'
    pprint.PrettyPrinter().pprint(obj)


def indent(printer):
    'Return an output functor with higher indentation level'
    return lambda x: printer(x) if x == '\n' else printer('  ' + x)


def title(word):
    'Uppercase first letter of `word\''
    return word[0].upper() + word[1:]


def snippet(env, o, name, specification=None):
    'Return snippet content with format provided in specification'
    with open(os.path.join(env['snippet_dir'], name)) as snippet_fo:
        template = snippet_fo.read()
        o('\n')
        o(template % specification if specification else template)


def storage_type(s):
    '''
    Return storage type for object defined by schema `s\'.
    Storage type is a c++ type stored in class instance.
    '''
    gen = s['generator']
    if gen == 'object':
        return s['name']
    if gen == 'array':
        return 'std::vector<{}>'.format(storage_type(s['items']))

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


def argument_type(s):
    '''
    Return argument type for object defined by schema `s\'.
    Argument type is a c++ type used for argument passing in setFoo(..)
    and return type in getFoo(..) methods.
    '''
    gen = s['generator']
    if gen == 'object':
        return 'const {}&'.format(s['name'])
    if gen == 'array':
        return 'const std::vector<{}>&'.format(storage_type(s['items']))

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


def resolve_cpp_types(env, s, first_pass=False):
    '''
    Resolve argument types, storage types and generators
    for each type in schema'
    '''
    if s == {}:
        return

    if 'generator' in s:
        # executed only during the second pass
        s[u'sto_type'] = storage_type(s)
        s[u'arg_type'] = argument_type(s)

    if s['type'] == 'string' and 'format' in s:
        s[u'generator'] = s['format']
    else:
        s[u'generator'] = s['type']

    if not first_pass:
        if s['generator'] == 'uuid':
            env['useBoostUuid'] = True
        if s['generator'] == 'date-time':
            env['useBoostDateTime'] = True
        if s['generator'] == 'utc-millisec':
            env['useBoostCstdint'] = True
        if s['generator'] == 'base64':
            env['useBase64'] = True

    for i in s.get('properties', {}).values():
        i = resolve_cpp_types(env, i, first_pass)
    resolve_cpp_types(env, s.get('items', {}), first_pass)
    return s


def all_names(prefix, sch):
    'Make a list of all objects in schema (including nested)'

    if not (sch['type'] == 'object' or sch['type'] == 'array'):
        return []

    if sch['type'] == 'object':
        prefix = sch['name'] if prefix == '' else prefix + '::' + sch['name']
        under = [j for i in sch['properties'].values() for j in all_names(prefix, i)]
        return [prefix] + under

    if sch['type'] == 'array':
        return [j for j in all_names(prefix, sch['items'])]


def header_has_clear(env, name, o):
    'Generate declarations of hasFoo() clearFoo() methods plus hasFoo_ member'

    o('\n')
    o('public:\n')
    o('  bool has{}() const{};\n'.format(title(name), env['noexcept']))
    o('  void clear{}(){};\n'.format(title(name), env['noexcept']))
    o('private:\n')
    o('  bool has{}_;\n'.format(title(name)))


def source_has_clear(env, mem_name, class_name, o):
    'Generate definition of hasFoo() clearFoo() methods'

    o('\n')
    o('bool {}::has{}() const{}\n'.format(title(class_name), title(mem_name), env['noexcept']))
    o('{\n')
    o('  return has{}_;\n'.format(title(mem_name)))
    o('}\n')

    o('\n')
    o('void {}::clear{}(){}\n'.format(title(class_name), title(mem_name), env['noexcept']))
    o('{\n')
    o('  has{}_ = false;\n'.format(title(mem_name)))
    o('}\n')


def header_default(env, name, schema, o):
    'Generate declaration of defaultFoo() method if property have default value'

    if not 'default' in schema:
        return

    if schema['generator'] == 'boolean':
        default_value = 'true' if schema['default'] else 'false'
    else:
        default_value = schema['default']

    o('\n')
    o('public:\n')

    if schema['generator'] == 'string':
        o('  static constexpr const char* default{}(){} {{ return "{}"; }}\n'\
            .format(title(name), env['noexcept'], default_value))
        return

    o('  static constexpr {} default{}(){} {{ return {}; }}\n'\
        .format(schema['arg_type'], title(name), env['noexcept'], default_value))


def header_primitive(env, name, schema, o):
    'Generate declarations for primitive type'
    oo = indent(o)
    ooo = indent(oo)

    o('\n')
    o('public:\n')
    oo('{0} {1}() const;\n'.format(schema['arg_type'], name))
    oo('void set{0}({1} new{0}){2}\n'
        .format(title(name), schema['arg_type'], '' if env['noexcept'] else ';'))
    if env['noexcept']:
        ooo('noexcept(std::is_nothrow_copy_constructible<{}>::value);\n'.format(schema['sto_type']))
    o('private:\n')
    oo('{0} {1}_;\n'.format(schema['sto_type'], name))

    header_has_clear(env, name, o)

    header_default(env, name, schema, o)


def source_primitive(env, mem_name, class_name, schema, o):
    'Generate definitions for primitive type'
    oo = indent(o)
    ooo = indent(oo)

    o('\n')
    o('{} {}::{}() const\n'.format(schema['arg_type'], class_name, mem_name))
    o('{\n')
    oo('if (!has{}_) {{\n'.format(title(mem_name)))
    ooo('JCPPY_THROW(std::runtime_error("Member \\"{}\\" is not set"));\n'.format(mem_name))
    oo('}\n')
    oo('return {}_;\n'.format(mem_name))
    o('}\n')

    o('\n')
    o('void {0}::set{1}({2} new{1})\n'.format(class_name, title(mem_name), schema['arg_type']))
    if env['noexcept']:
        oo('noexcept(std::is_nothrow_copy_constructible<{}>::value)\n'.format(schema['sto_type']))
    o('{\n')
    oo('{0}_ = new{1};\n'.format(mem_name, title(mem_name)))
    oo('has{}_ = true;\n'.format(title(mem_name)))
    o('}\n')

    source_has_clear(env, mem_name, class_name, o)


def header_movable(env, name, schema, o):
    'Generate declarations for movable type'
    oo = indent(o)

    arg_type = schema['arg_type']
    sto_type = schema['sto_type']

    o('\n')
    o('public:\n')
    oo('{} {}() const{};\n'.format(arg_type, name, env['noexcept']))
    oo('void set{0}({1} new{0});\n'.format(title(name), arg_type))
    oo('void set{0}({1}&& new{0}){2};\n'.format(title(name), sto_type, env['noexcept']))

    header_has_clear(env, name, o)

    o('\n')
    o('public:\n')
    o('  {}* mutable{}(){};\n'.format(sto_type, title(name), env['noexcept']))

    o('\n')
    o('private:\n')
    o('  {0} {1}_;\n'.format(sto_type, name))

    header_default(env, name, schema, o)


def source_movable(env, mem_name, class_name, schema, o):
    'Generate definitions for movable type'
    oo = indent(o)
    ooo = indent(oo)

    arg_type = schema['arg_type']
    sto_type = schema['sto_type']

    o('\n')
    o('{} {}::{}() const{}\n'.format(arg_type, class_name, mem_name, env['noexcept']))
    o('{\n')
    oo('if (!has{}_) {{\n'.format(title(mem_name)))
    ooo('JCPPY_THROW(std::runtime_error("Member \\"{}\\" is not set"));\n'.format(mem_name))
    oo('}\n')
    oo('return {}_;\n'.format(mem_name))
    o('}\n')

    o('\n')
    o('void {0}::set{1}({2} new{1})\n'.format(class_name, title(mem_name), arg_type))
    o('{\n')
    oo('{0}_ = new{1};\n'.format(mem_name, title(mem_name)))
    oo('has{}_ = true;\n'.format(title(mem_name)))
    o('}\n')

    o('\n')
    o('void {0}::set{1}({2}&& new{1}){3}\n'
        .format(class_name, title(mem_name), sto_type, env['noexcept']))
    o('{\n')
    oo('{0}_ = std::move(new{1});\n'.format(mem_name, title(mem_name)))
    oo('has{}_ = true;\n'.format(title(mem_name)))
    o('}\n')

    source_has_clear(env, mem_name, class_name, o)

    o('\n')
    o('{}* {}::mutable{}(){}\n'
        .format(sto_type, title(class_name), title(mem_name), env['noexcept']))
    o('{\n')
    oo('has{}_ = true;\n'.format(title(mem_name)))
    oo('return &{}_;\n'.format(mem_name))
    o('}\n')


def header_base64(env, name, _, o):
    'Generate declarations for base64 type'
    oo = indent(o)

    o('\n')
    o('public:\n')
    oo('const std::vector<char>& {}() const{};\n'.format(name, env['noexcept']))
    oo('void set{0}(const std::vector<char>& new{0});\n'.format(title(name)))
    oo('void set{0}(std::vector<char>&& new{0}){1};\n'.format(title(name), env['noexcept']))
    oo('std::vector<char>* mutable{}(){};\n'.format(title(name), env['noexcept']))
    header_has_clear(env, name, o)
    o('private:\n')
    oo('std::vector<char> {}_;\n'.format(name))


def source_base64(env, mem_name, class_name, _, o):
    'Generate definitions for base64 type'
    oo = indent(o)

    o('const std::vector<char>& {}::{}() const{}\n'.format(class_name, mem_name, env['noexcept']))
    o('{\n')
    oo('return {}_;\n'.format(mem_name))
    o('}\n')

    o('\n')
    o('void {0}::set{1}(const std::vector<char>& new{1})\n'.format(class_name, title(mem_name)))
    o('{\n')
    oo('{0}_ = new{1};\n'.format(mem_name, title(mem_name)))
    oo('has{}_ = true;\n'.format(title(mem_name)))
    o('}\n')

    o('\n')
    o('void {0}::set{1}(std::vector<char>&& new{1}){2}\n'
        .format(class_name, title(mem_name), env['noexcept']))
    o('{\n')
    oo('{0}_ = std::move(new{1});\n'.format(mem_name, title(mem_name)))
    oo('has{}_ = true;\n'.format(title(mem_name)))
    o('}\n')

    o('\n')
    o('std::vector<char>* {}::mutable{}(){}\n'.format(class_name, title(mem_name), env['noexcept']))
    o('{\n')
    oo('has{}_ = true;\n'.format(title(mem_name)))
    oo('return &{}_;\n'.format(mem_name))
    o('}\n')

    source_has_clear(env, mem_name, class_name, o)


def header_object(env, _, schema, o):
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
        if not schema['generator'] in HEADER_GENERATORS:
            raise Exception('unsupported type "{}"'.format(schema['generator']))
        o('\n')
        o('//' + '-' * 77 + '\n')
        o('// Methods and fields related to field "{}"\n'.format(name))
        o('//   Type     : {}\n'.format(schema['type']))
        o('//   Format   : {}\n'.format(schema.get('format', None)))
        o('//' + '-' * 77 + '\n')

        HEADER_GENERATORS[schema['generator']](env, name, schema, o)

    o('};\n')


def header_nested_object(env, name, schema, o):
    'Generate declarations for any object type excluding root object'

    o('\n')
    o('public:')
    header_object(env, None, schema, indent(o))

    header_movable(env, name, schema, o)


def write_json_any(name, schema, o):
    'Generate body of `writeJson\' method'
    oo = indent(o)

    if schema['generator'] == 'object':
        o('{}.writeJson(writer);\n'.format(name))

    elif schema['generator'] == 'array':
        o('writer->StartArray();\n')
        o('for (const auto& i : {}) {{\n'.format(name))
        write_json_any('i'.format(name), schema['items'], oo)
        o('}\n')
        o('writer->EndArray();\n')

    elif schema['generator'] == 'boolean':
        o('writer->Bool({});\n'.format(name))

    elif schema['generator'] == 'string':
        oo('writer->String({0}.c_str(), {0}.length());\n'.format(name))

    elif schema['generator'] == 'base64':
        o('{\n')
        oo('auto tmp = ::base64({});\n'.format(name))
        oo('writer->String(tmp.c_str(), tmp.length());\n')
        o('}\n')

    elif schema['generator'] == 'date-time':
        o('{\n')
        oo('auto tmp = boost::posix_time::to_iso_extended_string({});\n'.format(name))
        oo('writer->String(tmp.c_str(), tmp.length());\n')
        o('}\n')

    elif schema['generator'] == 'number':
        o('writer->Double({});\n'.format(name))

    elif schema['generator'] == 'integer':
        o('writer->Int({});\n'.format(name))

    elif schema['generator'] == 'utc-millisec':
        o('writer->Int64({});\n'.format(name))

    elif schema['generator'] == 'uuid':
        o('{\n')
        oo('auto tmp = boost::uuids::to_string({});\n'.format(name))
        oo('writer->String(tmp.c_str(), tmp.length());\n')
        o('}\n')
    else:
        raise Exception('unknown generator "' + schema['generator'] + '"')


def write_json_object(name, schema, o):
    'Generate implementation of `writeJson\' method'

    oo = indent(o)

    o('Writer* writer = static_cast<Writer*>(writerr);\n')
    o('\n')
    o('writer->StartObject();\n')
    for name, s in schema['properties'].items():
        o('\n')
        o('if (has{}_) {{\n'.format(title(name)))
        oo('writer->String(\"{}\");\n'.format(name))
        write_json_any('{}_'.format(name), s, oo)
        o('}\n')
    o('\n')
    o('writer->EndObject();\n')


def read_json_any(obj, name, schema, o):
    'Generate implementation of `readJson\' method'
    oo = indent(o)

    json_type = {
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

    o('if (!{}.Is{}()) {{\n'.format(obj, json_type[schema['generator']]))
    oo('JCPPY_THROW(std::runtime_error("Json type mismatch for member \\"{}\\""));\n'.format(name))
    o('}\n')


    if schema['generator'] == 'object':
        o('{} tmp;\n'.format(schema['sto_type'], name))
        o('JcppyHelper::readDocument(tmp, &{});\n'.format(obj))
        o('{} = std::move(tmp);\n'.format(name))

    elif schema['generator'] == 'array':
        o('{}.resize({}.Size());\n'.format(name, obj))
        o('for (std::size_t i = 0; i < {}.Size(); ++i) {{\n'.format(obj))
        read_json_any('{}[i]'.format(obj), '{}[i]'.format(name), schema['items'], oo)
        o('}\n')

    elif schema['generator'] in ['number', 'integer', 'utc-millisec', 'boolean']:
        o('{} = {}.Get{}();\n'.format(name, obj, json_type[schema['generator']]))

    elif schema['generator'] == 'string':
        o('{0}.assign({1}.GetString(), {1}.GetStringLength());\n'.format(name, obj))

    elif schema['generator'] == 'base64':
        o('{0} = ::fromBase64({1}.GetString(), {1}.GetStringLength());\n'.format(name, obj))

    elif schema['generator'] == 'date-time':
        o('std::string tmp({0}.GetString(), {0}.GetStringLength());\n'.format(obj))
        o('{} = boost::posix_time::time_from_string(std::move(tmp));\n'.format(name))

    elif schema['generator'] == 'uuid':
        o('boost::uuids::string_generator gen;\n')
        o('{0} = gen({1}.GetString(), {1}.GetString() + {1}.GetStringLength());\n'
            .format(name, obj))

    else:
        raise Exception('unknown generator "' + schema['generator'] + '"')


def read_json_object(name, schema, o):
    'Generate implementation of readJson() method'
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
        read_json_any('ivalue', '{}_'.format(name), s, ooo)
        ooo('has{}_ = true;\n'.format(title(name)))
        ooo('continue;\n')
        oo('}\n')
    o('}\n')
    o('ensureInitialized();\n')


def source_populate_defaults(schema, o):
    'Generate `populate_defaults\' method'

    class_name = schema['name']
    oo = indent(o)
    ooo = indent(oo)
    oooo = indent(ooo)

    o('\n')
    o('bool {}::populateDefaults()\n'.format(class_name))
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
            ooo('}\n')
        oo('}\n')
    oo('return res;\n')
    o('}\n')


def source_object(env, schema, o):
    'Generate definitions for root type'

    class_name = schema['name']
    oo = indent(o)
    ooo = indent(oo)
    spec = {
        'class': class_name
    }

    o('\n')
    o('{0}::{0}(){1}\n'.format(class_name, env['noexcept']))
    if env['delegatingCtors']:
        oo(': ')
        o('\n  , '.join(['has{}_(false)'.format(title(i)) for i in schema['properties'].keys()]))
        o('\n')
    o('{\n')
    if not env['delegatingCtors']:
        oo('clear();\n')
    o('}\n')

    if env['delegatingCtors']:
        snippet(env, o, 'ctor_stream.inl', spec)
        snippet(env, o, 'ctor_string.inl', spec)
    else:
        snippet(env, o, 'no_delegating_ctor_stream.inl', spec)
        snippet(env, o, 'no_delegating_ctor_string.inl', spec)

    snippet(env, o, 'json.inl', spec)
    snippet(env, o, 'write_json.inl', spec)

    o('\n')
    o('void {}::writeJson(void* writerr) const\n'.format(class_name))
    o('{\n')
    oo('ensureInitialized();\n')
    write_json_object(None, schema, oo)
    o('}\n')

    snippet(env, o, 'from_json.inl', spec)
    snippet(env, o, 'read_json.inl', spec)

    o('\n')
    o('void {}::readDocument(void* document)\n'.format(class_name))
    o('{\n')
    oo('clear();\n')
    oo('\n')
    read_json_object(None, schema, oo)
    o('}\n')

    o('\n')
    o('void {}::ensureInitialized() const\n'.format(class_name))
    o('{')
    for i in schema.get('required', []):
        oo('\n')
        oo('if (!has{}_) {{\n'.format(title(i)))
        ooo('JCPPY_THROW(std::runtime_error("Member \\"{}\\" is not initialized"));\n'.format(i))
        oo('}\n')
    o('}\n')

    source_populate_defaults(schema, o)

    o('\n')
    o('void {}::clear()\n'.format(class_name))
    o('{\n')
    for name, s in schema['properties'].items():
        oo('has{}_ = false;\n'.format(title(name)))
        if s['generator'] in ['array', 'object']:
            oo('{}_.clear();\n'.format(name))
    o('}\n')

    for name, s in schema['properties'].items():
        if not s['type'] in SOURCE_GENERATORS:
            raise Exception('unsupported type "{}"'.format(s['type']))
        SOURCE_GENERATORS[s['generator']](env, name, class_name, s, o)


def source_nested_object(env, mem_name, class_name, schema, o):
    'Generate definitions for any object type excluding root object'

    source_object(env, schema, o)
    source_movable(env, mem_name, class_name, schema, o)


def header_array(env, name, schema, o):
    'Generate declarations for array type'

    if schema['items']['type'] == 'object':
        o('\n')
        o('public:')
        header_object(env, None, schema['items'], indent(o))

    o('\n')
    header_movable(env, name, schema, o)


def source_array(env, mem_name, class_name, schema, o):
    'Generate definitions for array type'

    if schema['items']['type'] == 'object':
        source_object(env, schema['items'], o)

    o('\n')
    source_movable(env, mem_name, class_name, schema, o)


HEADER_GENERATORS = {
    'boolean': header_primitive,
    'string': header_movable,
    'integer': header_primitive,
    'number': header_primitive,
    'date-time': header_primitive,
    'utc-millisec': header_primitive,
    'uuid': header_primitive,
    'base64': header_base64,
    'object': header_nested_object,
    'array': header_array
}

SOURCE_GENERATORS = {
    'boolean': source_primitive,
    'string': source_movable,
    'integer': source_primitive,
    'number': source_primitive,
    'date-time': source_primitive,
    'utc-millisec': source_primitive,
    'uuid': source_primitive,
    'base64': source_base64,
    'object': source_nested_object,
    'array': source_array
}


def header(env, schema, o):
    'Generate header for type described by `schema\''

    if schema['type'] != 'object':
        raise Exception('jcppy can generate cpp classes only for objects')

    o('/// @file Generated by jcppy\n')
    o('/// @warning Do not edit!\n')
    o('\n')
    o('#pragma once\n')
    o('#include <string>\n')
    o('#include <vector>\n')
    o('#include <type_traits>\n')

    has_date_time = env['useBoostDateTime']
    has_uuid = env['useBoostUuid']
    has_cstdint = env['useBoostCstdint']

    if has_uuid:
        o('#include <boost/uuid/uuid.hpp>\n')
        o('#include <boost/uuid/uuid_io.hpp>\n')

    if has_date_time:
        o('#include <boost/date_time/posix_time/posix_time_types.hpp>\n')

    if has_cstdint:
        o('#include <boost/cstdint.hpp>\n')

    if has_uuid or has_date_time or has_cstdint:
        o('\n')
        o('namespace jcppy {\n')
        o('\n')
        if has_uuid:
            o('typedef boost::uuids::uuid uuid;\n')
        if has_date_time:
            o('typedef boost::posix_time::ptime date_time;\n')
        if has_cstdint:
            o('typedef boost::uint64_t uint64_t;\n')
        o('\n')
        o('} // namespace jcppy\n')

    o('\n')
    o('\n'.join(['namespace {} {{'.format(i) for i in env['namespace'].split('::')]) + '\n')

    o('\n')
    o('class JcppyHelper;\n')

    header_object(env, None, schema, o)

    o('\n')
    o('}' * len(env['namespace'].split('::')) + ' // namespace {}\n'.format(env['namespace']))


def source(env, schema, o):
    'Generate source file for entire schema'

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
    o('#include <rapidjson/error/en.h>\n')

    o('#include "{}"\n'.format(env['header']))

    o('\n')
    o('namespace {\n')

    snippet(env, o, 'ostream_wrapper.inl')
    snippet(env, o, 'istream_wrapper.inl')

    if env['useBase64']:
        snippet(env, o, 'base64.inl')
        snippet(env, o, 'from_base64.inl')

    o('\n')
    o('} // anonymous namespace\n')

    o('\n')
    o('\n'.join(['namespace {} {{'.format(i) for i in env['namespace'].split('::')]) + '\n')
    snippet(env, o, 'jcppy_helper.inl')
    o('\n')
    o('}' * len(env['namespace'].split('::')) + ' // namespace {}\n'.format(env['namespace']))

    o('\n')
    o('typedef rapidjson::Writer<::OStreamWrapper> Writer;\n')
    o('typedef rapidjson::Document Document;\n')
    for i in all_names('', schema):
        o('typedef {}::{} {};\n'.format(env['namespace'], i, i.split('::')[-1]))

    o('\n')
    if env['useBoostThrowException']:
        o('#define JCPPY_THROW(x) BOOST_THROW_EXCEPTION(x)\n')
    else:
        o('#define JCPPY_THROW(x) throw x\n')

    source_object(env, schema, o)


def main():
    'jcppy entry point'
    parser = argparse.ArgumentParser(
        description='Generate c++ classes from the given json-schema'
        , prog='jcppy'
        , formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('files'
        , metavar='file'
        , type=unicode
        , nargs='+'
        , help='json-schema files to process')
    parser.add_argument('-n', '--namespace'
        , metavar='<namespace>'
        , type=unicode
        , default='gen'
        , help='namespace to place generated classes in. '
            'May be of format "foo::bar"')
    parser.add_argument('-o', '--output-dir'
        , metavar='<directory>'
        , type=unicode
        , default=argparse.SUPPRESS
        , help='directory to store generated files to')
    parser.add_argument('-s', '--snippet-dir'
        , metavar='<directory>'
        , type=unicode
        , default=os.path.realpath(
            os.path.join(os.path.dirname(__file__), '../share/jcppy/snippet'))
        , help='directory with code snippets used by %(prog)s.')
    parser.add_argument('--noexcept'
        , help='generate noexcept specifiers'
        , default=False
        , action='store_true')
    parser.add_argument('--boost-throw-exception'
        , help='use BOOST_THROW_EXCEPTION macro instead of throw()'
        , default=True
        , action='store_true')
    parser.add_argument('--delegating-constructors'
        , help='use c++11 delegating constructors in generated code'
        , default=False
        , action='store_true')
    parser.add_argument('--verbose'
        , help='print debug messages'
        , default=False
        , action='store_true')
    parser.add_argument('-v', '--version'
        , help='print version'
        , action='version'
        , version='%(prog)s {}'.format(JCPPY_VERSION))

    args = parser.parse_args()
    for i in args.files:
        header_file = os.path.basename(i[:i.rfind('.')]) + '.h'
        source_file = os.path.basename(i[:i.rfind('.')]) + '.cpp'
        if not args.output_dir is None:
            header_file = os.path.join(args.output_dir, header_file)
            source_file = os.path.join(args.output_dir, source_file)
        env = {
            'version': JCPPY_VERSION,
            'namespace' : args.namespace,
            'header' : header_file,
            'source' : source_file,
            'verbose' : args.verbose,
            'useBoostUuid' : False,
            'useBoostDateTime' : False,
            'useBoostCstdint' : False,
            'useBase64': False,
            'useBoostThrowException' : args.boost_throw_exception,
            'noexcept': ' noexcept' if args.noexcept else '',
            'delegatingCtors': args.delegating_constructors,
            'snippet_dir': args.snippet_dir
        }
        with open(i) as schema_fo\
            , codecs.open(header_file, 'w', 'utf-8') as header_fo\
            , codecs.open(source_file, 'w', 'utf-8') as source_fo:
            schema = json.loads(schema_fo.read())
            schema = resolve_cpp_types(env, schema, first_pass=True)
            schema = resolve_cpp_types(env, schema, first_pass=False)
            if env['verbose']:
                debug(schema)
            header(env, schema, header_fo.write)
            source(env, schema, source_fo.write)
    return 0

if __name__ == '__main__':
    sys.exit(main())
