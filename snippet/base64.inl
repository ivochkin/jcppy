std::string base64(const std::vector<char>& buf)
{
  if (!buf.size()) {
    return "";
  }
  static const char alpha[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  std::stringstream res;
  for (std::size_t i = 0, groups = buf.size() / 3; i < groups; ++i) {
    res << alpha[(buf[3 * i] & 0xFC) >> 2]
      << alpha[((buf[3 * i] & 0x03) << 4) | (buf[3 * i + 1] >> 4)]
      << alpha[((buf[3 * i + 1] & 0x0F) << 2) | (buf[3 * i + 2] >> 6)]
      << alpha[(buf[3 * i + 2] & 0x3F)];
  }
  auto tail = 3 * (buf.size() / 3);
  auto remain = buf.size() % 3;
  if (remain == 1) {
    res << alpha[(buf[tail] & 0xFC) >> 2]
      << alpha[((buf[tail] & 0x03) << 4)]
      << "==";
  } else if (remain == 2) {
    res << alpha[(buf[tail] & 0xFC) >> 2]
      << alpha[((buf[tail] & 0x03) << 4) | (buf[tail + 1] >> 4)]
      << alpha[((buf[tail + 1] & 0x0F) << 2)]
      << '=';
  }
  return res.str();
}
