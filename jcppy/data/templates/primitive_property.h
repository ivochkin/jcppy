  {{return_type}} {{name}}() const;
  void set{{Name}}({{argument_type}} value);
  {{storage_type}}* mutable{{Name}}();
{% if optional %}
  void reset{{Name}}();
  bool has{{Name}}() const;
{% endif %}


