struct OStreamWrapper
{
  explicit OStreamWrapper(std::ostream& os) : os_(os) {}
  void Put(char c) { os_.put(c); }
  void Flush() { os_.flush(); }
  std::ostream& os_;
};
