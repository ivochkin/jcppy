class IStreamWrapper
{
public:
  explicit IStreamWrapper(std::istream& is)
    : is_(is)
    , count_(0)
  {
    read();
  }

  char Peek() const { return current_; }
  char Take() { char c = current_; read(); return c; }
  int Tell() const { return count_; }

  // methods needed by destructive json parser
  IStreamWrapper& operator=(const IStreamWrapper& other)
  {
    current_ = other.current_;
    count_ = other.count_;
    return *this;
  }

  void Put(char) { assert(false); }
  char* PutBegin() { assert(false); return nullptr; }
  size_t PutEnd(char*) { assert(false); return 0; }

private:
  void read()
  {
    is_.get(current_);
    if (is_.good()) {
      ++count_;
    } else {
      current_ = '\0';
    }
  }

  std::istream& is_;
  char current_;
  size_t count_;
};
