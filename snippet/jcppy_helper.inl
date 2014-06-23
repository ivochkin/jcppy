class JcppyHelper
{
public:
  template<class T> static void readDocument(T& obj, void* doc)
  {
    obj.readDocument(doc);
  }
};
