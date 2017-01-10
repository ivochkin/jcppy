template<class Iterator>
Iterator {{Name}}Writer::write(Iterator output)
{
  while (output) {
    writeByte(*output);
    output++;
  }
  return output;
}


