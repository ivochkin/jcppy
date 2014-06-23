#include <iostream>
#include <boost/uuid/uuid_generators.hpp>
#include <gtest/gtest.h>

#include <test/core.h>
#include <test/nested.h>
#include <test/nested_array.h>
#include <test/dog.h>
#include <test/plain_array.h>
#include <test/deeply_nested.h>


using jcppy::gen::Person;
using jcppy::gen::Outer;
using jcppy::gen::ShoppingList2;
using jcppy::gen::Dog;
using jcppy::gen::ShoppingList;
using jcppy::gen::Foo;


static boost::uuids::string_generator stringUuid;


TEST(Types, NotRequired)
{
  Person p;
  p.setName("Person X");
  EXPECT_TRUE(p.hasName());
  p.clearName();
  EXPECT_FALSE(p.hasName());
}

TEST(Types, Base64)
{
  Person p;
  p.clearPhoto();
  EXPECT_FALSE(p.hasPhoto());
  (void) p.mutablePhoto();
  EXPECT_TRUE(p.hasPhoto());
  p.clearPhoto();
  EXPECT_FALSE(p.hasPhoto());
  p.setPhoto(std::vector<char>{'f','\0', 'q'});
}

TEST(Types, DefaultDouble)
{
  Person p;
  p.setWealth(0);
  EXPECT_EQ(0, p.wealth());
  p.setWealth(p.defaultWealth());
  EXPECT_EQ(Person::defaultWealth(), p.wealth());
}

TEST(Types, StringMove)
{
  Person p;
  std::string newName = "Person X";
  p.setName(std::move(newName));
  EXPECT_EQ("", newName);
  EXPECT_EQ("Person X", p.name());
}

TEST(Types, Base64Move)
{
  Person p;
  std::vector<char> newPhoto = {'o', 'o', 'p', 's'};
  p.setPhoto(std::move(newPhoto));
  EXPECT_EQ(0, newPhoto.size());
  EXPECT_EQ(4, p.photo().size());
}

TEST(Types, RequiredHas)
{
  Person p;
  EXPECT_FALSE(p.hasGender());
  p.setGender(false);
  EXPECT_FALSE(p.gender());
  EXPECT_TRUE(p.hasGender());
  p.clearGender();
  EXPECT_FALSE(p.hasGender());
  EXPECT_THROW(p.gender(), std::runtime_error);
}

TEST(Core, Initialization)
{
  auto f = []() {
    Person p;
    EXPECT_FALSE(p.hasAge());
    p.setAge(2);
    EXPECT_TRUE(p.hasAge());
  };

  f();
  f();
}

TEST(Types, Object)
{
  Outer o;
  o.mutablePosition()->setX(0);
  o.mutablePosition()->setY(1);
  o.mutablePosition()->setZ(-1);
  EXPECT_EQ(0, o.position().x());
  EXPECT_EQ(1, o.position().y());
  EXPECT_EQ(-1, o.position().z());

  Outer::Position pos;
  pos.setX(10);
  pos.setY(5);
  o.setPosition(std::move(pos));
  EXPECT_EQ(10, o.position().x());
  EXPECT_FALSE(o.position().hasZ());
}

TEST(Types, Array)
{
  ShoppingList2 sl;
  sl.mutableItems()->push_back(ShoppingList2::Item{});
  sl.mutableItems()->begin()->mutableItemsPerWeek()->resize(10);
  EXPECT_TRUE(sl.hasItems());
  EXPECT_EQ(10, sl.items()[0].itemsPerWeek().size());
}

TEST(Core, Defaults)
{
  Dog dog;
  dog.setAge(dog.defaultAge());
  dog.setName(dog.defaultName());
  dog.setGender(dog.defaultGender());
  dog.setWeight(dog.defaultWeight());
  EXPECT_EQ(Dog::defaultAge(), dog.age());
  EXPECT_EQ(Dog::defaultName(), dog.name());
  EXPECT_EQ(Dog::defaultGender(), dog.gender());
  EXPECT_EQ(Dog::defaultWeight(), dog.weight());
}

TEST(ToJson, Smoke)
{
  Dog dog;
  dog.setAge(4);
  dog.setName("Goofy");
  dog.setGender(true);
  EXPECT_EQ("{\"gender\":true,\"age\":4,\"name\":\"Goofy\"}", dog.json());
}

TEST(ToJson, Nested)
{
  Outer o;
  o.mutablePosition()->setX(10);
  o.mutablePosition()->setY(-47);
  EXPECT_EQ("{\"position\":{\"y\":-47,\"x\":10}}", o.json());
}

