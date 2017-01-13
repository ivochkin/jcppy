/**
 * An object that holds {{Name}} parsing state.
 *
 * Reader can be used for iterative parsing, e.g. when data arrives from the
 * network as a series of length-limited buffers.
 *
 * If any of read() functions succeds and consumes less bytes than it have been
 * provided with, {{Name}} object is * considered parsed and could be accessed
 * via getters
 * - instance()
 * - mutableInstance()
 */
class {{Name}}Reader
{
public:
  {{Name}}Reader();

  enum Error
  {
    {{NAME}}_READER_OK,
    {{NAME}}_READER_PARSE_ERROR,
    {{NAME}}_READER_IO_ERROR
  };

  /**
   * Read upto count bytes from stream.
   *
   * @returns Number of bytes actually read, -1 if read operation or data
   * parsing failed.
   *
   * @see error(), throwIfError()
   */
  std::size_t read(std::istream& stream, std::size_t count,
      bool throwOnError = true);

  /**
   * Read upto count bytes from the buffer buf
   *
   * @returns Number of bytes actually read, -1 if read operation failed
   *
   * @see error(), throwIfError()
   */
  std::size_t read(const char* buf, std::size_t count,
      bool throwOnError = true);

  /**
   * Read char sequence from the [begin; end) range.
   *
   * @returns Iterator to the element next to the last successfully read one.
   */
  template<class Iterator>
  Iterator read(Iterator begin, Iterator end, bool throwOnError = true);

  /**
   * Returns non-zero error code if the last read operation failed. Otherwise
   * returns 0.
   */
  int error() const;

  /**
   * Returns a string representation of the code returned by the error() methd.
   */
  const char* errorMessage() const;

  const {{Name}}& instance() const;
  {{Name}}* mutableInstance();

private:
  void readByte(char value);

  {{Name}} instance_;
  int error_;
};


