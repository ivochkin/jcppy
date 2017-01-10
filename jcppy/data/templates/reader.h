class {{Name}}Reader
{
public:
  explicit {{Name}}Reader(bool throwExceptionOnError);

  std::size_t read(std::istream& stream, std::size_t count);

  std::size_t read(const char* data, std::size_t size);

  template<class Iterator>
  Iterator read(Iterator begin, Iterator end);

  int error() const;

  {{Name}}& instance();
  {{Name}}* mutableInstance();

private:
  bool readByte(char value);

  {{Name}} instance_;
  bool throwExceptionOnError_;
};


