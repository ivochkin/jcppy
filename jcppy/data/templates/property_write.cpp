{%- macro leading_snprintf_fmt(p) -%}
  {%- if p["first_in_json"] -%}
    {%- raw -%}
    {
    {%- endraw -%}
  {%- elif p["can_be_first_in_json"] -%}
    %c
  {%- else -%}
    ,
  {%- endif -%}
{%- endmacro -%}

{%- macro leading_snprintf_val(p, suffix) -%}
  {%- if p["can_be_first_in_json"] -%}
  firstPropertyWritten_ ? ',' : '{'{{ suffix }}
  {%- endif -%}
{%- endmacro -%}

{%- macro snprintf(p, format, getter_extra="") -%}
int nwritten = snprintf(buffer, buffer_end - buffer,
    "{{ leading_snprintf_fmt(p) }}\"{{ p["name"] }}\":{{ format }}", {{ leading_snprintf_val(p, ",") }} object_->{{ p["name"] }}(){{ getter_extra }});
if (nwritten <= 0) {
  break;
}
buffer += nwritten;
{% if not p["first_in_json"] and p["can_be_first_in_json"] %}
firstPropertyWritten_ = true;
{% endif %}
{%- endmacro %}

{%- macro string(NAME, p) -%}
if (!offset_) {
  static const char intro[] = "\"{{ p["name"] }}\":\"";
  static const std::size_t introSize = sizeof(intro) / sizeof(intro[0]);
  // Ensure that intro plus opening bracer (or comma) plus at least
  // one symbol of the string will fit into the buffer
  if (static_cast<std::size_t>(buffer_end - buffer) < introSize) {
    error_ = {{NAME}}_WRITER_BUFFER_TOO_SMALL;
    if (throwOnError) {
      throw std::runtime_error(errorMessage());
    }
    return npos;
  }
  {% if p["first_in_json"] %}
  *buffer++ = '{';
  {% elif p["can_be_first_in_json"] %}
  *buffer++ = {{ leading_snprintf_val(p) }};
  {% else %}
  *buffer++ = ',';
  {% endif %}
  (void) std::memcpy(buffer, intro, introSize);
  buffer += introSize;
}
std::size_t tocopy = std::min<std::size_t>(buffer_end - buffer, object_->{{ p["name"] }}().size() - offset_);
(void) std::memcpy(buffer, object_->{{ p["name"] }}().c_str() + offset_, tocopy);
offset_ += tocopy;
buffer += tocopy;
// Some string data haven't fit into the buffer
if (offset_ != object_->{{ p["name"] }}().size()) {
  break;
}
if (!(buffer_end - buffer)) {
  break;
}
*buffer++ = '\"';
offset_ = 0;
{% if not p["first_in_json"] and p["can_be_first_in_json"] %}
firstPropertyWritten_ = true;
{% endif %}
{%- endmacro -%}
