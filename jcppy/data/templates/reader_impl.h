template<class Iterator>
Iterator {{Name}}Reader::read(Iterator begin, Iterator end)
{
  while (begin != end) {
    if (!readByte(*begin)) {
      break;
    }
    ++begin;
  }
  return begin;
}


