template<class Iterator>
{{Name}} {{Name}}::fromJson(Iterator begin, Iterator end)
{
  {{Name}}Reader reader(true);
  reader.read(begin, end);
  reader.ensureDone();
  return reader.instance();
};

template<class Container>
{{Name}} {{Name}}::fromJson(const Container& container)
{
  return fromJson(container.begin(), container.end());
}


