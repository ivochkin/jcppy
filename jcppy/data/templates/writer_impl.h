template<class Iterator>
Iterator {{Name}}Writer::write(Iterator output, bool throwOnError)
{
  std::size_t nwritten;
  do {
    std::vector<char> buffer(bufferSizeHint());
    nwritten = write(&buffer[0], buffer.size(), throwOnError);
    if (nwritten == {{Name}}Writer::npos) {
      return output;
    }
    std::copy(buffer.begin(), buffer.begin() + nwritten, output);
  } while (nwritten);
  return output;
}


