#include <vector>

#include <gtest/gtest.h>

#define JCPPY_THROW(x) throw x

namespace {

#include <snippet/from_base64.inl>

} // anonymous namespace


TEST(ParseBase64, Smoke)
{
  const char data[] = "Zm9vCg==";
  auto res = ::fromBase64(data, sizeof(data) - 1);
  EXPECT_EQ('f', res[0]);
  EXPECT_EQ('o', res[1]);
  EXPECT_EQ('o', res[2]);
  EXPECT_EQ('\n', res[3]);
}

TEST(ParseBase64, NoPadding)
{
  const char data[] = "aGVsbG8K";
  auto res = ::fromBase64(data, sizeof(data) - 1);
  EXPECT_EQ('h', res[0]);
  EXPECT_EQ('e', res[1]);
  EXPECT_EQ('l', res[2]);
  EXPECT_EQ('l', res[3]);
  EXPECT_EQ('o', res[4]);
  EXPECT_EQ('\n', res[5]);
}
