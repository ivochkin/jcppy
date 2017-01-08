class {{Name}}Reader
{
public:
  {{Name}}Reader();

  void read(std::istream& stream, std::size_t count);

  void read(const char* data, std::size_t size);

  template<class Iterator>
  void read(Iterator begin, Iterator end)
  {
    while (begin != end) {
      readByte(*begin);
      ++begin;
    }
  }

  bool done() const;
  void ensureDone() const;

  {{Name}}& instance();
  {{Name}}* mutableInstance();

private:
  void readByte(char value);

  {{Name}} instance_;
  bool done_;
};


