{{Name}}Reader::{{Name}}Reader()
  : error_({{NAME}}_READER_OK)
{
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
}

int {{Name}}Reader::error() const
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



