class {{Name}}Writer
{
public:
  explicit {{Name}}Writer({{Name}}* object);

  std::ostream& write(std::ostream& stream, std::size_t count = -1);
  std::size_t write(char* buffer, std::size_t count);

  template<class Iterator>
  Iterator write(Iterator output);

  std::size_t bufferSizeHint() const;
  int error() const;

private:
  bool writeByte(char* buffer);

  {{Name}}* object_;
  int error_;
};


