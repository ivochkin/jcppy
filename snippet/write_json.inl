void %(class)s::writeJson(std::ostream& out) const
{
  ::OStreamWrapper sw(out);
  Writer writer(sw);
  writeJson(&writer);
}
