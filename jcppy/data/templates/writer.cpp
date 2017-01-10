{{Name}}Writer::{{Name}}Writer({{Name}}* object)
  : object_(object)
{
}

std::ostream& {{Name}}Writer::writer(std::ostream& stream, std::size_t count)
{
  return stream;
}

std::size_t {{Name}}Writer::write(char* buffer, std::size_t count)
{
  return 0;
}

std::size_t {{Name}}Writer::bufferSizeHint() const
{
  return 4096;
}

int {{Name}}::error() const
{
  return error_;
}

bool {{Name}}::writeByte(char* buffer)
{
  return false;
}


