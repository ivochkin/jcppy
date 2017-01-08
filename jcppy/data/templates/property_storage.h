{% if description %}
/*
{{description}}
*/
{% endif %}
  {{storage_type}} {{name}}_;
{% if optional %}
  bool has{{Name}}_;
{% endif %}

