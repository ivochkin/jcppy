{{return_type}} {{class_name}}::{{name}}() const
{
  return {{name}}_;
}

void {{class_name}}::set{{Name}}({{argument_type}} value)
{
  {{name}}_ = value;
{% if optional %}
  has{{Name}}_ = true;
{% endif %}
}

{{storage_type}}* {{class_name}}::mutable{{Name}}()
{
  return &{{name}}_;
}

{% if optional %}
void {{class_name}}::reset{{Name}}()
{
  has{{Name}}_ = false;
}

bool {{class_name}}::has{{Name}}() const
{
  return has{{Name}}_;
}

{% endif %}

