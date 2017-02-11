#define STATIC_ASSERT(expression, name) \
  typedef char assert_ ##name[(expression) ? 1 : -1];

enum {{Name}}ReaderState
{
  {{NAME}}_READER_INIT = 0,
  {{NAME}}_READER_DONE,
  {{NAME}}_READER_NEAR_PROPERTY_NAME,
  {{NAME}}_READER_PROPERTY_NAME,
  {{NAME}}_READER_PROPERTY_VALUE,
  {{NAME}}_READER_STRING_VALUE,
  {{NAME}}_READER_ARRAY_ELEMENT,
  {{NAME}}_READER_STRING_ARRAY_ELEMENT,
};

class {{Name}}ReaderAccess
{
public:
  static void setError({{Name}}Reader* reader, {{Name}}Reader::Error error)
  {
    reader->error_ = error;
  }

  static void setErrorPosition({{Name}}Reader* reader, const char* position)
  {
    reader->errorPosition_ = position;
  }

  static {{Name}}ReaderState state({{Name}}Reader* reader)
  {
    return static_cast<{{Name}}ReaderState>(reader->state_);
  }

  static void setState({{Name}}Reader* reader, {{Name}}ReaderState state)
  {
    reader->state_ = state;
  }

  static std::list<std::size_t>* mutablePossibleProperties({{Name}}Reader* reader)
  {
    return &reader->possibleProperties_;
  }

  static std::size_t propertyNameOffset({{Name}}Reader* reader)
  {
    return reader->propertyNameOffset_;
  }

  static std::size_t* mutablePropertyNameOffset({{Name}}Reader* reader)
  {
    return &reader->propertyNameOffset_;
  }

  static {{Name}}* mutableInstance({{Name}}Reader* reader)
  {
    return &reader->instance_;
  }
};

{{Name}}Reader::{{Name}}Reader()
  : error_({{NAME}}_READER_OK)
  , errorPosition_(NULL)
  , state_({{NAME}}_READER_INIT)
{
  STATIC_ASSERT(sizeof(parser_) >= sizeof(embedjson_parser),
      enough_room_for_embedjson_parser);
  std::memset(parser_, 0, sizeof(parser_));
}

std::size_t {{Name}}Reader::read(std::istream& stream, std::size_t count,
    bool throwOnError)
{
  std::size_t totalRead = 0;
  for (; stream.good() && totalRead < count; ++totalRead) {
    char c;
    stream.read(&c, 1);
    std::size_t nread = stream.gcount();
    if (stream.bad() || !nread) {
      error_ = {{NAME}}_READER_IO_ERROR;
      if (throwOnError) {
        throw std::runtime_error(errorMessage());
      }
      return totalRead;
    }
    readByte(c);
    if (error_) {
      if (throwOnError) {
        throw std::runtime_error(errorMessage());
      }
      return totalRead;
    }
  }
  return totalRead;
}

std::size_t {{Name}}Reader::read(const char* buf, std::size_t count,
    bool throwOnError)
{
  for (const char* end = buf + count, *i = buf; i != end; ++i) {
    readByte(*i);
    if (error_) {
      if (throwOnError) {
        throw std::runtime_error(errorMessage());
      }
      return i - buf;
    }
  }
  return count;
}

const {{Name}}& {{Name}}Reader::instance() const
{
  return instance_;
}

{{Name}}* {{Name}}Reader::mutableInstance()
{
  return &instance_;
}

void {{Name}}Reader::readByte(char value)
{
  embedjson_push(reinterpret_cast<embedjson_parser*>(parser_), &value, 1);
}

{{Name}}Reader::Error {{Name}}Reader::error() const
{
  return error_;
}

const char* {{Name}}Reader::errorMessage() const
{
  switch(error_) {
    case {{NAME}}_READER_OK: return "No error";
    case {{NAME}}_READER_PARSE_ERROR: return "Parse error";
    case {{NAME}}_READER_IO_ERROR: return "IO error";
    default: return "Unknown error";
  };
  return "Unknown error";
}

int embedjson_error(embedjson_parser* parser, const char* position)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  {{Name}}ReaderAccess::setError(reader, {{Name}}Reader::{{NAME}}_READER_PARSE_ERROR);
  {{Name}}ReaderAccess::setErrorPosition(reader, position);
  return 1;
}

int embedjson_null(embedjson_parser* parser)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  {{Name}}ReaderAccess::setState(reader, {{NAME}}_READER_NEAR_PROPERTY_NAME);
  return 0;
}

