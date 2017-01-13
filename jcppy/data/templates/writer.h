class {{Name}}Writer
{
public:
  explicit {{Name}}Writer(const {{Name}}* object);

  enum Error
  {
    {{NAME}}_WRITER_OK,
    {{NAME}}_WRITER_UNEXPECTED_ERROR,
    {{NAME}}_WRITER_BUFFER_TOO_SMALL,
  };

  static const std::size_t npos;

  std::size_t write(char* buffer, std::size_t count, bool throwOnError = true);

  template<class Iterator>
  Iterator write(Iterator output, bool throwOnError = true);

  std::size_t bufferSizeHint() const;
  int error() const;
  const char* errorMessage() const;

private:
  const {{Name}}* object_;
  int error_;
{% if nproperties %}
  std::size_t nextProperty_;
  bool firstPropertyWritten_;
  std::size_t offset_;
{% endif %}
};


