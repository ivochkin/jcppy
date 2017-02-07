{% import "property_write.cpp" as property_write %}

const std::size_t {{Name}}Writer::npos = (std::size_t) -1;

{{Name}}Writer::{{Name}}Writer(const {{Name}}* object)
  : object_(object)
{% if properties %}
  , nextProperty_(0)
  , firstPropertyWritten_(false)
  , offset_(0)
{% endif %}
{
}

std::size_t {{Name}}Writer::write(char* buffer, std::size_t count, bool throwOnError)
{
  {% if properties %}
  if (!count) {
    error_ = {{NAME}}_WRITER_BUFFER_TOO_SMALL;
    if (throwOnError) {
      throw std::runtime_error(errorMessage());
    }
    return npos;
  }
  char* original_buffer = buffer;
  char* buffer_end = buffer + count;
  switch (nextProperty_) {
  {% for p in properties %}
    case {{ loop.index0 }}: { /* {{ p["name"] }} */
      {% if p["optional"] %}
      if (object_->has{{ p["Name"] }}()) {
      {% endif %}
      {% if p["type"] == "integer" %}
      {{ property_write.snprintf(p, "%\" PRId64 \"") | indent(6) }}
      {% elif p["type"] == "number" %}
      {{ property_write.snprintf(p, "%lf") | indent(6) }}
      {% elif p["type"] == "boolean" %}
      {{ property_write.snprintf(p, "%s", " ? \"true\" : \"false\"") | indent(6) }}
      {% elif p["type"] == "string" %}
      {{ property_write.string(NAME, p) | indent(6) }}
      {% endif %}
      {% if p["optional"] %}
      }
      {% endif %}
      nextProperty_++;
    }
  {% endfor %}
    case {{ properties | length }}: /* finalize */ {
      if (buffer_end - buffer) {
        *buffer++ = '}';
      }
      nextProperty_++;
      break;
    }
    case {{ (properties | length ) + 1}}: /* done */ {
      return 0;
    }
    default:
      error_ = {{ NAME }}_WRITER_UNEXPECTED_ERROR;
      if (throwOnError) {
        throw std::runtime_error(errorMessage());
      }
      return npos;
  }
  return buffer - original_buffer;
  {% else %}
  error_ = {{NAME}}_WRITER_UNEXPECTED_ERROR;
  return npos;
  {% endif %}
}

std::size_t {{Name}}Writer::bufferSizeHint() const
{
  return 4096;
}

int {{Name}}Writer::error() const
{
  return error_;
}

const char* {{Name}}Writer::errorMessage() const
{
  switch(error_) {
    case {{NAME}}_WRITER_OK: return "No error";
    case {{NAME}}_WRITER_UNEXPECTED_ERROR: return "Unexpected error. Please report it to the author";
    case {{NAME}}_WRITER_BUFFER_TOO_SMALL: return "Buffer too small";
    default: return "Unknown error";
  };
  return "Unknown error";
}


std::ostream& operator<<(std::ostream& os, const {{Name}}& obj)
{
  obj.writeJson(os);
  return os;
}