int embedjson_bool(embedjson_parser* parser, char value)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  {{Name}}ReaderAccess::setState(reader, {{NAME}}_READER_NEAR_PROPERTY_NAME);
  return 0;
}

int embedjson_int(embedjson_parser* parser, int64_t value)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  switch ({{Name}}ReaderAccess::state(reader)) {
    case {{NAME}}_READER_INIT:
    case {{NAME}}_READER_DONE:
    case {{NAME}}_READER_NEAR_PROPERTY_NAME:
    case {{NAME}}_READER_PROPERTY_NAME:
      break;
    case {{NAME}}_READER_PROPERTY_VALUE: {
      std::list<std::size_t>* possibleProperties =
        {{Name}}ReaderAccess::mutablePossibleProperties(reader);
      std::size_t nproperty = possibleProperties->front();
      switch (nproperty) {
      {% for p in properties %}
        case {{loop.index0}}: // {{p.name}}
          {% if p.type == "integer" %}
          {{Name}}ReaderAccess::mutableInstance(reader)->set{{p.Name}}(value);
          {% endif %}
          break;
      {% endfor %}
      }
      {{Name}}ReaderAccess::setState(reader, {{NAME}}_READER_NEAR_PROPERTY_NAME);
      break;
    }
    case {{NAME}}_READER_STRING_VALUE:
    case {{NAME}}_READER_ARRAY_ELEMENT:
    case {{NAME}}_READER_STRING_ARRAY_ELEMENT:
      break;
  }
  return 0;
}

int embedjson_double(embedjson_parser* parser, double value)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  switch ({{Name}}ReaderAccess::state(reader)) {
    case {{NAME}}_READER_INIT:
    case {{NAME}}_READER_DONE:
    case {{NAME}}_READER_NEAR_PROPERTY_NAME:
    case {{NAME}}_READER_PROPERTY_NAME:
      break;
    case {{NAME}}_READER_PROPERTY_VALUE: {
      std::list<std::size_t>* possibleProperties =
        {{Name}}ReaderAccess::mutablePossibleProperties(reader);
      std::size_t nproperty = possibleProperties->front();
      switch (nproperty) {
      {% for p in properties %}
        case {{loop.index0}}: // {{p.name}}
          {% if p.type == "number" %}
          {{Name}}ReaderAccess::mutableInstance(reader)->set{{p.Name}}(value);
          {% endif %}
          break;
      {% endfor %}
      }
      {{Name}}ReaderAccess::setState(reader, {{NAME}}_READER_NEAR_PROPERTY_NAME);
      break;
    }
    case {{NAME}}_READER_STRING_VALUE:
    case {{NAME}}_READER_ARRAY_ELEMENT:
    case {{NAME}}_READER_STRING_ARRAY_ELEMENT:
      break;
  }
  return 0;
}

int embedjson_string_begin(embedjson_parser* parser)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  switch ({{Name}}ReaderAccess::state(reader)) {
    case {{NAME}}_READER_INIT:
    case {{NAME}}_READER_DONE:
      break;
    case {{NAME}}_READER_NEAR_PROPERTY_NAME: {
      {{Name}}ReaderAccess::setState(reader, {{NAME}}_READER_PROPERTY_NAME);
      {% if properties %}
      std::list<std::size_t>* possibleProperties =
          {{Name}}ReaderAccess::mutablePossibleProperties(reader);
      possibleProperties->clear();
      {% for p in properties %}
      possibleProperties->push_back({{loop.index0}}); // {{p.name}}
      {% endfor %}
      *{{Name}}ReaderAccess::mutablePropertyNameOffset(reader) = 0;
      {% endif %}
      break;
    }
    case {{NAME}}_READER_PROPERTY_NAME:
      break;
    case {{NAME}}_READER_PROPERTY_VALUE: {
      std::list<std::size_t>* possibleProperties =
        {{Name}}ReaderAccess::mutablePossibleProperties(reader);
      std::size_t nproperty = possibleProperties->front();
      switch (nproperty) {
      {% for p in properties %}
        case {{loop.index0}}: // {{p.name}}
          {% if p.type == "string" %}
          {{Name}}ReaderAccess::mutableInstance(reader)->mutable{{p.Name}}()->clear();
          {% endif %}
          break;
      {% endfor %}
      }
      {{Name}}ReaderAccess::setState(reader, {{NAME}}_READER_STRING_VALUE);
      break;
    }
    case {{NAME}}_READER_STRING_VALUE:
    case {{NAME}}_READER_ARRAY_ELEMENT:
    case {{NAME}}_READER_STRING_ARRAY_ELEMENT:
      break;
  }
  return 0;
}

