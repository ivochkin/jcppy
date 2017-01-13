template<class Iterator>
Iterator {{Name}}Reader::read(Iterator begin, Iterator end, bool throwOnError)
{
  Iterator i = begin;
  for (; i != end; ++i) {
    readByte(*i);
    if (error_) {
      if (throwOnError) {
        throw std::runtime_error(errorMessage());
      }
      return i;
    }
  }
  return i;
}