TEST(ToJson, Array)
{
  ShoppingList sl;
  sl.mutableItems()->resize(5);
  sl.setId(stringUuid("e414200c-c648-4ea2-b31c-b81d38fe6ed1"));
  int c = 2;
  for (auto& i : *sl.mutableItems()) {
    i = c;
    c = c * c;
  }
  EXPECT_EQ("{\"items\":[2,4,16,256,65536],\"id\":\"e414200c-c648-4ea2-b31c-b81d38fe6ed1\"}", sl.json());
}

TEST(FromJson, Smoke)
{
  Dog dog;
  dog.fromJson("{\"name\" : \"Goofy\", \"age\":4,\"gender\": true}");
  EXPECT_EQ("Goofy", dog.name());
  EXPECT_EQ(4, dog.age());
  EXPECT_TRUE(dog.gender());
}

TEST(FromJson, Array)
{
  ShoppingList sl;
  sl.fromJson("{\"items\":[2,4,16,256,65536],\"id\":\"e414200c-c648-4ea2-b31c-b81d38fe6ed1\"}");
  EXPECT_EQ(5, sl.items().size());
  EXPECT_EQ(2, sl.items()[0]);
  EXPECT_EQ(4, sl.items()[1]);
  EXPECT_EQ(16, sl.items()[2]);
  EXPECT_EQ(256, sl.items()[3]);
  EXPECT_EQ(65536, sl.items()[4]);
  auto expectedId = stringUuid("e414200c-c648-4ea2-b31c-b81d38fe6ed1");
  EXPECT_EQ(expectedId, sl.id());
}

TEST(Core, Required)
{
  Person p;
  EXPECT_THROW(p.ensureInitialized(), std::runtime_error);
}

TEST(Core, RequiredToJson)
{
  Person p;
  p.setAge(40);
  p.setGender(true);
  // missing dateOfBirth
  EXPECT_THROW(p.json(), std::runtime_error);
}

TEST(Core, RequiredFromJson)
{
  Person p;
  EXPECT_THROW(p.fromJson("{\"age\":40, \"gender\":false}"), std::runtime_error);
}

TEST(Core, Constructors)
{
  Dog dog("{\"name\" : \"Goofy\", \"age\":4,\"gender\": true}");
  EXPECT_EQ("Goofy", dog.name());
  EXPECT_EQ(4, dog.age());
  EXPECT_TRUE(dog.gender());
}

TEST(ToJson, Base64Padding1)
{
  Person p;
  p.setAge(1);
  p.setGender(true);
  p.setDateOfBirth(boost::posix_time::ptime(boost::gregorian::date(2000, 4, 4)));
  p.setPhoto(std::vector<char>{'h', 'e', 'l', 'l', 'o'});
  EXPECT_EQ("{\"gender\":true,\"age\":1,\"dateOfBirth\":\"2000-04-04T00:00:00\",\"photo\":\"aGVsbG8=\"}", p.json());
}

TEST(ToJson, Base64Padding2)
{
  Person p;
  p.setAge(1);
  p.setGender(true);
  p.setDateOfBirth(boost::posix_time::ptime(boost::gregorian::date(2000, 4, 4)));
  p.setPhoto(std::vector<char>{'c', 'h', 'e', 'e', 's', 'e', 'e'});
  EXPECT_EQ("{\"gender\":true,\"age\":1,\"dateOfBirth\":\"2000-04-04T00:00:00\",\"photo\":\"Y2hlZXNlZQ==\"}", p.json());
}

TEST(ToJson, Base64NoPadding)
{
  Person p;
  p.setAge(1);
  p.setGender(true);
  p.setDateOfBirth(boost::posix_time::ptime(boost::gregorian::date(2000, 4, 4)));
  p.setPhoto(std::vector<char>{'c', 'h', 'e', 'e', 's', 'e'});
  EXPECT_EQ("{\"gender\":true,\"age\":1,\"dateOfBirth\":\"2000-04-04T00:00:00\",\"photo\":\"Y2hlZXNl\"}", p.json());
}

TEST(Core, PopulateDefaultsPlain)
{
  Person p;
  EXPECT_TRUE(p.populateDefaults());
  EXPECT_TRUE(p.married());
  EXPECT_DOUBLE_EQ(1000000.2, p.wealth());
}

TEST(Core, PopulateDefaultsNoop)
{
  Foo foo;
  EXPECT_FALSE(foo.populateDefaults());
}

TEST(Core, PopulateDefaultsNested)
{
  Outer out;
  EXPECT_TRUE(out.populateDefaults());
  EXPECT_DOUBLE_EQ(-1, out.position().z());
  EXPECT_FALSE(out.position().hasX());
  EXPECT_FALSE(out.position().hasY());
}
