void %(class)s::readJson(std::istream& is)
{
  Document doc;
  ::IStreamWrapper s(is);
  doc.ParseStream<0>(s);
  if (doc.HasParseError()) {
    std::stringstream errMessage;
    errMessage << "Can not parse json for object %(class)s . Error at offset "
      << doc.GetErrorOffset() << " : " << GetParseError_En(doc.GetParseError());
    JCPPY_THROW(std::runtime_error(errMessage.str()));
  }
  readDocument(&doc);
}
