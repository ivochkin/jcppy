std::string %(class)s::json() const
{
  std::stringstream s;
  writeJson(s);
  return s.str();
}
