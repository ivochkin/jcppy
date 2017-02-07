template<class Iterator>
{{Name}} {{Name}}::fromJson(Iterator begin, Iterator end)
{
  {{Name}}Reader reader;
  reader.read(begin, end);
  return reader.instance();
};

template<class Iterable>
{{Name}} {{Name}}::fromJson(const Iterable& iterable)
{
  return fromJson(iterable.begin(), iterable.end());
}


