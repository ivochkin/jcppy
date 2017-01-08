{{Name}}Reader::{{Name}}Reader()
{
}

void {{Name}}Reader::read(std::istream& stream, std::size_t count)
{
}

void {{Name}}Reader::read(const char* data, std::size_t size)
{
}

bool {{Name}}Reader::done() const
{
  return done_;
}

void {{Name}}Reader::ensureDone() const
{
  if (!done()) {
    throw std::runtime_error("Parsing failed");
  }
}

{{Name}}& {{Name}}Reader::instance()
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
