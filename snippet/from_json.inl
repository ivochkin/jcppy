void %(class)s::fromJson(const std::string& jsonObject)
{
  std::stringstream s(jsonObject);
  s >> std::noskipws;
  readJson(s);
}