int embedjson_string_chunk(embedjson_parser* parser,
    const char* data, size_t size)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  switch ({{Name}}ReaderAccess::state(reader)) {
    case {{NAME}}_READER_INIT:
    case {{NAME}}_READER_DONE:
    case {{NAME}}_READER_NEAR_PROPERTY_NAME:
    case {{NAME}}_READER_PROPERTY_NAME: {
      std::list<std::size_t>* possibleProperties =
        {{Name}}ReaderAccess::mutablePossibleProperties(reader);
      std::size_t propertyNameOffset = {{Name}}ReaderAccess::propertyNameOffset(reader);
      for (std::list<std::size_t>::iterator it = possibleProperties->begin();
          it != possibleProperties->end();) {
        switch (*it) {
          {% for p in properties %}
          case {{loop.index0}}: // {{p.name}}
            if (std::memcmp("{{p.name}}" + propertyNameOffset, data, size)) {
              it = possibleProperties->erase(it);
            } else {
              ++it;
            }
            break;
          {% endfor %}
        }
      }
      if (possibleProperties->empty()) {
        return 1;
      }
      *{{Name}}ReaderAccess::mutablePropertyNameOffset(reader) += size;
      break;
    }
    case {{NAME}}_READER_PROPERTY_VALUE:
      break;
    case {{NAME}}_READER_STRING_VALUE: {
      std::list<std::size_t>* possibleProperties =
        {{Name}}ReaderAccess::mutablePossibleProperties(reader);
      std::size_t nproperty = possibleProperties->front();
      switch (nproperty) {
      {% for p in properties %}
        case {{loop.index0}}: // {{p.name}}
          {% if p.type == "string" %}
          {{Name}}ReaderAccess::mutableInstance(reader)->mutable{{p.Name}}()->append(data, size);
          {% endif %}
          break;
      {% endfor %}
      }
      break;
    }
    case {{NAME}}_READER_ARRAY_ELEMENT:
    case {{NAME}}_READER_STRING_ARRAY_ELEMENT:
      break;
  }
  return 0;
}

int embedjson_string_end(embedjson_parser* parser)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  switch ({{Name}}ReaderAccess::state(reader)) {
    case {{NAME}}_READER_INIT:
    case {{NAME}}_READER_DONE:
    case {{NAME}}_READER_NEAR_PROPERTY_NAME:
      break;
    case {{NAME}}_READER_PROPERTY_NAME:
      {{Name}}ReaderAccess::setState(reader, {{NAME}}_READER_PROPERTY_VALUE);
      break;
    case {{NAME}}_READER_PROPERTY_VALUE:
    case {{NAME}}_READER_STRING_VALUE:
      {{Name}}ReaderAccess::setState(reader, {{NAME}}_READER_NEAR_PROPERTY_NAME);
      break;
    case {{NAME}}_READER_ARRAY_ELEMENT:
    case {{NAME}}_READER_STRING_ARRAY_ELEMENT:
      break;
  }
  return 0;
}

int embedjson_object_begin(embedjson_parser* parser)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  switch ({{Name}}ReaderAccess::state(reader)) {
    case {{NAME}}_READER_INIT:
      {{Name}}ReaderAccess::setState(reader, {{NAME}}_READER_NEAR_PROPERTY_NAME);
      break;
    case {{NAME}}_READER_DONE:
    case {{NAME}}_READER_NEAR_PROPERTY_NAME:
    case {{NAME}}_READER_PROPERTY_NAME:
    case {{NAME}}_READER_PROPERTY_VALUE:
    case {{NAME}}_READER_STRING_VALUE:
    case {{NAME}}_READER_ARRAY_ELEMENT:
    case {{NAME}}_READER_STRING_ARRAY_ELEMENT:
      break;
  }
  return 0;
}

int embedjson_object_end(embedjson_parser* parser)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  {{Name}}ReaderAccess::setState(reader, {{NAME}}_READER_DONE);
  return 0;
}

int embedjson_array_begin(embedjson_parser* parser)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  return 0;
}

int embedjson_array_end(embedjson_parser* parser)
{
  {{Name}}Reader* reader = reinterpret_cast<{{Name}}Reader*>(parser);
  return 0;
}
