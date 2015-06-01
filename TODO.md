* jcppy_generate target should depend on snippets
* use env.variable instead of env['variable']
* add doxygen comments to generated fields
* remove rapidjson dependency - embed json parsing
* change cmake install to setup.py
* implement no-copy constructor:
  template<class T>
  %(class)s::%(class)s(const T& stringlike)
    : %(class)s()
  {
    fromJson(stringlike.data(), stringlike.size());
  }
